#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import gzip
import jaconv
import urllib.request
from unicodedata import normalize

urllib.request.urlretrieve(
    'http://ftp.edrdg.org/pub/Nihongo/edict2.gz', 'edict2.gz')

with gzip.open('edict2.gz', 'rt', encoding='EUC-JP') as file:
    lines = file.read().splitlines()

l2 = []

for i in range(len(lines)):
    # エントリが全角スペースで始まる場合はスキップ
    # 名詞でなければスキップ
    if lines[i][0] == '　' or \
            ' /(n' not in lines[i]:
        continue

    entry = lines[i].split(' /(n')[0]

    # カタカナ語には読みが付与されていないので、表記から読みを作る
    # 表記が複数ある場合は、最初のものだけを採用する
    #     ブラックコーヒー;ブラック・コーヒー /
    if ' [' not in entry:
        hyouki = entry.split(';')[0]
        yomi = hyouki
    # 表記または読みが複数ある場合は、それぞれ最初のものだけを採用する
    #     暗唱;暗誦;諳誦 [あんしょう;あんじゅ(暗誦,諳誦)(ok)] /
    else:
        entry = entry.split(' [')
        yomi = entry[1].split(']')[0].split(';')[0]
        hyouki = entry[0].split(';')[0]

    hyouki = hyouki.split('(')[0]
    yomi = yomi.split('(')[0]
    yomi = yomi.translate(str.maketrans('', '', ' =・'))

    # 読みが2文字以下の場合はスキップ
    # 表記が1文字以下の場合はスキップ
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    if len(yomi) < 3 or \
            len(hyouki) < 2 or \
            len(hyouki) > 25:
        continue

    # 読みのカタカナをひらがなに変換
    yomi = jaconv.kata2hira(yomi)
    yomi = yomi.translate(str.maketrans('ゐゑ', 'いえ'))

    # 表記の全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)

    entry = [yomi, '0000', '0000', '8000', hyouki]
    l2.append('\t'.join(entry) + '\n')

lines = sorted(set(l2))
dict_name = 'mozcdic-ut-edict2.txt'

with open(dict_name, 'w', encoding='utf-8') as file:
    file.writelines(lines)
