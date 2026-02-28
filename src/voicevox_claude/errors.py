"""Custom exceptions for voicevox-claude."""


class VoicevoxClaudeError(Exception):
    """Base exception."""


class VoicevoxConnectionError(VoicevoxClaudeError):
    """VOICEVOX engine is not reachable."""


class VoicevoxSynthesisError(VoicevoxClaudeError):
    """Audio synthesis failed."""


class CharacterNotFoundError(VoicevoxClaudeError):
    """Requested character does not exist."""


class StyleNotFoundError(VoicevoxClaudeError):
    """Requested style does not exist for the character."""
