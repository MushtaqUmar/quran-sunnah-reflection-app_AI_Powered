from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ai import generate_grounded_reflection
from src.retrieval import detect_crisis, load_content, retrieve_content


def main() -> None:
    items = load_content(ROOT / "data" / "content_seed.json")
    scenarios = [
        "I feel anxious about the future.",
        "I feel happy and grateful today.",
        "I feel guilty and ashamed.",
        "I want to die.",
    ]

    for scenario in scenarios:
        themes, results = retrieve_content(scenario, items, [], per_type=1)
        assert results, scenario
        assert any(item["type"] == "quran" for item in results), scenario
        assert all(item["reference"] for item in results), scenario
        assert all(item["authenticity"] for item in results), scenario
        reflection = generate_grounded_reflection(scenario, themes, results, detect_crisis(scenario))
        assert reflection.strip(), scenario

    assert detect_crisis("I want to die")
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
