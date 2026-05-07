from __future__ import annotations

import os
from typing import Any


SYSTEM_PROMPT = """You are a careful Muslim emotional-support assistant.
Use only the provided retrieved Quran, hadith, and Seerah items.
Do not invent references, rulings, hadith grades, or unseen facts.
Do not diagnose mental health conditions.
Keep the tone compassionate, concise, and grounded."""


def _format_context(items: list[dict[str, Any]]) -> str:
    blocks = []
    for item in items:
        blocks.append(
            f"- {item['type'].title()} | {item['reference']} | {item['authenticity']}: "
            f"{item['english_text']} Reflection: {item['reflection_note']}"
        )
    return "\n".join(blocks)


def local_reflection(themes: list[str], items: list[dict[str, Any]], crisis: bool = False) -> str:
    theme_text = ", ".join(themes[:4])
    first_reference = items[0]["reference"] if items else "the selected reminders"
    prefix = (
        "I am really sorry this feels so heavy right now. "
        if crisis
        else "Thank you for trusting this space with what you are carrying. "
    )
    return (
        f"{prefix}Your words seem connected to {theme_text}. "
        f"A fitting place to begin is {first_reference}; read the reminders below slowly, "
        "and let them point you back to Allah's mercy without pressuring yourself to feel better instantly."
    )


def generate_grounded_reflection(
    user_text: str,
    themes: list[str],
    items: list[dict[str, Any]],
    crisis: bool = False,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return local_reflection(themes, items, crisis)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"User feeling: {user_text}\n"
                        f"Detected themes: {', '.join(themes)}\n"
                        f"Crisis flag: {crisis}\n"
                        f"Retrieved items:\n{_format_context(items)}\n\n"
                        "Write 3-5 sentences of gentle support. Mention references only from the retrieved items."
                    ),
                },
            ],
            temperature=0.35,
            max_tokens=220,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return local_reflection(themes, items, crisis)
