"""Custom exceptions for voicevox-claude."""


class VoicevoxClaudeError(Exception):
    """Base exception."""


class VoicevoxConnectionError(VoicevoxClaudeError):
    """VOICEVOX engine is not reachable."""


class VoicevoxSynthesisError(VoicevoxClaudeError):
    """Audio synthesis failed."""
