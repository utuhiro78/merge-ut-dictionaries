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
    # Mozc のバージョンを取得
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

    mozc_ver_full = f'{mozc_ver}.{committed_date}'
    mozc_dir = f'mozc-{mozc_ver_full}'

    # Mozc の最新アーカイブが存在する場合は終了
    if Path(f'{mozc_dir}.tar.zst').exists():
        print('The archive is up to date.')
        sys.exit()

    # Mozc の最新アーカイブを取得
    mozc_file = 'mozc.zip'
    Path(mozc_file).unlink(missing_ok=True)

    url = 'https://github.com/google/mozc/archive/refs/heads/master.zip'
    urllib.request.urlretrieve(url, mozc_file)

    extract_dir = 'mozc-master'
    if Path(extract_dir).exists():
        shutil.rmtree(extract_dir)

    shutil.unpack_archive(mozc_file)
    Path(mozc_file).unlink(missing_ok=True)
    Path(extract_dir).replace(mozc_dir)

    # Fcitx-mozc の最新アーカイブを取得
    fcitx_file = 'fcitx-mozc.zip'
    Path(fcitx_file).unlink(missing_ok=True)

    url = 'https://github.com/fcitx/mozc/archive/refs/heads/fcitx.zip'
    urllib.request.urlretrieve(url, fcitx_file)

    extract_dir = 'mozc-fcitx'
    if Path(extract_dir).exists():
        shutil.rmtree(extract_dir)

    shutil.unpack_archive(fcitx_file)
    Path(fcitx_file).unlink(missing_ok=True)

    # Fcitx-mozc のファイルを Mozc に移動
    Path(f'{extract_dir}/scripts').replace(f'{mozc_dir}/scripts')

    shutil.rmtree(f'{mozc_dir}/src/unix')
    Path(f'{extract_dir}/src/unix').replace(f'{mozc_dir}/src/unix')

    Path(
        f'{extract_dir}/src/MODULE.bazel').replace(
        f'{mozc_dir}/src/MODULE.bazel')
    Path(
        f'{extract_dir}/src/session/BUILD.bazel').replace(
        f'{mozc_dir}/src/session/BUILD.bazel')

    shutil.rmtree(extract_dir)

    # Mozc のアーカイブを作成
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
