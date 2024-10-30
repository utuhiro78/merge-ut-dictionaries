#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import gzip
import urllib.request
from unicodedata import normalize

urllib.request.urlretrieve(
    'https://skk-dev.github.io/dict/SKK-JISYO.L.gz', 'SKK-JISYO.L.gz')

with gzip.open('SKK-JISYO.L.gz', 'rt', encoding='EUC-JP') as file:
    lines = file.read().splitlines()

# Mozc の一般名詞のIDを取得
url = 'https://raw.githubusercontent.com/' + \
        'google/mozc/master/src/data/dictionary_oss/id.def'

with urllib.request.urlopen(url) as response:
    id_mozc = response.read().decode()

id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]

l2 = []

for i in range(len(lines)):
    # わりふr /割り振/割振/
    # いずみ /泉/和泉;地名,大阪/出水;地名,鹿児島/
    entry = lines[i].split(' /')
    yomi = entry[0].replace('う゛', 'ゔ')

    # 読みが2文字以下の場合はスキップ
    # 読みが英数字を含む場合はスキップ
    if len(yomi) < 3 or \
            len(yomi.encode('utf-8')) != len(yomi) * 3:
        continue

    hyouki = entry[1].split('/')

    for c in range(len(hyouki)):
        hyouki[c] = hyouki[c].split(';')[0]

        # 表記の全角英数を半角に変換
        hyouki[c] = normalize('NFKC', hyouki[c])

        # 表記が1文字の場合はスキップ
        # 表記が英数字のみの場合はスキップ
        if len(hyouki[c]) < 2 or \
                len(hyouki[c].encode('utf-8')) == len(hyouki[c]):
            continue

        # 1つ前の表記と同じ場合はスキップ
        # ＩＣカード/ICカード/
        if hyouki[c] == hyouki[c - 1]:
            continue

        # 2個目以降の表記のコストを上げる
        cost = 8000 + (10 * c)

        entry = [yomi, id_mozc, id_mozc, str(cost), hyouki[c]]
        l2.append('\t'.join(entry) + '\n')

lines = sorted(set(l2))
dict_name = 'mozcdic-ut-skk-jisyo.txt'

with open(dict_name, 'w', encoding='utf-8') as file:
    file.writelines(lines)
