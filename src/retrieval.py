from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


CONTENT_TYPES = ("quran", "hadith", "seerah")

THEME_ALIASES: dict[str, set[str]] = {
    "anxious": {"anxious", "anxiety", "panic", "worried", "worry", "nervous", "restless", "stress", "stressed"},
    "exhausted": {"exhausted", "tired", "burnout", "burned", "drained", "fatigue", "weary", "overwhelmed"},
    "sad": {"sad", "sadness", "depressed", "down", "low", "heartbroken", "crying", "grief", "loss"},
    "lonely": {"lonely", "alone", "abandoned", "isolated", "forgotten"},
    "happy": {"happy", "joy", "joyful", "excited", "relieved", "content", "grateful", "blessed"},
    "guilt": {"guilt", "guilty", "shame", "ashamed", "sin", "mistake", "repent", "repentance"},
    "fear": {"fear", "afraid", "scared", "unsafe", "danger", "uncertain"},
    "anger": {"angry", "anger", "frustrated", "rage", "resentful", "irritated"},
    "hope": {"hope", "hopeful", "mercy", "relief", "ease", "trust", "tawakkul"},
}

CRISIS_TERMS = {
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "self-harm",
    "harm myself",
    "want to die",
    "can't go on",
    "cannot go on",
}


def load_content(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        items = json.load(handle)
    validate_content(items)
    return items


def validate_content(items: list[dict[str, Any]]) -> None:
    required = {"id", "type", "themes", "english_text", "reflection_note", "reference", "authenticity", "source_url"}
    for item in items:
        missing = required - item.keys()
        if missing:
            raise ValueError(f"{item.get('id', 'unknown item')} is missing: {', '.join(sorted(missing))}")
        if item["type"] not in CONTENT_TYPES:
            raise ValueError(f"{item['id']} has unsupported type: {item['type']}")
        if item["type"] == "quran" and not re.search(r"Quran\s+\d+:\d+", item["reference"]):
            raise ValueError(f"{item['id']} needs a Quran surah:ayah reference")
        if item["type"] == "hadith" and item["authenticity"].lower() not in {"sahih", "hasan"}:
            raise ValueError(f"{item['id']} must be authentic or hasan for v1")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']{2,}", normalize_text(text))


def detect_crisis(text: str) -> bool:
    normalized = normalize_text(text)
    return any(term in normalized for term in CRISIS_TERMS)


def infer_themes(text: str, selected: list[str] | None = None) -> list[str]:
    tokens = set(tokenize(text))
    normalized = normalize_text(text)
    themes: list[str] = []

    for theme, aliases in THEME_ALIASES.items():
        if tokens.intersection(aliases) or any(alias in normalized for alias in aliases if " " in alias):
            themes.append(theme)

    for chip in selected or []:
        chip_theme = normalize_text(chip)
        if chip_theme and chip_theme not in themes:
            themes.append(chip_theme)

    return themes or ["hope"]


def _score_item(item: dict[str, Any], query_tokens: Counter[str], themes: list[str]) -> float:
    item_terms = Counter(tokenize(" ".join([
        item.get("english_text", ""),
        item.get("reflection_note", ""),
        " ".join(item.get("themes", [])),
        item.get("reference", ""),
    ])))
    theme_overlap = set(themes).intersection(item.get("themes", []))
    lexical = sum(min(count, item_terms.get(term, 0)) for term, count in query_tokens.items())
    length_norm = math.sqrt(sum(item_terms.values())) or 1.0
    type_bonus = {"quran": 0.25, "hadith": 0.15, "seerah": 0.0}.get(item["type"], 0.0)
    return (2.2 * len(theme_overlap)) + (lexical / length_norm) + type_bonus


def retrieve_content(
    text: str,
    items: list[dict[str, Any]],
    selected_themes: list[str] | None = None,
    per_type: int = 2,
) -> tuple[list[str], list[dict[str, Any]]]:
    themes = infer_themes(text, selected_themes)
    query_tokens = Counter(tokenize(" ".join([text, *themes])))

    ranked = sorted(
        ({**item, "score": _score_item(item, query_tokens, themes)} for item in items),
        key=lambda item: item["score"],
        reverse=True,
    )

    chosen: list[dict[str, Any]] = []
    for content_type in CONTENT_TYPES:
        typed = [item for item in ranked if item["type"] == content_type and item["score"] > 0]
        chosen.extend(typed[:per_type])

    if not chosen:
        chosen = ranked[:3]

    return themes, chosen
