"""VOICEVOX Engine API client."""

from __future__ import annotations

import httpx

from voicevox_claude.errors import VoicevoxConnectionError, VoicevoxSynthesisError


class VoicevoxClient:
    """Synchronous client for VOICEVOX Engine REST API."""

    def __init__(self, base_url: str = "http://localhost:50021") -> None:
        self._base_url = base_url
        self._client = httpx.Client(base_url=base_url, timeout=30.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if the VOICEVOX engine is reachable."""
        try:
            resp = self._client.get("/version")
            resp.raise_for_status()
        except (httpx.ConnectError, httpx.HTTPStatusError):
            return False
        return True

    def audio_query(
        self, text: str, speaker_id: int, speed: float = 1.0
    ) -> dict:
        """Create an audio query and apply speed scaling.

        Raises:
            VoicevoxConnectionError: Engine is not reachable.
        """
        try:
            resp = self._client.post(
                "/audio_query",
                params={"text": text, "speaker": speaker_id},
            )
            resp.raise_for_status()
        except httpx.ConnectError as exc:
            raise VoicevoxConnectionError(
                f"Cannot connect to VOICEVOX at {self._base_url}"
            ) from exc

        query = resp.json()
        query["speedScale"] = speed
        return query

    def synthesis(self, audio_query: dict, speaker_id: int) -> bytes:
        """Synthesise speech from an audio query.

        Returns:
            WAV audio bytes.

        Raises:
            VoicevoxConnectionError: Engine is not reachable.
            VoicevoxSynthesisError: Synthesis HTTP request failed.
        """
        try:
            resp = self._client.post(
                "/synthesis",
                params={"speaker": speaker_id},
                json=audio_query,
            )
        except httpx.ConnectError as exc:
            raise VoicevoxConnectionError(
                f"Cannot connect to VOICEVOX at {self._base_url}"
            ) from exc

        if resp.status_code != 200:
            raise VoicevoxSynthesisError(
                f"Synthesis failed (HTTP {resp.status_code}): {resp.text}"
            )
        return resp.content

    def speak(
        self, text: str, speaker_id: int, speed: float = 1.0
    ) -> bytes:
        """High-level convenience: text -> WAV bytes.

        Combines :meth:`audio_query` and :meth:`synthesis`.
        """
        query = self.audio_query(text, speaker_id, speed=speed)
        return self.synthesis(query, speaker_id)
