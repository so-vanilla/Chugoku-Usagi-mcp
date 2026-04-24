"""Audio playback utilities using system commands."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

_lock = threading.Lock()
_current_proc: subprocess.Popen[bytes] | None = None
_current_tmp: Path | None = None


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


def _stop_current() -> None:
    global _current_proc, _current_tmp
    if _current_proc is not None and _current_proc.poll() is None:
        _current_proc.terminate()
        _current_proc.wait()
    if _current_tmp is not None:
        _current_tmp.unlink(missing_ok=True)
    _current_proc = None
    _current_tmp = None


def play_wav(wav_data: bytes) -> None:
    """Play WAV audio data through the first available system player.

    Stops any currently playing audio before starting new playback.

    Raises:
        RuntimeError: No supported audio player is installed.
    """
    global _current_proc, _current_tmp

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
    tmp_path = Path(tmp.name)

    with _lock:
        _stop_current()
        proc = subprocess.Popen([cmd, *extra_args, tmp.name])
        _current_proc = proc
        _current_tmp = tmp_path

    def _cleanup() -> None:
        global _current_proc, _current_tmp
        proc.wait()
        with _lock:
            if _current_proc is proc:
                _current_proc = None
            if _current_tmp == tmp_path:
                _current_tmp = None
        tmp_path.unlink(missing_ok=True)

    threading.Thread(target=_cleanup, daemon=True).start()


def can_play() -> bool:
    """Return True if a supported audio player is available."""
    return _detect_player() is not None
