#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

HEADERS = {'User-Agent': 'Mozilla/5.0'}


def main():
    # mozc のバージョンを取得
    url = 'https://raw.githubusercontent.com/' + \
            'google/mozc/refs/heads/master/src/version.bzl'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        lines = response.read().decode()

    mozc_ver = lines.split('MAJOR = ')[1].split('\n')[0] + '.'
    mozc_ver += lines.split('MINOR = ')[1].split('\n')[0] + '.'
    mozc_ver += lines.split('BUILD_OSS = ')[1].split('\n')[0] + '.102'

    # Mozc の最終コミット日を取得
    url = 'https://api.github.com/repos/google/mozc/commits/master'
    committed_date = get_committed_date(url)

    # mozc のアーカイブが古い場合は取得
    mozc_ver_full = f'{mozc_ver}.{committed_date}'
    mozc_dir = f'mozc-{mozc_ver_full}'

    if not Path(f'{mozc_dir}.tar.zst').exists():
        if Path('mozc').exists():
            shutil.rmtree('mozc')

        subprocess.run(
                ['git', 'clone', '--depth', '1', '-b', 'master',
                    'https://github.com/google/mozc.git'], check=True)
        shutil.rmtree('mozc/.git')
        shutil.rmtree('mozc/.github')

        if Path(mozc_dir).exists():
            shutil.rmtree(mozc_dir)

        Path('mozc').replace(mozc_dir)
    else:
        print(f'{mozc_dir} is up to date.')
        sys.exit()

    fcitx_file = 'fcitx-mozc.zip'

    # 既存の 'fcitx-mozc.zip' を削除
    Path(fcitx_file).unlink(missing_ok=True)

    # 'fcitx-mozc.zip' を取得
    subprocess.run(
        ['wget', 'https://github.com/' +
            'fcitx/mozc/archive/refs/heads/fcitx.zip',
            '-O', fcitx_file], check=True)

    fcitx_dir = 'mozc-fcitx'

    # 既存の 'mozc-fcitx' を削除
    if Path(fcitx_dir).exists():
        shutil.rmtree(fcitx_dir)

    # 'fcitx-mozc.zip' を展開
    shutil.unpack_archive(fcitx_file)

    # fcitx-mozc のファイルを mozc に移動
    Path(f'{fcitx_dir}/scripts').replace(f'{mozc_dir}/scripts')

    shutil.rmtree(f'{mozc_dir}/src/unix')
    Path(f'{fcitx_dir}/src/unix').replace(f'{mozc_dir}/src/unix')

    Path(
        f'{fcitx_dir}/src/MODULE.bazel').replace(
        f'{mozc_dir}/src/MODULE.bazel')
    Path(
        f'{fcitx_dir}/src/session/BUILD.bazel').replace(
        f'{mozc_dir}/src/session/BUILD.bazel')

    shutil.rmtree(fcitx_dir)

    # mozc のアーカイブを作成
    subprocess.run(
        ['tar', '--zstd', '-cf', f'{mozc_dir}.tar.zst', mozc_dir], check=True)

    shutil.rmtree(mozc_dir)

    # PKGBUILD を更新
    update_pkgbuild('fcitx5-mozc-ut.PKGBUILD', mozc_ver_full)
    update_pkgbuild('ibus-mozc-ut.PKGBUILD', mozc_ver_full)


# GitHub の最終コミット日を取得
def get_committed_date(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        date_str = data['commit']['committer']['date']

    date_str = datetime.fromisoformat(date_str)
    date_str = date_str.strftime('%Y%m%d')

    return date_str


# PKGBUILD を更新
def update_pkgbuild(pkgbuild, mozc_ver_full):
    with open(pkgbuild, 'r') as file:
        lines = file.read()

    lines = re.sub('_mozcver=.*\n', f'_mozcver={mozc_ver_full}\n', lines)

    with open(pkgbuild, 'w') as file:
        file.write(lines)

    return


if __name__ == '__main__':
    main()
