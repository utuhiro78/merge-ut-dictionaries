#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import jaconv
import lzma
import re
import subprocess
import urllib.request

url = 'https://github.com/neologd/mecab-ipadic-neologd/tree/master/seed'
with urllib.request.urlopen(url) as response:
    html = response.read().decode('utf-8')

neologdver = html.split('mecab-user-dict-seed.')[1]
neologdver = neologdver.split('.csv.xz')[0]

subprocess.run(
    ['wget', '-nc', 'https://github.com/neologd/mecab-ipadic-neologd/' +
        f'raw/master/seed/mecab-user-dict-seed.{neologdver}.csv.xz'])

with lzma.open(f'mecab-user-dict-seed.{neologdver}.csv.xz') as xz_ref:
    lines = xz_ref.read().decode()

lines = lines.splitlines()
dict_name = 'mozcdic-ut-neologd.txt'

# Mozc の一般名詞のIDを取得
url = 'https://raw.githubusercontent.com/' + \
        'google/mozc/master/src/data/dictionary_oss/id.def'

with urllib.request.urlopen(url) as response:
    id_mozc = response.read().decode()

id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]

l2 = []

for i in range(len(lines)):
    # 表層形,左文脈ID,右文脈ID,コスト,品詞1,品詞2,品詞3,品詞4,品詞5,品詞6,
    # 原形,読み,発音

    # little glee monster,1289,1289,2098,名詞,固有名詞,人名,一般,*,*,
    # Little Glee Monster,リトルグリーモンスター,リトルグリーモンスター

    # リトルグリーモンスター,1288,1288,-1677,名詞,固有名詞,一般,*,*,*,
    # Little Glee Monster,リトルグリーモンスター,リトルグリーモンスター

    entry = lines[i].split(',')

    # 「読み」を読みにする
    yomi = entry[11].replace('=', '')
    yomi = yomi.replace('・', '')

    # 「原形」を表記にする
    hyouki = entry[10]

    # 読みが2文字以下の場合はスキップ
    # 表記が1文字以下の場合はスキップ
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    # 表記が英数字のみの場合はスキップ
    # 表記と entry[0] が異なる場合はスキップ
    # 名詞以外の場合はスキップ
    # 地名をスキップ。地名は郵便番号ファイルから生成する
    # 名をスキップ
    if len(yomi) < 3 or \
            len(hyouki) < 2 or \
            len(hyouki) > 25 or \
            len(hyouki) == len(hyouki.encode()) or \
            hyouki != entry[0] or \
            entry[4] != '名詞' or \
            entry[6] == '地域' or \
            entry[7] == '名':
        continue

    # 読みのカタカナをひらがなに変換
    yomi = jaconv.kata2hira(yomi)
    yomi = yomi.replace('ゐ', 'い').replace('ゑ', 'え')

    # 読みがひらがな以外を含む場合はスキップ
    if yomi != ''.join(re.findall('[ぁ-ゔー]', yomi)):
        continue

    cost = int(entry[3])

    # コストが 0 未満の場合は 0 にする
    if cost < 0:
        cost = 0
    # コストが 10000 以上の場合は 9999 にする
    elif cost > 9999:
        cost = 9999

    # 全体のコストを 8000 台にする
    cost = 8000 + (cost // 10)

    # 読み, 表記, コスト の順に並べる
    entry = [yomi, hyouki, str(cost)]
    l2.append('\t'.join(entry))

lines = sorted(l2)
l2 = []

for i in range(len(lines)):
    entry1 = lines[i].split('\t')
    entry2 = lines[i - 1].split('\t')

    # [読み, 表記] が重複するエントリをスキップ
    if entry1[0:2] == entry2[0:2]:
        continue

    # [読み, id_mozc, id_mozc, コスト, 表記] の順に並べる
    entry1 = [entry1[0], id_mozc, id_mozc, entry1[2], entry1[1]]
    l2.append('\t'.join(entry1) + '\n')

lines = l2

with open(dict_name, 'w', encoding='utf-8') as dict_file:
    dict_file.writelines(lines)
