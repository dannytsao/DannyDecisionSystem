# ruff: noqa: INP001, CPY001

"""Parse the small FITS header subset needed by the intake gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path  # noqa: TC003 - Path is also used at runtime

FITS_SUFFIXES = frozenset({".fit", ".fits", ".fts"})
HEADER_BLOCK_BYTES = 2880
CARD_BYTES = 80


@dataclass(frozen=True)
class FitsHeaderError(Exception):
    """Report a FITS header that cannot be safely interpreted."""

    path: Path
    reason: str

    def __str__(self) -> str:
        """Return a concise parse failure for the manifest report."""
        return f"invalid FITS header {self.path}: {self.reason}"


@dataclass(frozen=True)
class FitsMetadata:
    """Stable image metadata required before a processing recipe is approved."""

    width: int
    height: int
    bitpix: int
    bayerpat: str | None
    filter_name: str | None


def is_fits(path: Path) -> bool:
    """Return whether the path uses a supported FITS suffix."""
    return path.suffix.lower() in FITS_SUFFIXES


def _read_cards(path: Path) -> tuple[bytes, ...]:
    cards: list[bytes] = []
    with path.open("rb") as source:
        while True:
            block = source.read(HEADER_BLOCK_BYTES)
            if len(block) != HEADER_BLOCK_BYTES:
                raise FitsHeaderError(path, "header is shorter than a FITS block")
            cards.extend(
                block[offset : offset + CARD_BYTES]
                for offset in range(0, HEADER_BLOCK_BYTES, CARD_BYTES)
            )
            if any(card[:8].rstrip() == b"END" for card in cards[-36:]):
                return tuple(cards)


def _card_values(cards: tuple[bytes, ...], path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for card in cards:
        try:
            keyword = card[:8].decode("ascii").strip()
            body = card[10:].decode("ascii")
        except UnicodeDecodeError as error:
            raise FitsHeaderError(path, "header contains non-ASCII cards") from error
        if keyword == "END":
            break
        if card[8:10] != b"= ":
            continue
        value = body.split("/", 1)[0].strip()
        if value.startswith("'") and "'" in value[1:]:
            value = value[1 : value.index("'", 1)].strip()
        values[keyword] = value
    return values


def _required_int(values: dict[str, str], key: str, path: Path) -> int:
    raw = values.get(key)
    if raw is None:
        raise FitsHeaderError(path, f"missing {key}")
    try:
        return int(raw)
    except ValueError as error:
        raise FitsHeaderError(path, f"{key} is not an integer") from error


def read_fits_metadata(path: Path) -> FitsMetadata:
    """Parse required primary-image metadata from a FITS file."""
    values = _card_values(_read_cards(path), path)
    if values.get("SIMPLE") != "T":
        raise FitsHeaderError(path, "SIMPLE is not T")
    width = _required_int(values, "NAXIS1", path)
    height = _required_int(values, "NAXIS2", path)
    bitpix = _required_int(values, "BITPIX", path)
    if width <= 0 or height <= 0:
        raise FitsHeaderError(path, "image dimensions must be positive")
    return FitsMetadata(
        width=width,
        height=height,
        bitpix=bitpix,
        bayerpat=values.get("BAYERPAT") or None,
        filter_name=values.get("FILTER") or None,
    )
