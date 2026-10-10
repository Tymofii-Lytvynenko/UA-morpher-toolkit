"""Clipboard and batch operations independent of the graphical toolkit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


CASE_NAMES: dict[str, str] = {
    "nomn": "Називний",
    "gent": "Родовий",
    "datv": "Давальний",
    "accs": "Знахідний",
    "ablt": "Орудний",
    "loct": "Місцевий",
    "voct": "Кличний",
}


@dataclass(frozen=True)
class InflectionRow:
    original: str
    result: str
    error: str | None = None


def parse_clipboard(text: str) -> list[str]:
    """Parse Excel TSV or a newline-separated list into ordered full names.

    Supports a single full-name column or 2/3 adjacent name columns.
    Blank rows inside the selected range are deliberately preserved.
    The extra empty row caused by the final newline is not a data row.
    """
    if not text:
        return []

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines[-1] == "":
        lines.pop()

    rows: list[str] = []
    for line in lines:
        cells = line.split("\t")
        if len(cells) == 1:
            rows.append(cells[0].strip())
        else:
            # Columns from Excel: surname, first name, patronymic.
            # Ignore any columns past the first three.
            rows.append(" ".join(cell.strip() for cell in cells[:3] if cell.strip()))
    return rows


def inflect_rows(
    names: Sequence[str],
    case: str,
    morph_name: Callable[..., str],
    *,
    uppercase_surname: bool = False,
) -> list[InflectionRow]:
    """Inflect each entry without reordering or dropping failed/blank rows.

    The callable is injected so this module stays usable without Qt/pymorphy3.
    """
    if case not in CASE_NAMES:
        raise ValueError(f"Невідомий відмінок: {case}")

    results = []
    for original in names:
        if not original.strip():
            results.append(InflectionRow(original, ""))
            continue
        try:
            value = morph_name(original, case, uppercase_surname=uppercase_surname)
            results.append(InflectionRow(original, value))
        except Exception as exc:
            # Keep original text visible/copyable to avoid losing a record.
            results.append(InflectionRow(original, original, str(exc)))
    return results


def results_to_clipboard(rows: Sequence[InflectionRow]) -> str:
    """Return one output cell per row in the same order as the input."""
    return "\n".join(row.result for row in rows)
