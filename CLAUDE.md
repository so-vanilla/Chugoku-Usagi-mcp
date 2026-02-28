# voicevox-claude

VOICEVOX 音声合成 MCP サーバー。Claude Code からキャラクターボイスで応答する。

## 技術スタック

- Python 3.12, FastMCP (MCPサーバー), httpx (VOICEVOX API)
- VOICEVOX Engine: ローカルまたは Docker (`voicevox/voicevox_engine:cpu-latest`)

## プロジェクト構成

```
src/voicevox_claude/
├── server.py      # FastMCPサーバー本体 (list_characters, set_character, speak, narrate)
├── config.py      # ~/.config/voicevox-claude/config.toml
├── voicevox.py    # VOICEVOX REST APIクライアント (httpx)
├── audio.py       # 音声再生 (pw-play/paplay/aplay/ffplay)
├── errors.py      # カスタム例外
└── characters/
    ├── base.py    # Character, Style dataclass
    ├── __init__.py # レジストリ (TOML読み込み)
    └── data/*.toml # キャラクター定義ファイル
```

## MCPツール使用ルール

### speak / narrate の text パラメータ

**自然な日本語の会話文のみ**を渡すこと。以下を絶対に含めない:

- マークダウン記法（`#`, `**`, `` ` ``, `>` など）
- コードブロック・インラインコード
- URL・ファイルパス
- 箇条書き記号（`-`, `*`, `1.` など）
- 括弧による補足

コードや構造化された情報は通常のテキスト応答で表示し、speak には音声で読み上げる説明文だけを渡す。

### 使い分け

- `speak`: ユーザーへの応答を音声で伝える。emotion でスタイル（感情）を指定可能
- `narrate`: 作業中の実況。デフォルトスタイルで短く伝える

### キャラクター設定

1. `list_characters` で利用可能キャラクターを確認
2. `set_character` でキャラクターを選択。返却されるプロンプトに従って口調を変える
3. 以降の `speak` / `narrate` は設定されたキャラクターの声で再生される

## キャラクター追加

`src/voicevox_claude/characters/data/` に TOML ファイルを追加するだけ（コード変更不要）。

## 開発

```bash
devenv shell
pip install -e .
python -c "from voicevox_claude.server import mcp; print('OK')"
```
