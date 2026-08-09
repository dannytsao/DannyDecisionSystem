# DDS Runtime and Interface Architecture

Status: Accepted foundation

## Decision

DDS is an **AI Decision & Execution Platform**.

The DDS Runtime is the permanent core. User interfaces, knowledge systems, LLMs and external tools are replaceable adapters.

> Build the Runtime once. Connect multiple interfaces.

## Core boundary

The Runtime owns:

- decision;
- planning;
- execution;
- memory and state;
- skill orchestration;
- evidence, risk and checkpoint handling.

The Runtime does not depend on LINE, ChatGPT, Claude, Obsidian, GitHub or any single model or product.

## Adapter boundary

```text
User
  |
  +-- LINE / Chat / Web / Voice
          |
     Interface Adapter
          |
       DDS Runtime
          |
  +-------+--------+--------+
  |                |        |
Knowledge       LLM       Tool
Adapters        Adapters  Adapters
```

### Interface adapters

LINE Bot is the preferred Phase-1 daily interface. Chat is the bootstrap UI, not the final UI. Future interfaces may include Web Dashboard, desktop, mobile and voice.

### Knowledge adapters

Obsidian, Markdown, GitHub, Google Drive, databases and future stores are sources or destinations. None is DDS itself.

### LLM adapters

Codex, Claude Code, Kimi, Hermes, OpenAI models and future models may participate. No model owns the architecture or the source of truth.

### Tool adapters

GitHub, n8n, Render, MCP services, calendars and other execution systems remain replaceable integrations.

## Evolution

1. Chat and LINE as bootstrap interfaces.
2. LINE for commands and notifications; Web Dashboard for status, approvals and history.
3. Multiple interfaces connected to the same Runtime.

## Invariants

- DDS must never depend on one UI, model or knowledge tool.
- DDS must always support conversational interaction.
- Repository decisions and accepted records are the source of truth.
- Adapters may change without rewriting the Runtime contract.
