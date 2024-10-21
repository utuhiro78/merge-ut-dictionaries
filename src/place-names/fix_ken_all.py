#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import urllib.request
from unicodedata import normalize
from zipfile import ZipFile

urllib.request.urlretrieve(
    'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip',
    'ken_all.zip')

with ZipFile('ken_all.zip') as zip_ref:
    with zip_ref.open('KEN_ALL.CSV') as file:
        lines = file.read().decode('SJIS')

lines = normalize('NFKC', lines)
lines = lines.splitlines()

dict_name = 'KEN_ALL.CSV.fixed'

with open(dict_name, 'w', encoding='utf-8') as dict_file:
    dict_file.write('')

for i in range(len(lines)):
    # 01101,"064  ","0640820",
    # "ホッカイドウ","サッポロシチュウオウク","オオドオリニシ(20-28チョウメ)",
    # "北海道","札幌市中央区","大通西(20〜28丁目)",1,0,1,0,0,0

    entry = lines[i].split(",")

    # 町域に次の文字列が含まれていればスキップ
    str_ng = [
        '○', '〔', '〜', '、', '「', 'を除く', '以外', 'その他',
        '地割', '不明', '以下に掲載がない場合']

    # 町域の () 内に除外文字列があるか確認
    if '(' in entry[8]:
        kakko = ''.join(entry[8].split('(')[1:])

        for c in range(len(str_ng)):
            if str_ng[c] in kakko:
                # マッチする場合は町域の読みと表記の「(」以降を削除
                entry[5] = entry[5].split('(')[0]
                entry[8] = entry[8].split('(')[0]
                break

    # 町域の () 外に除外文字列があるか確認
    for c in range(len(str_ng)):
        if str_ng[c] in entry[8]:
            # マッチする場合は町域の読みと表記を空にする
            entry[5] = ''
            entry[8] = ''
            break

    # 町域の読みの () を取る
    #     'ハラ(ゴクラクザカ)','原(極楽坂)' を
    #     'ハラゴクラクザカ','原(極楽坂)' にする。
    #     表記の () は取らない。「原極楽坂」だと読みにくいので。
    entry[5] = entry[5].replace('(', '').replace(')', '')

    with open(dict_name, 'a', encoding='utf-8') as dict_file:
        dict_file.write(','.join(entry) + '\n')
