"""LLM provider integration for Google Gemini API (Phase 5).

Keeps API credentials strictly server-side and implements bounded retries,
timeouts, structured JSON parsing, and token usage reporting.
"""
import asyncio
from dataclasses import dataclass
import json
import logging
import re
from typing import Any, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


@dataclass
class LLMResult:
    """Normalized response from the LLM provider."""

    raw_text: str
    parsed_json: Optional[dict[str, Any]]
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMProviderError(RuntimeError):
    """Raised when the external LLM provider fails or is misconfigured."""


def _extract_json_object(text: str) -> Optional[dict[str, Any]]:
    """Parse JSON from raw text, stripping markdown code fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


class GeminiLLMClient:
    """Async client for the Google Gemini generateContent REST API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL

    async def generate_structured(
        self,
        system_instruction: str,
        contents: list[dict[str, Any]],
        max_output_tokens: int = 1200,
        temperature: float = 0.2,
    ) -> LLMResult:
        """Call Gemini generateContent and return parsed structured JSON + token usage."""
        if not self.api_key:
            raise LLMProviderError("LLM_API_KEY is not configured on the server.")

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": "application/json",
            },
        }

        candidate_models = [self.model]
        for fallback_model in ("gemini-3.1-flash-lite-preview", "gemini-flash-latest"):
            if fallback_model not in candidate_models:
                candidate_models.append(fallback_model)

        data: Optional[dict[str, Any]] = None
        used_model = self.model
        last_error_msg = "LLM provider request failed."

        async with httpx.AsyncClient(timeout=15.0) as client:
            for model_name in candidate_models:
                url = f"{GEMINI_API_BASE}/{model_name}:generateContent"
                for attempt in range(2):
                    try:
                        response = await client.post(url, headers=headers, json=payload)
                        if response.status_code in {429, 500, 502, 503, 504} and attempt < 1:
                            await asyncio.sleep(0.4)
                            continue
                        if response.status_code >= 400:
                            logger.warning(
                                "Gemini API returned HTTP %s (model=%s)",
                                response.status_code,
                                model_name,
                            )
                            last_error_msg = f"LLM provider error (HTTP {response.status_code})."
                            break
                        data = response.json()
                        used_model = model_name
                        break
                    except (httpx.TimeoutException, httpx.RequestError) as exc:
                        last_error_msg = f"LLM provider request failed: {exc.__class__.__name__}."
                        break
                if data is not None:
                    break

        if data is None:
            raise LLMProviderError(last_error_msg)

        candidates = data.get("candidates") or []
        if not candidates:
            raise LLMProviderError("LLM provider returned no candidate responses.")

        parts = (candidates[0].get("content") or {}).get("parts") or []
        raw_text = "\n".join(p.get("text", "") for p in parts if p.get("text")).strip()
        if not raw_text:
            raise LLMProviderError("LLM provider returned empty content.")

        usage = data.get("usageMetadata") or {}
        prompt_tokens = int(usage.get("promptTokenCount") or 0)
        completion_tokens = int(usage.get("candidatesTokenCount") or 0)
        total_tokens = int(usage.get("totalTokenCount") or (prompt_tokens + completion_tokens))

        return LLMResult(
            raw_text=raw_text,
            parsed_json=_extract_json_object(raw_text),
            model=used_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )
