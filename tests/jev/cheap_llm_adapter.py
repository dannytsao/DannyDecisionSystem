#!/usr/bin/env python3
"""Executable, provider-neutral Cheap LLM adapter for shadow validation.

The adapter accepts sanitized DDS decision inputs over JSONL and emits one
decision row per input. A configured command provider is preferred; an
OpenAI-compatible HTTP endpoint is supported when all required environment
variables are present. Missing configuration abstains without inventing a
decision, price, or provider measurement.
"""

import json
import os
import shlex
import subprocess
import sys
import time
from typing import Any, Dict, Optional, Protocol
from urllib import error as urllib_error
from urllib import request as urllib_request


INPUT_FIELDS = ("id", "gate", "state", "options", "policy_facts")
DEFAULT_TIMEOUT_SECONDS = 30.0


class Provider(Protocol):
    name: str

    def complete(self, request: Dict[str, Any]) -> Dict[str, Any]:
        ...

def build_request(case: Dict[str, Any]) -> Dict[str, Any]:
    return {key: case[key] for key in INPUT_FIELDS if key in case}


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def cost_from_usage(
    usage: Dict[str, Any],
    input_rate_usd_per_million: Optional[float],
    output_rate_usd_per_million: Optional[float],
) -> Optional[float]:
    if input_rate_usd_per_million is None or output_rate_usd_per_million is None:
        return None
    prompt_tokens = _number(usage.get("prompt_tokens"))
    completion_tokens = _number(usage.get("completion_tokens"))
    if prompt_tokens is None or completion_tokens is None:
        return None
    if prompt_tokens < 0 or completion_tokens < 0:
        return None
    return (
        prompt_tokens * input_rate_usd_per_million
        + completion_tokens * output_rate_usd_per_million
    ) / 1_000_000


def _env_rate(name: str) -> Optional[float]:
    value = os.getenv(name)
    if not value:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _extract_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, str):
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
            if isinstance(content, dict):
                return content
    return payload


class UnconfiguredProvider:
    name = "unconfigured"

    def complete(self, request: Dict[str, Any]) -> Dict[str, Any]:
        del request
        return {}


class CommandProvider:
    def __init__(self, command: str, timeout_seconds: float) -> None:
        self.name = "command"
        self._command = command
        self._timeout_seconds = timeout_seconds

    def complete(self, request: Dict[str, Any]) -> Dict[str, Any]:
        run = subprocess.run(
            shlex.split(self._command),
            input=json.dumps(request, ensure_ascii=False) + "\n",
            text=True,
            capture_output=True,
            timeout=self._timeout_seconds,
            check=True,
        )
        lines = [line for line in run.stdout.splitlines() if line.strip()]
        if len(lines) != 1:
            raise ValueError("provider returned an invalid JSONL response")
        payload = json.loads(lines[0])
        if not isinstance(payload, dict):
            raise ValueError("provider returned a non-object response")
        return payload


class OpenAICompatibleProvider:
    def __init__(self, url: str, api_key: str, model: str, timeout_seconds: float) -> None:
        self.name = "openai-compatible"
        self._url = url
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def complete(self, request: Dict[str, Any]) -> Dict[str, Any]:
        body = {
            "model": self._model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "Return a JSON object with decision and optional confidence. Use only the supplied options.",
                },
                {"role": "user", "content": json.dumps(request, ensure_ascii=False)},
            ],
        }
        http_request = urllib_request.Request(
            self._url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib_request.urlopen(http_request, timeout=self._timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("provider returned a non-object response")
        return _extract_response(payload) | {
            "usage": payload.get("usage"),
        }


def provider_from_env() -> Provider:
    command = os.getenv("CHEAP_LLM_PROVIDER_CMD")
    timeout = _env_rate("CHEAP_LLM_TIMEOUT_SECONDS") or DEFAULT_TIMEOUT_SECONDS
    if command:
        return CommandProvider(command, timeout)
    url = os.getenv("CHEAP_LLM_API_URL")
    api_key = os.getenv("CHEAP_LLM_API_KEY")
    model = os.getenv("CHEAP_LLM_MODEL")
    if url and api_key and model:
        return OpenAICompatibleProvider(url, api_key, model, timeout)
    return UnconfiguredProvider()


def unconfigured_result(case: Dict[str, Any]) -> Dict[str, Any]:
    del case
    return {
        "decision": None,
        "confidence": None,
        "provider": "unconfigured",
        "provider_error": None,
        "latency_ms": 0.0,
        "llm_calls": 0,
        "tool_calls": 0,
        "search_calls": 0,
        "retries": 0,
        "pipeline_steps": 0,
        "context_tokens": None,
        "cost_usd": None,
    }


def decide(case: Dict[str, Any], provider: Optional[Provider] = None) -> Dict[str, Any]:
    selected = provider or provider_from_env()
    if isinstance(selected, UnconfiguredProvider):
        return unconfigured_result(case)
    request = build_request(case)
    started = time.perf_counter()
    try:
        payload = selected.complete(request)
    except (OSError, ValueError, subprocess.SubprocessError, TimeoutError, urllib_error.URLError):
        return {
            **unconfigured_result(case),
            "provider": selected.name,
            "provider_error": "provider_request_failed",
            "llm_calls": 1,
            "pipeline_steps": 1,
            "latency_ms": (time.perf_counter() - started) * 1000,
        }
    decision = payload.get("decision")
    if decision not in case.get("options", []):
        decision = None
        provider_error = "invalid_decision"
    else:
        provider_error = None
    confidence = _number(payload.get("confidence"))
    usage = payload.get("usage")
    usage_dict = usage if isinstance(usage, dict) else {}
    context_tokens = _number(usage_dict.get("prompt_tokens"))
    return {
        "decision": decision,
        "confidence": confidence,
        "provider": selected.name,
        "provider_error": provider_error,
        "latency_ms": (time.perf_counter() - started) * 1000,
        "llm_calls": 1,
        "tool_calls": 0,
        "search_calls": 0,
        "retries": 0,
        "pipeline_steps": 1,
        "context_tokens": context_tokens,
        "cost_usd": cost_from_usage(
            usage_dict,
            _env_rate("CHEAP_LLM_INPUT_USD_PER_MILLION"),
            _env_rate("CHEAP_LLM_OUTPUT_USD_PER_MILLION"),
        ),
    }


def main() -> int:
    provider = provider_from_env()
    for line in sys.stdin:
        if line.strip():
            case = json.loads(line)
            print(json.dumps(decide(case, provider), ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
