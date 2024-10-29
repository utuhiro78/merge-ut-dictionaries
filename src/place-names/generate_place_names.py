#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import jaconv
import re
import urllib.request
from unicodedata import normalize
from zipfile import ZipFile


def fix_ken_all():
    urllib.request.urlretrieve(
        'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip',
        'ken_all.zip')

    with ZipFile('ken_all.zip') as zip_ref:
        with zip_ref.open('KEN_ALL.CSV') as file:
            lines = file.read().decode('SJIS')

    lines = normalize('NFKC', lines)
    lines = lines.splitlines()
    l2 = []

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

        l2.append(','.join(entry))

    return (l2)


def generate_place_names(lines):
    # Mozc の一般名詞のIDを取得
    url = 'https://raw.githubusercontent.com/' + \
            'google/mozc/master/src/data/dictionary_oss/id.def'

    with urllib.request.urlopen(url) as response:
        id_mozc = response.read().decode()

    id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]

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

    with open('mozcdic-ut-place-names.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)


def main():
    lines = fix_ken_all()
    generate_place_names(lines)


if __name__ == '__main__':
    main()
