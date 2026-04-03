from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings


@dataclass(frozen=True)
class TranslationResult:
    ok: bool
    text: str
    error: Optional[str] = None


def translate_en_to_ru(text: str) -> TranslationResult:
    text = (text or "").strip()
    if not text:
        return TranslationResult(ok=True, text="")

    auth_key = (getattr(settings, "DEEPL_AUTH_KEY", "") or "").strip()
    if not auth_key:
        return TranslationResult(ok=False, text=text, error="DEEPL_AUTH_KEY is not set")

    api_url = (getattr(settings, "DEEPL_API_URL", "") or "https://api-free.deepl.com/v2/translate").strip()

    try:
        resp = requests.post(
            api_url,
            data={
                "text": text,
                "source_lang": "EN",
                "target_lang": "RU",
            },
            headers={
                "Authorization": f"DeepL-Auth-Key {auth_key}",
            },
            timeout=20,
        )
    except Exception as e:
        return TranslationResult(ok=False, text=text, error=str(e))

    if resp.status_code >= 400:
        return TranslationResult(ok=False, text=text, error=f"DeepL HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        payload = resp.json()
        translated = payload["translations"][0]["text"]
    except Exception:
        return TranslationResult(ok=False, text=text, error=f"DeepL bad JSON: {resp.text[:300]}")

    return TranslationResult(ok=True, text=(translated or "").strip())
