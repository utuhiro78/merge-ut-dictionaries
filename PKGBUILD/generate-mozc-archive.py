#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import os
import re
import shutil
import subprocess
import urllib.request


def main():
    # mozc のバージョンを取得
    url = 'https://raw.githubusercontent.com/' + \
            'google/mozc/refs/heads/master/src/version.bzl'

    with urllib.request.urlopen(url) as response:
        lines = response.read().decode()

    version = lines.split('MAJOR = ')[1].split('\n')[0] + '.'
    version += lines.split('MINOR = ')[1].split('\n')[0] + '.'
    version += lines.split('BUILD_OSS = ')[1].split('\n')[0] + '.102'

    # mozc の最終コミット日を取得
    url = 'https://github.com/google/mozc/commits/master/'
    committed_date = get_committed_date(url)

    # mozc のアーカイブが古い場合は取得
    mozc_ver = f'{version}.{committed_date}'
    mozc_dir = f'mozc-{mozc_ver}'
    fcitx_mozc_dir = f'fcitx-mozc-{mozc_ver}'

    if not os.path.exists(f'{mozc_dir}.tar.zst'):
        if os.path.exists('mozc'):
            shutil.rmtree('mozc')

        subprocess.run(
                ['git', 'clone', '--depth', '1', '-b', 'master',
                    'https://github.com/google/mozc.git'], check=True)
        shutil.rmtree('mozc/.git')
        shutil.rmtree('mozc/.github')

        if os.path.exists(mozc_dir):
            shutil.rmtree(mozc_dir)

        os.replace('mozc', mozc_dir)
    else:
        print(f'{mozc_dir} is up to date.')
        exit()

    # fcitx-mozc を取得
    if not os.path.exists(f'{fcitx_mozc_dir}.zip'):
        subprocess.run(
            ['wget', 'https://github.com/' +
                'fcitx/mozc/archive/refs/heads/fcitx.zip',
                '-O', f'{fcitx_mozc_dir}.zip'], check=True)
    else:
        print(f'{fcitx_mozc_dir} is up to date.')

    # fcitx-mozc を展開
    if os.path.exists(fcitx_mozc_dir):
        shutil.rmtree(fcitx_mozc_dir)

    shutil.unpack_archive(f'{fcitx_mozc_dir}.zip')
    os.replace('mozc-fcitx', fcitx_mozc_dir)

    # fcitx5-mozc のファイルを mozc に移動
    os.replace(f'{fcitx_mozc_dir}/scripts', f'{mozc_dir}/scripts')

    shutil.rmtree(f'{mozc_dir}/src/unix')
    os.replace(f'{fcitx_mozc_dir}/src/unix', f'{mozc_dir}/src/unix')

    os.replace(
        f'{fcitx_mozc_dir}/src/MODULE.bazel',
        f'{mozc_dir}/src/MODULE.bazel')
    os.replace(
        f'{fcitx_mozc_dir}/src/build_mozc.py',
        f'{mozc_dir}/src/build_mozc.py')
    os.replace(
        f'{fcitx_mozc_dir}/src/session/BUILD.bazel',
        f'{mozc_dir}/src/session/BUILD.bazel')

    shutil.rmtree(fcitx_mozc_dir)

    # mozc のアーカイブを作成
    subprocess.run(
        ['tar', '--zstd', '-cf', f'{mozc_dir}.tar.zst', mozc_dir], check=True)

    shutil.rmtree(mozc_dir)

    # PKGBUILD を更新
    update_pkgbuild('fcitx5-mozc-ut.PKGBUILD', mozc_ver)
    update_pkgbuild('ibus-mozc-ut.PKGBUILD', mozc_ver)


# GitHub の最終コミット日を取得
def get_committed_date(url):
    with urllib.request.urlopen(url) as response:
        lines = response.read().decode()

    # "committedDate":"2024-01-16T06:05:57.000Z"
    committed_date = lines.split('"committedDate":"')[1]
    # 数字以外を削除
    committed_date = re.sub(r'\D', '', committed_date)[:8]
    return (committed_date)


# PKGBUILD を更新
def update_pkgbuild(pkgbuild, mozc_ver):
    with open(pkgbuild, 'r') as file:
        lines = file.read()

    lines = re.sub('_mozcver=.*\n', f'_mozcver={mozc_ver}\n', lines)

    with open(pkgbuild, 'w') as file:
        file.write(lines)


if __name__ == '__main__':
    main()
