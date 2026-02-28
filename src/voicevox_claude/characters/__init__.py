"""Character loading and registry."""

from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path

from voicevox_claude.characters.base import Character, Style
from voicevox_claude.errors import CharacterNotFoundError

__all__ = ["Character", "Style", "get_all_characters", "get_character"]


def _load_character(path: Path) -> Character:
    """Read a TOML file and construct a Character."""
    with open(path, "rb") as f:
        data = tomllib.load(f)

    char = data["character"]
    styles = tuple(
        Style(name=s["name"], id=s["id"], speaker_id=s["speaker_id"])
        for s in data["styles"]
    )
    return Character(
        name=char["name"],
        id=char["id"],
        description=char["description"],
        styles=styles,
        default_style=char["default_style"],
        system_prompt=data["prompt"]["system"],
    )


def get_all_characters() -> dict[str, Character]:
    """Scan ``characters/data/*.toml`` and return a dict keyed by character id."""
    data_dir = importlib.resources.files(__package__).joinpath("data")
    characters: dict[str, Character] = {}
    for resource in data_dir.iterdir():
        if resource.name.endswith(".toml"):
            path = Path(str(resource))
            character = _load_character(path)
            characters[character.id] = character
    return characters


def get_character(character_id: str) -> Character:
    """Return a character by id, or raise CharacterNotFoundError."""
    characters = get_all_characters()
    if character_id not in characters:
        raise CharacterNotFoundError(f"Character '{character_id}' not found")
    return characters[character_id]
