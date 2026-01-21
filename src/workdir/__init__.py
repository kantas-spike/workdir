# workdir/cli.py
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from cookiecutter.main import cookiecutter

# ローカルモジュール
from ._config import (
    add_alias,
    get_alias,
    list_templates,
    remove_alias,
)

import re

__version__ = "0.1.0"


# --------------------------------------------------------------
# ヘルパー関数: ディレクトリ内の次プレフィックス取得
# --------------------------------------------------------------
def _get_next_prefix_from_directory(dir_path: Path) -> str:
    """Return a prefix string for a new subdirectory.

    Subdirectories follow the pattern ``xx_yyy`` where ``xx`` is a two‑digit
    number. The function scans *dir_path* for existing subdirectories, finds the
    maximum numeric prefix and returns that value plus one formatted as a two‑
    digit string with an underscore suffix (e.g. ``"03_"``).
    """

    # Regex to capture leading two digits followed by an underscore.
    prefix_re = re.compile(r"^(\d+)_")
    max_num = -1
    prefix_len = 2
    for entry in dir_path.iterdir():
        if not entry.is_dir():
            continue
        m = prefix_re.match(entry.name)
        if m:
            try:
                prefix = m.group(1)
                num = int(prefix)
                num_len = len(prefix)
                if num_len > prefix_len:
                    prefix_len = num_len
                if num > max_num:
                    max_num = num
            except ValueError:
                # Should not happen because regex ensures digits.
                pass

    if max_num == -1:
        return ""
    else:
        return str(max_num + 1).zfill(prefix_len) + "_"


# --------------------------------------------------------------
# ヘルパー関数（前回と同様）
# --------------------------------------------------------------


def _resolve_template(name: str) -> str:
    alias_ref = get_alias(name)
    if alias_ref:
        return alias_ref

    builtin_map = list_templates()
    if name in builtin_map and builtin_map[name] == "builtin":
        # パッケージ内部のテンプレートを取得
        from importlib import resources

        tmpl_path = resources.files("workdir.templates") / name
        return str(tmpl_path)

    # それ以外はそのままパス/URL とみなす
    return name


def _parse_extra_context(items: Optional[List[str]]) -> dict:
    ctx = {}
    if not items:
        return ctx
    for item in items:
        if "=" not in item:
            print(f"[WARN] 無視されたオプション: {item!r}", file=sys.stderr)
            continue
        k, v = item.split("=", 1)
        ctx[k.strip()] = v.strip()
    return ctx


# --------------------------------------------------------------
# 各サブコマンド本体
# --------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> int:
    tmpl_name = args.type
    if not tmpl_name:
        print(
            "[ERROR] テンプレートが決定できません。--type を指定してください",
            file=sys.stderr,
        )
        return 1

    if not args.output.is_dir():
        print(f"出力先のディレクトリが存在しません。: {args.output}", file=sys.stderr)
        return 1

    try:
        template_ref = _resolve_template(tmpl_name)
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] テンプレート解決失敗: {exc}", file=sys.stderr)
        return 1

    extra_ctx = _parse_extra_context(args.extra_context)
    prefix_key = "wkdir_prefix"

    if prefix_key not in extra_ctx:
        prefix = _get_next_prefix_from_directory(args.output)
        extra_ctx[prefix_key] = prefix

    try:
        workdir_path = cookiecutter(
            template_ref,
            no_input=(not args.use_input),
            extra_context=extra_ctx,
            output_dir=args.output,
            overwrite_if_exists=False,
        )
        print(
            f"[INFO] '{tmpl_name}'から作業ディレクトリ({workdir_path})を作成しました",
            file=sys.stderr,
        )
        print(workdir_path)
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Cookiecutter 実行エラー: {exc}", file=sys.stderr)
        return 1

    return 0


def cmd_list(_: argparse.Namespace) -> int:
    tmpl_map = list_templates()
    if not tmpl_map:
        print("[INFO] 登録テンプレートはありません")
        return 0

    max_len = max(len(k) for k in tmpl_map)
    fmt = f"{{:<{max_len}}}  {{}}"
    print(fmt.format("NAME", "TYPE"))
    print("-" * (max_len + 2 + 6))
    for name, typ in sorted(tmpl_map.items()):
        kind = "builtin" if typ == "builtin" else "alias"
        print(fmt.format(name, kind))
    return 0


def cmd_add_alias(args: argparse.Namespace) -> int:
    add_alias(args.alias, args.ref)
    print(f"[OK] エイリアス '{args.alias}' → {args.ref} を登録しました")
    return 0


def cmd_remove_alias(args: argparse.Namespace) -> int:
    if remove_alias(args.alias):
        print(f"[OK] エイリアス '{args.alias}' を削除しました")
        return 0
    else:
        print(f"[WARN] エイリアス '{args.alias}' は存在しません", file=sys.stderr)
        return 1


def cmd_version(_: argparse.Namespace) -> int:
    from . import __version__

    print(f"workdir {__version__}")
    return 0


# --------------------------------------------------------------
# argparse のセットアップ
# --------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workdir",
        description="Cookiecutterの雛形から作業ディレクトリを生成する CLI ツール",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # new
    p_new = sub.add_parser("new", help="テンプレートから新規プロジェクト作成")
    p_new.add_argument(
        "-t",
        "--type",
        dest="type",
        help="使用テンプレート種別またはエイリアス",
        required=True,
    )
    p_new.add_argument(
        "-o",
        "--output",
        dest="output",
        help="作業フォルダを作成するディレクトリ",
        type=Path,
        required=True,
    )
    p_new.add_argument(
        "--use-input",
        default=False,
        action="store_true",
        help="対話入力を利用する (default: False)",
    )
    p_new.add_argument(
        "-c",
        "--extra-context",
        dest="extra_context",
        action="append",
        help="key=value 形式で Cookiecutter に渡す変数（複数可）",
    )
    p_new.set_defaults(func=cmd_new)

    # list
    sub.add_parser("list", help="登録済みテンプレートを一覧表示").set_defaults(
        func=cmd_list
    )

    # add-alias
    p_add = sub.add_parser(
        "add-alias", help="外部 Cookiecutter テンプレートにエイリアス名を付けて登録"
    )
    p_add.add_argument("alias", help="ローカルで使う名前（例: mytmpl）")
    p_add.add_argument("ref", help="テンプレートへのパス、URL、または git リポジトリ")
    p_add.set_defaults(func=cmd_add_alias)

    # remove-alias
    p_rm = sub.add_parser("remove-alias", help="登録したエイリアスを削除")
    p_rm.add_argument("alias", help="削除対象のエイリアス名")
    p_rm.set_defaults(func=cmd_remove_alias)

    # version
    sub.add_parser("version", help="バージョン情報表示").set_defaults(func=cmd_version)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
