#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import io
import re
import tarfile
import urllib.request
from unicodedata import normalize

# ひらがなと長音にマッチ
RE_HIRAGANA = re.compile(r'[ぁ-ゔー]+')
# '_4小野坂_3昌也' を '小野坂昌也' に変換
RE_JINMEI_YOMISUU = re.compile(r'[_0-9]')


def main():
    alt_canna_file = 'alt-cannadic-110208.tar.bz2'
    url = 'https://ftp.iij.ad.jp/pub/osdn.jp/alt-cannadic/50881/' + \
        f'{alt_canna_file}'

    urllib.request.urlretrieve(url, alt_canna_file)
    alt_canna = []

    with tarfile.open(alt_canna_file) as tar:
        files = [
            'alt-cannadic-110208/gcanna.ctd',
            'alt-cannadic-110208/g_fname.ctd']
        for file in files:
            f = tar.extractfile(file)
            with io.TextIOWrapper(f, encoding='euc_jp') as text_file:
                for entry in text_file:
                    entry = entry.strip().split(' ')
                    entry = generate_dict_entry(entry)
                    if entry:
                        alt_canna.extend(entry)

    alt_canna = remove_duplicate(alt_canna)

    with open('mozcdic-ut-alt-cannadic.txt', 'w', encoding='utf-8') as file:
        for entry in alt_canna:
            file.write(f'{"\t".join(entry)}\n')


def generate_dict_entry(entry):
    # あきびん, #T35*202, 空き瓶, 空瓶, #T35*151, 空きビン, 空ビン
    yomi = entry[0]
    yomi = yomi.replace('う゛', 'ゔ')

    # 読みが2文字以下の場合はスキップ
    # 読みがひらがな以外を含む場合はスキップ
    if len(yomi) < 3 or \
            not RE_HIRAGANA.fullmatch(yomi):
        return None

    id = '0000'
    c = 1

    # 読みを除去したエントリを作る
    entry = entry[1:]
    entry_mod = []

    for entry_part in entry:
        # 「#」で始まるエントリの場合は品詞とコストを取得
        #     #T35*202 空き瓶 空瓶 #T35*151 空きビン 空ビン
        if entry_part.startswith('#'):
            if entry_part.startswith('#T3') or \
                    entry_part.startswith('#T0') or \
                    entry_part.startswith('#JN') or \
                    entry_part.startswith('#KK') or \
                    entry_part.startswith('#CN'):
                cost = entry_part.split('*', 1)[1]
                cost = (9000 - int(cost)) + c
                c += 2
                id = '0000'
                continue
            elif entry_part.startswith('#_'):
                entry_part = entry_part[1:]
                entry_part = RE_JINMEI_YOMISUU.sub('', entry_part)
            else:
                id = None

        if not id:
            continue

        hyouki = entry_part
        # 表記が1文字以下の場合はスキップ
        if len(hyouki) < 2:
            continue

        hyouki = normalize('NFKC', hyouki)
        entry_mod.append([yomi, cost, hyouki])

    return entry_mod


def remove_duplicate(alt_canna):
    # yomi -> hyouki -> cost の優先順でソート
    alt_canna.sort(key=lambda x: (x[0], x[2], x[1]))
    alt_canna_mod = []
    prev_key = ()

    for entry in alt_canna:
        yomi, cost, hyouki = entry
        current_key = (yomi, hyouki)

        # 重複する UT エントリを削除
        # Mozc 形式のエントリを作成
        if prev_key != current_key:
            entry = [yomi, '0000', '0000', str(cost), hyouki]
            alt_canna_mod.append(entry)

        prev_key = current_key

    return alt_canna_mod


if __name__ == '__main__':
    main()
