#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import csv
import io
import jaconv
import re
import urllib.request
from pathlib import Path
from unicodedata import normalize
from zipfile import ZipFile

# ひらがなと長音にマッチ
RE_HIRAGANA = re.compile(r'[ぁ-ゔー]+')

# 「(」「)」を削除
TRANS_KAKKO = str.maketrans('', '', '・()')

# 1-59 の読みを生成
D1 = ['', 'いち', 'に', 'さん', 'よん', 'ご', 'ろく', 'なな', 'はち', 'きゅう']
D10 = ['', 'じゅう', 'にじゅう', 'さんじゅう', 'よんじゅう', 'ごじゅう']
YOMI_NUMS = [p + q for p in D10 for q in D1]


def main():
    place_dict = get_zipcode_file()

    with open('mozcdic-ut-place-names.txt', 'w', encoding='utf-8') as file:
        for entry in place_dict:
            entry = [entry[0], '0000', '0000', '9000', entry[1]]
            file.write(f'{"\t".join(entry)}\n')


def get_zipcode_file():
    Path('ken_all.zip').unlink(missing_ok=True)

    urllib.request.urlretrieve(
        'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip',
        'ken_all.zip')

    place_dict = set()

    with ZipFile('ken_all.zip') as zip_ref:
        with zip_ref.open('KEN_ALL.CSV') as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='sjis'))
            for row in reader:
                entry = generate_dict_entry(row)
                if entry:
                    place_dict.update(entry)

    place_dict = sorted(place_dict)

    return place_dict


def generate_dict_entry(entry):
    # 0 全国地方公共団体コード,1 旧郵便番号,2 郵便番号,
    # 3 都道府県名,4 市区町村名,5 町域名,
    # 6 都道府県名,7 市区町村名,8 町域名,

    # 01102,"060  ","0600812",
    # "ﾎｯｶｲﾄﾞｳ","ｻｯﾎﾟﾛｼｷﾀｸ","ｷﾀ12ｼﾞｮｳﾆｼ(5-12ﾁｮｳﾒ)",
    # "北海道","札幌市北区","北十二条西（５〜１２丁目）",

    shi_yomi, chou_yomi = entry[4], entry[5]
    shi_hyouki, chou_hyouki = entry[7], entry[8]

    # 半角を全角に変換
    shi_yomi = normalize('NFKC', shi_yomi)
    shi_yomi = jaconv.kata2hira(shi_yomi)
    chou_yomi = normalize('NFKC', chou_yomi)
    chou_hyouki = normalize('NFKC', chou_hyouki)

    # chou_hyouki に次の文字列が含まれている場合はスキップ
    ng_str = [
        '○', '〔', '〜', '、', '「', 'を除く', '以外', 'その他',
        '地割', '不明', '以下に掲載がない場合']

    # chou_hyouki の () 内に除外文字列があるか確認
    if '(' in chou_hyouki:
        chou_hyouki_part = chou_hyouki.rsplit('(', 1)

        if any(s in chou_hyouki_part[1] for s in ng_str):
            # マッチする場合は町域の読みと表記の「(」以降を削除
            chou_hyouki = chou_hyouki_part[0]
            chou_yomi = chou_yomi.rsplit('(', 1)[0]

    # chou_hyouki 全体に除外文字列があるか確認
    if any(s in chou_hyouki for s in ng_str):
        # マッチする場合は (shi_yomi, shi_hyouki) のみを返す
        return [(shi_yomi, shi_hyouki)]

    chou_yomi = update_chou_yomi(chou_yomi)
    if not chou_yomi:
        return None

    # 市のエントリを作成
    entry_mod = [(shi_yomi, shi_hyouki)]

    # 町のエントリを作成
    entry_mod.append((chou_yomi, chou_hyouki))

    # 市+町のエントリを作成
    entry_mod.append((shi_yomi + chou_yomi, shi_hyouki + chou_hyouki))

    return entry_mod


def update_chou_yomi(chou_yomi):
    # 読みをひらがなに変換
    chou_yomi = jaconv.kata2hira(chou_yomi)

    # chou_yomi の「・」「(」「)」を取る
    #     'ハラ(ゴクラクザカ)','原(極楽坂)' を
    #     'ハラゴクラクザカ','原(極楽坂)' にする。
    #     chou_hyouki の () は取らない。「原極楽坂」になるので。
    chou_yomi = chou_yomi.translate(TRANS_KAKKO)

    # chou_yomi が半角数字を含むか確認
    #     サッポロシヒガシクキタ51ジョウヒガシ
    c = ''.join(filter(str.isdigit, chou_yomi))

    # chou_yomi の半角数字が 60 未満の場合はひらがなに変換
    #     さっぽろしひがしくきた51じょうひがし
    if c and 0 < int(c) < 60:
        chou_yomi = chou_yomi.replace(c, YOMI_NUMS[int(c)])

    # chou_yomi がひらがな以外を含む場合はスキップ
    #     OAPたわー
    if not RE_HIRAGANA.fullmatch(chou_yomi):
        return None

    return chou_yomi


if __name__ == '__main__':
    main()
