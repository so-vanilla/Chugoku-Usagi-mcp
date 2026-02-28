"""Character and Style data models."""

from __future__ import annotations

from dataclasses import dataclass

from voicevox_claude.errors import StyleNotFoundError


@dataclass(frozen=True)
class Style:
    """A voice style for a character."""

    name: str
    id: str
    speaker_id: int


@dataclass(frozen=True)
class Character:
    """A VOICEVOX character with associated voice styles and system prompt."""

    name: str
    id: str
    description: str
    styles: tuple[Style, ...]
    default_style: str
    system_prompt: str

    def get_style(self, style_id: str) -> Style:
        """Return the style matching *style_id*, or raise StyleNotFoundError."""
        for style in self.styles:
            if style.id == style_id:
                return style
        raise StyleNotFoundError(
            f"Style '{style_id}' not found for character '{self.id}'"
        )

    def get_default_style(self) -> Style:
        """Return the default style for this character."""
        return self.get_style(self.default_style)
