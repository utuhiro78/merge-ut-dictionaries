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
            'google/mozc/master/src/data/version/mozc_version_template.bzl'

    with urllib.request.urlopen(url) as response:
        lines = response.read().decode()

    version = lines.split('MAJOR = ')[1].split('\n')[0] + '.'
    version += lines.split('MINOR = ')[1].split('\n')[0] + '.'
    version += lines.split('BUILD_OSS = ')[1].split('\n')[0] + '.102.'

    # mozc の最終コミット日を取得
    date = get_committed_date('https://github.com/google/mozc/commits/master/')

    # mozc のアーカイブが古い場合は取得
    global mozcver
    mozcver = version + date
    mozcdir = 'mozc-' + mozcver

    if not os.path.exists(mozcdir + '.tar.zst'):
        if os.path.exists('mozc'):
            shutil.rmtree('mozc')

        subprocess.run(
                ['git', 'clone', '--depth', '1',
                    '--recursive', '--shallow-submodules',
                    'https://github.com/fcitx/mozc.git'], check=True)
        shutil.rmtree('mozc/.git')
        os.rename('mozc', mozcdir)
    else:
        print(mozcdir + ' is up to date.')
        subprocess.run(['tar', 'xf', f'{mozcdir}.tar.zst'], check=True)

    # mozc-fcitx の最終コミット日を取得
    date = get_committed_date('https://github.com/fcitx/mozc/commits/fcitx/')

    # mozc-fcitx のアーカイブが古い場合は取得
    if not os.path.exists(f'mozc-fcitx-{date}.zip'):
        subprocess.run(
            ['wget', 'https://github.com/' +
                'fcitx/mozc/archive/refs/heads/fcitx.zip',
                '-O', f'mozc-fcitx-{date}.zip'], check=True)

    if os.path.exists('mozc-fcitx'):
        shutil.rmtree('mozc-fcitx')

    # mozc-fcitx を展開して、mozc-fcitx/src/unix を mozc に移動
    subprocess.run(
        ['unzip', '-q', f'mozc-fcitx-{date}.zip',
            'mozc-fcitx/src/unix/*'], check=True)
    shutil.rmtree(mozcdir + '/src/unix')
    os.rename('mozc-fcitx/src/unix', mozcdir + '/src/unix')
    shutil.rmtree('mozc-fcitx')

    # mozc のアーカイブを作成
    subprocess.run(
        ['tar', '--zstd', '-cf', f'{mozcdir}.tar.zst', mozcdir], check=True)
    shutil.rmtree(mozcdir)

    # PKGBUILD を更新
    update_pkgbuild('fcitx5-mozc-ut.PKGBUILD')
    update_pkgbuild('ibus-mozc-ut.PKGBUILD')


# GitHub の最終コミット日を取得
def get_committed_date(url):
    with urllib.request.urlopen(url) as response:
        lines = response.read().decode()

    # "committedDate":"2024-01-16T06:05:57.000Z"
    date = lines.split('"committedDate":"')[1]
    # 数字以外を削除
    date = re.sub(r'\D', '', date)[:8]
    return (date)


# PKGBUILD を更新
def update_pkgbuild(pkgbuild):
    with open(pkgbuild, 'r') as file:
        lines = file.read()

    lines = re.sub('_mozcver=.*\n', f'_mozcver={mozcver}\n', lines)

    with open(pkgbuild, 'w') as file:
        file.write(lines)


if __name__ == '__main__':
    main()
