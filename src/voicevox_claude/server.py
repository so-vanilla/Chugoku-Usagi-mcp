"""FastMCP server for VOICEVOX voice synthesis."""

from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from voicevox_claude.audio import play_wav
from voicevox_claude.config import load_config
from voicevox_claude.voicevox import VoicevoxClient

# ---------------------------------------------------------------------------
# Character data (loaded once from TOML)
# ---------------------------------------------------------------------------

_CHAR_TOML = Path(
    str(importlib.resources.files("voicevox_claude").joinpath("characters/data/chugoku_usagi.toml"))
)

with open(_CHAR_TOML, "rb") as _f:
    _char_data = tomllib.load(_f)

_CHAR_NAME: str = _char_data["character"]["name"]
_STYLES: dict[str, dict] = {s["id"]: s for s in _char_data["styles"]}
_DEFAULT_STYLE: str = _char_data["character"]["default_style"]
_SYSTEM_PROMPT: str = _char_data["prompt"]["system"]

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_config = load_config()
_voicevox = VoicevoxClient(_config.voicevox.base_url)
_speed = _config.default_speed

mcp = FastMCP("voicevox-claude", instructions=_SYSTEM_PROMPT)


def main() -> None:
    """Entry point for console script."""
    mcp.run()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


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

    良い例: "...これはPythonの人がよく使うデコレータです"
    悪い例: "これは`Python`の**デコレータ**なのだ"

    Args:
        text: 音声合成するテキスト。自然な日本語会話文のみ。
        emotion: スタイルID（省略時はノーマル）。
                 normal / surprise / sad / exhausted から選択。

    Returns:
        再生結果メッセージ
    """
    style = _STYLES.get(emotion) or _STYLES[_DEFAULT_STYLE]

    try:
        wav = _voicevox.speak(text, style["speaker_id"], speed=_speed)
        play_wav(wav)
    except Exception as e:
        return f"音声再生エラー: {e}"

    return f"再生完了（{_CHAR_NAME} / {style['name']}）"


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
    style = _STYLES[_DEFAULT_STYLE]

    try:
        wav = _voicevox.speak(text, style["speaker_id"], speed=_speed)
        play_wav(wav)
    except Exception as e:
        return f"ナレーション再生エラー: {e}"

    return f"ナレーション再生完了（{_CHAR_NAME}）"
