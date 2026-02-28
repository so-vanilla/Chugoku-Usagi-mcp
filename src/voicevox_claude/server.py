"""FastMCP server for VOICEVOX voice synthesis."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from voicevox_claude.audio import play_wav
from voicevox_claude.characters import get_all_characters, get_character
from voicevox_claude.config import load_config
from voicevox_claude.voicevox import VoicevoxClient

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_config = load_config()
_voicevox = VoicevoxClient(_config.voicevox.base_url)
_current_character = get_character(_config.default_character)
_current_style = _config.default_style
_speed = _config.default_speed

mcp = FastMCP("voicevox-claude")


def main() -> None:
    """Entry point for console script."""
    mcp.run()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_characters() -> str:
    """利用可能なVOICEVOXキャラクター一覧を返す。"""
    characters = get_all_characters()
    lines: list[str] = []
    for char in characters.values():
        style_names = ", ".join(f"{s.id}({s.name})" for s in char.styles)
        lines.append(f"- {char.id}: {char.name} — {char.description}")
        lines.append(f"  スタイル: {style_names}")
    return "\n".join(lines)


@mcp.tool()
def set_character(character_id: str, style_id: str = "") -> str:
    """キャラクターを設定する。設定後はそのキャラクターの口調で応答すること。

    Args:
        character_id: キャラクターID（list_charactersで確認可能）
        style_id: スタイルID（省略時はデフォルトスタイル）

    Returns:
        キャラクター情報、利用可能スタイル一覧、キャラクタープロンプト
    """
    global _current_character, _current_style

    try:
        char = get_character(character_id)
    except Exception as e:
        return f"エラー: {e}"

    _current_character = char
    _current_style = style_id if style_id else char.default_style

    try:
        char.get_style(_current_style)
    except Exception:
        _current_style = char.default_style

    style_list = "\n".join(
        f"  - {s.id}: {s.name}" + (" (現在)" if s.id == _current_style else "")
        for s in char.styles
    )

    return (
        f"キャラクター「{char.name}」に設定しました。\n\n"
        f"スタイル一覧:\n{style_list}\n\n"
        f"--- キャラクタープロンプト ---\n{char.system_prompt}"
    )


@mcp.tool()
def speak(text: str, emotion: str = "") -> str:
    """テキストを音声合成して再生する。

    【重要】textには自然な日本語の会話文のみを渡すこと。
    以下は絶対に含めないこと:
    - マークダウン記法（#, *, `, > など）
    - コードブロック
    - URL
    - 箇条書き記号（-, * など）
    - 括弧で囲まれた補足説明

    良い例: "これはPythonのデコレータなのだ"
    悪い例: "これは`Python`の**デコレータ**なのだ"

    Args:
        text: 音声合成するテキスト。自然な日本語会話文のみ。
        emotion: スタイルID（省略時は現在のスタイル）。
                 キャラクターのスタイル一覧から選択。

    Returns:
        再生結果メッセージ
    """
    style_id = emotion if emotion else _current_style

    try:
        style = _current_character.get_style(style_id)
    except Exception:
        style = _current_character.get_default_style()

    try:
        wav = _voicevox.speak(text, style.speaker_id, speed=_speed)
        play_wav(wav)
    except Exception as e:
        return f"音声再生エラー: {e}"

    return f"再生完了（{_current_character.name} / {style.name}）"


@mcp.tool()
def narrate(text: str) -> str:
    """作業中の実況ナレーションを音声で再生する。デフォルトスタイルを使用。

    コーディング作業の進捗や状況を音声で伝えるために使う。
    textには自然な日本語の会話文のみを渡すこと（マークダウン・コード禁止）。

    Args:
        text: ナレーションテキスト。自然な日本語会話文のみ。

    Returns:
        再生結果メッセージ
    """
    style = _current_character.get_default_style()

    try:
        wav = _voicevox.speak(text, style.speaker_id, speed=_speed)
        play_wav(wav)
    except Exception as e:
        return f"ナレーション再生エラー: {e}"

    return f"ナレーション再生完了（{_current_character.name}）"
