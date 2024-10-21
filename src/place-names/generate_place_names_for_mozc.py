#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import jaconv
import re
import urllib.request

file_name = 'KEN_ALL.CSV.fixed'
dict_name = 'mozcdic-ut-place-names.txt'

# Mozc の一般名詞のIDを取得
url = 'https://raw.githubusercontent.com/' + \
        'google/mozc/master/src/data/dictionary_oss/id.def'

with urllib.request.urlopen(url) as response:
    id_mozc = response.read().decode()

id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]

with open(file_name, 'r') as dict_file:
    lines = dict_file.read().splitlines()

# 数字の1から9までの読みを作成
d1 = ['', 'いち', 'に', 'さん', 'よん', 'ご', 'ろく', 'なな', 'はち', 'きゅう']

# 数字の10から59までの読みを作成
d2 = ['じゅう', 'にじゅう', 'さんじゅう', 'よんじゅう', 'ごじゅう']

for p in range(5):
    # append していくので range(len(d1)) にはしない
    for q in range(10):
        d1.append(d2[p] + d1[q])

l2 = []

for i in range(len(lines)):
    # 01101,"064  ","0640820",
    # "ホッカイドウ","サッポロシチュウオウク","オオドオリニシ(20-28チョウメ)",
    # "北海道","札幌市中央区","大通西（２０〜２８丁目）",1,0,1,0,0,0

    entry = lines[i].replace('"', '').split(",")

    # 読みをひらがなに変換
    entry[3] = jaconv.kata2hira(entry[3])
    entry[4] = jaconv.kata2hira(entry[4])
    entry[5] = jaconv.kata2hira(entry[5])

    # 読みの「・」を取る
    entry[5] = entry[5].replace('・', '')

    # 市を出力
    mozc_ent = [entry[4], id_mozc, id_mozc, '9000', entry[7]]
    l2.append('\t'.join(mozc_ent) + '\n')

    # 町の読みが半角数字を含むか確認
    c = ''.join(filter(str.isdigit, entry[5]))

    # 町の読みの半角数字が60未満の場合はひらがなに変換
    #     さっぽろしひがしくきた51じょうひがし
    if c != '' and 0 < int(c) < 60:
        entry[5] = entry[5].replace(c, d1[int(c)])

    # 町の読みがひらがな以外を含む場合はスキップ
    #     OAPたわー
    # 町の表記が空の場合はスキップ
    if entry[5] != ''.join(re.findall('[ぁ-ゔー]', entry[5])) or \
            entry[8] == '':
        continue

    # 町を出力
    mozc_ent = [entry[5], id_mozc, id_mozc, '9000', entry[8]]
    l2.append('\t'.join(mozc_ent) + '\n')

    # 市+町を出力
    mozc_ent = [
        entry[4] + entry[5], id_mozc, id_mozc, '9000', entry[7] + entry[8]]
    l2.append('\t'.join(mozc_ent) + '\n')

lines = sorted(set(l2))

with open(dict_name, 'w', encoding='utf-8') as dict_file:
    dict_file.writelines(lines)
