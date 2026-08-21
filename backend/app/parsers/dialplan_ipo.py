"""Парсер IPO shortcodes CSV → dialplan_entries (source=ipo_shortcode)."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IpoShortcodeRow:
    """Одна строка short code IPO."""

    match_prefix: str
    telephone_number: str | None
    feature: str | None
    line_group: str | None
    raw: str


_WILDCARD_TRAIL = re.compile(r"[NXnZx.z]+$")


def _prefix_from_short_code(short_code: str) -> str:
    """9N → 9, 12XX → 12, *17 → *17 (хвостовые wildcard убираем для longest-prefix)."""
    text = short_code.strip()
    cleaned = _WILDCARD_TRAIL.sub("", text)
    return cleaned or text


def parse_ipo_shortcodes_csv(text: str) -> list[IpoShortcodeRow]:
    """Разбор CSV Short Code,Telephone Number,Feature,Line Group."""
    reader = csv.DictReader(io.StringIO(text.strip()))
    rows: list[IpoShortcodeRow] = []
    if not reader.fieldnames:
        return rows
    # Нормализуем имена колонок
    field_map = {name.lower().strip(): name for name in reader.fieldnames}

    def col(*aliases: str) -> str | None:
        for alias in aliases:
            key = field_map.get(alias.lower())
            if key:
                return key
        return None

    sc_key = col("short code", "shortcode", "code")
    tn_key = col("telephone number", "telephone", "number")
    feat_key = col("feature")
    lg_key = col("line group", "linegroup", "group")

    for record in reader:
        short = (record.get(sc_key) or "").strip() if sc_key else ""
        if not short:
            continue
        telephone = (record.get(tn_key) or "").strip() if tn_key else ""
        feature = (record.get(feat_key) or "").strip() if feat_key else ""
        line_group = (record.get(lg_key) or "").strip() if lg_key else ""
        raw = ",".join(
            [
                short,
                telephone,
                feature,
                line_group,
            ]
        )
        rows.append(
            IpoShortcodeRow(
                match_prefix=_prefix_from_short_code(short),
                telephone_number=telephone or None,
                feature=feature or None,
                line_group=line_group or None,
                raw=raw,
            )
        )
    return rows
