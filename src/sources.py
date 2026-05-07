from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


class SourceError(RuntimeError):
    """Raised when an optional external source is unavailable."""


@dataclass(frozen=True)
class QuranFoundationClient:
    base_url: str = "https://apis.quran.foundation/content/api/v4"

    def _headers(self) -> dict[str, str]:
        client_id = os.getenv("QURAN_CLIENT_ID")
        access_token = os.getenv("QURAN_ACCESS_TOKEN")
        if not client_id or not access_token:
            raise SourceError("Quran Foundation API requires QURAN_CLIENT_ID and QURAN_ACCESS_TOKEN.")
        return {"x-client-id": client_id, "x-auth-token": access_token}

    def verse_by_key(self, verse_key: str, translation_id: int = 131) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/verses/by_key/{verse_key}",
            headers=self._headers(),
            params={"translations": translation_id, "words": "false"},
            timeout=12,
        )
        response.raise_for_status()
        return response.json()


@dataclass(frozen=True)
class QuranEncClient:
    base_url: str = "https://quranenc.com/api/v1"

    def translation(self, language: str, surah: int, ayah: int) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/translation/aya/{language}/{surah}/{ayah}",
            timeout=12,
        )
        response.raise_for_status()
        return response.json()


@dataclass(frozen=True)
class HadithApiClient:
    base_url: str = "https://hadithapi.com/api"

    def _params(self) -> dict[str, str]:
        api_key = os.getenv("HADITH_API_KEY")
        if not api_key:
            raise SourceError("Hadith API access requires HADITH_API_KEY.")
        return {"apiKey": api_key}

    def hadiths(self, book: str | None = None, status: str = "Sahih", page: int = 1) -> dict[str, Any]:
        params: dict[str, Any] = {**self._params(), "status": status, "page": page}
        if book:
            params["book"] = book
        response = requests.get(f"{self.base_url}/hadiths", params=params, timeout=12)
        response.raise_for_status()
        return response.json()
