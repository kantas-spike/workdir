# workdir/_config.py
from pathlib import Path
from typing import Dict, Any

import yaml

CONFIG_DIR = Path.home() / ".config" / "workdir"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def _ensure_config_file() -> None:
    """設定ディレクトリ・ファイルが無ければ作成（空 dict）"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config({})


def load_config() -> Dict[str, Any]:
    _ensure_config_file()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f)


def add_alias(name: str, ref: str) -> None:
    cfg = load_config()
    aliases = cfg.setdefault("aliases", {})
    aliases[name] = ref
    save_config(cfg)


def remove_alias(name: str) -> bool:
    cfg = load_config()
    aliases = cfg.get("aliases", {})
    if name in aliases:
        del aliases[name]
        save_config(cfg)
        return True
    return False


def get_alias(name: str):
    """エイリアスがあればその参照先を返す。無ければ None"""
    cfg = load_config()
    return cfg.get("aliases", {}).get(name)


def list_templates() -> Dict[str, str]:
    """
    組み込みテンプレート（パッケージ内部） + ユーザーエイリアス
    戻り値は {テンプレート名: "builtin" または 参照先文字列}
    """
    result = {}

    # ── ユーザーエイリアス ────────────────────────────────────────
    cfg = load_config()
    for name, ref in cfg.get("aliases", {}).items():
        result[name] = ref

    return result
