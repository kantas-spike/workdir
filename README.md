# Workdir CLI ツール

このプロジェクトは、[Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html#)用に作成された雛形から簡単に作業ディレクトリを作成するCLIツーです。

## 機能

- Cookiecutter用雛形の管理(`list`, `add-alias`, `remove-alias`)
- ワンコマンドで新しい作業ディレクトリを初期化(`new`)

## インストール手順

プロジェクト管理に [uv](https://docs.astral.sh/uv/getting-started/) を使用しています。あらかじめインストールしてください。

```sh
# リポジトリをクローン
git clone <repo‑url> .

# パッケージをインストール
uv sync

# uv ツールとしてインストール
uv tool install .
```

## 使い方

`workdir --help` を実行すると、全コマンドとオプションの一覧が表示されます。

```sh
usage: workdir [-h] {new,list,add-alias,remove-alias,version} ...

Cookiecutterの雛形から作業ディレクトリを生成する CLI ツール

positional arguments:
  {new,list,add-alias,remove-alias,version}
    new                 テンプレートから新規プロジェクト作成
    list                登録済みテンプレートを一覧表示
    add-alias           外部 Cookiecutter テンプレートにエイリアス名を付けて登録
    remove-alias        登録したエイリアスを削除
    version             バージョン情報表示

options:
  -h, --help            show this help message and exit
```

### 雛形の登録

Cookiecutter用の雛形を設定ファイルに追加する必要があります。

設定ファイルは`~/.config/workdir/config.yaml`です。

```yaml
# config.yaml
aliases: {}
```

初期状態では、利用できる雛形がないため、雛形一覧を実行しても何も表示されません。

```shell
% workdir list
[INFO] 登録テンプレートはありません
```

デフォルトでは、Cookiecutter用の雛形が登録されていないため、`add-alias`で登録します。

例えば、[Cookiecutter — cookiecutter 2.6.0 documentation](https://cookiecutter.readthedocs.io/en/latest/README.html)で紹介されている、[audreyfeldroy/cookiecutter-pypackage: Cookiecutter template for a Python package.](https://github.com/audreyfeldroy/cookiecutter-pypackage)を雛形として登録します。

今回は、別名 `mypackage`として、雛形のURL(`https://github.com/audreyfeldroy/cookiecutter-pypackage.git`)を登録します。

```shell
% workdir add-alias pypackage https://github.com/audreyfeldroy/cookiecutter-pypackage.git”
[OK] エイリアス 'pypackage' → https://github.com/audreyfeldroy/cookiecutter-pypackage.git を登録しました
```

雛形一覧を確認すると、`pypackage`が登録されていますね。

```shell
% workdir list
[INFO] 登録テンプレートはありません
NAME       TYPE
-----------------
pypackage  alias
```

更新された設定ファイル(`~/.config/workdir/config.yaml`)は、以下になります。

```yaml
aliases:
  pypackage: https://github.com/audreyfeldroy/cookiecutter-pypackage.git
```

また、`add-alias`には、URLだけではなくファイルパスも指定できます。

### 作業ディレクトリの作成

`workdir new`コマンドで作業ディレクトリを作成します。

```shell
% workdir new -h
usage: workdir new [-h] -t TYPE -o OUTPUT [--use-input] [-c EXTRA_CONTEXT]

options:
  -h, --help            show this help message and exit
  -t, --type TYPE       使用テンプレート種別またはエイリアス
  -o, --output OUTPUT   作業フォルダを作成するディレクトリ
  --use-input           対話入力を利用する (default: False)
  -c, --extra-context EXTRA_CONTEXT
                        key=value 形式で Cookiecutter に渡す変数（複数可）
```

雛形`pypackage`が利用できるようになったので、実際に作業ディレクトリを作成してみましょう。
`-t`オプションに雛形の名前`pypackage`を指定します。
そして、`-o`オプションに作業ディレクトリを作成する先になるディレクトリを指定します。
今回は、`-o`に`~/wk`を指定します。

対話的にCookiecutterの変数を設定する場合は、`--use-input`オプションを指定します。

```shell
% workdir new -t pypackage -o ~/wk --use-input
  [1/9] full_name (Audrey M. Roy Greenfeld): my name
  [2/9] email (audreyfeldroy@example.com): myaddress@example.com
  [3/9] github_username (audreyfeldroy): myname
  [4/9] pypi_package_name (python-boilerplate): test
  [5/9] project_name (Python Boilerplate): test
  [6/9] project_slug (test):
  [7/9] project_short_description (Python Boilerplate contains all the boilerplate you need to create a Python package.):
  [8/9] pypi_username (myname):
  [9/9] first_version (0.1.0):
Your Python package project has been created successfully!
[INFO] 'pypackage'から作業ディレクトリ(~/wk/test)を作成しました
```

対話的ではなく、Cookiecutterの変数を明示的に指定する場合は、`-c`オプションに`key=value`形式で変数の値を指定します。

```shell
% workdir new -t pypackage -o ~/wk -c project_name=test -c email=myaddress@example.com -c github_username=myname -c pypi_package_name=test -c project_name=test
Your Python package project has been created successfully!
[INFO] 'pypackage'から作業ディレクトリ(~/wk/test)を作成しました
```

## ライセンス

このプロジェクトは MIT License の下で提供されています。詳細は [`LICENSE`](./LICENSE)ご覧ください。
