"""Audio playback utilities using system commands."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
from pathlib import Path


def _detect_player() -> tuple[str, list[str]] | None:
    """Return ``(command, extra_args)`` for the first available audio player.

    Detection order: pw-play (PipeWire), paplay, aplay, ffplay.
    """
    candidates: list[tuple[str, list[str]]] = [
        ("pw-play", []),
        ("paplay", []),
        ("aplay", ["-q"]),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"]),
    ]
    for cmd, args in candidates:
        if shutil.which(cmd) is not None:
            return (cmd, args)
    return None


def play_wav(wav_data: bytes) -> None:
    """Play WAV audio data through the first available system player.

    Raises:
        RuntimeError: No supported audio player is installed.
    """
    player = _detect_player()
    if player is None:
        raise RuntimeError(
            "No audio player found. "
            "Please install one of: pw-play (PipeWire), paplay (PulseAudio), "
            "aplay (ALSA), or ffplay (FFmpeg)."
        )

    cmd, extra_args = player
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.write(wav_data)
    tmp.close()

    proc = subprocess.Popen([cmd, *extra_args, tmp.name])

    def _cleanup() -> None:
        proc.wait()
        Path(tmp.name).unlink(missing_ok=True)

    threading.Thread(target=_cleanup, daemon=True).start()


def can_play() -> bool:
    """Return True if a supported audio player is available."""
    return _detect_player() is not None
