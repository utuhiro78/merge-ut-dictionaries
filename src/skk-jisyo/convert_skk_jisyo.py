#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import urllib.request
from unicodedata import normalize


def main():
    urllib.request.urlretrieve(
        'https://github.com/skk-dev/dict/raw/refs/heads/master/SKK-JISYO.L',
        'SKK-JISYO.L')

    skk_jisyo = []

    with open('SKK-JISYO.L', 'r', encoding='EUC-JP') as file:
        for line in file:
            if not line or line.startswith(';'):
                continue

            entry = generate_dict_entry(line)
            if entry:
                skk_jisyo.extend(entry)

    skk_jisyo = sorted(skk_jisyo)

    with open('mozcdic-ut-skk-jisyo.txt', 'w', encoding='utf-8') as file:
        for entry in skk_jisyo:
            yomi, cost, hyouki = entry
            entry = [yomi, '0000', '0000', cost, hyouki]
            file.writelines(f'{"\t".join(entry)}\n')


def generate_dict_entry(line):
    # わりふr /割り振/割振/
    # いずみ /泉/和泉;地名,大阪/出水;地名,鹿児島/
    if ' /' not in line:
        return None

    entry = line.split(' /', 1)
    yomi, hyouki = entry

    yomi = yomi.replace('う゛', 'ゔ')

    # 読みが2文字以下の場合はスキップ
    # 読みが英数字を含む場合はスキップ
    if len(yomi) < 3 or \
            len(yomi.encode('utf-8')) != len(yomi) * 3:
        return None

    hyouki_set = hyouki.split('/')
    hyouki_prev = ''
    entry_mod = []
    c = 0

    for hyouki in hyouki_set:
        hyouki = hyouki.split(';')[0]

        # 表記の全角英数を半角に変換
        hyouki = normalize('NFKC', hyouki)

        # 表記が1文字の場合はスキップ
        # 表記が英数字のみの場合はスキップ
        if len(hyouki) < 2 or \
                len(hyouki.encode('utf-8')) == len(hyouki):
            continue

        # 1つ前の表記と同じ場合はスキップ
        # ＩＣカード/ICカード/
        if hyouki == hyouki_prev:
            continue

        # 2個目以降の表記はコストを上げる
        cost = 8000 + (10 * c)

        entry_mod.append([yomi, str(cost), hyouki])
        hyouki_prev = hyouki
        c += 1

    return entry_mod


if __name__ == '__main__':
    main()
