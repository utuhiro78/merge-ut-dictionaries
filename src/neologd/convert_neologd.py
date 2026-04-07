#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import csv
import io
import jaconv
import lzma
import re
import urllib.request
from pathlib import Path

# ひらがなと長音にマッチ
RE_HIRAGANA = re.compile(r'[ぁ-ゔー]+')

# 「=」「・」を削除
TRANS_NON_YOMI = str.maketrans('', '', '=・')
# 「ゐ」「ゑ」を「い」「え」に置換
TRANS_OLD_I_E = str.maketrans('ゐゑ', 'いえ', '')


def main():
    url = 'https://github.com/neologd/mecab-ipadic-neologd/tree/master/seed'
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')

    neologd_ver = html.split('mecab-user-dict-seed.')[1]
    neologd_ver = neologd_ver.split('.csv.xz')[0]
    neologd_file = f'mecab-user-dict-seed.{neologd_ver}.csv.xz'

    if not Path(neologd_file).exists():
        url = 'https://github.com/neologd/mecab-ipadic-neologd/raw/refs/' + \
            f'heads/master/seed/{neologd_file}'
        urllib.request.urlretrieve(url)

    neologd_dict = []

    with lzma.open(neologd_file) as xz_ref:
        reader = csv.reader(io.TextIOWrapper(xz_ref, encoding='utf-8'))
        for row in reader:
            row = generate_dict_entry(row)
            if row:
                neologd_dict.append(row)

    neologd_dict = remove_duplicate(neologd_dict)

    with open('mozcdic-ut-neologd.txt', 'w', encoding='utf-8') as file:
        for entry in neologd_dict:
            file.write(f'{"\t".join(entry)}\n')


def generate_dict_entry(entry):
    # https://taku910.github.io/mecab/dic.html
    # 0 表層形,1 左文脈ID,2 右文脈ID,3 コスト,
    # 4 品詞1,5 品詞2,6 品詞3,7 品詞4,
    # 8 品詞5,9 品詞6,10 原形,11 読み,
    # 12 発音

    # ihi corporation,1292,1292,5893,
    # 名詞,固有名詞,組織,*,
    # *,*,IHI,アイエイチアイ,
    # アイエイチアイ

    id1, id3, id4 = entry[4], entry[6], entry[7]
    yomi, hyouki = entry[11], entry[10]
    yomi = yomi.translate(TRANS_NON_YOMI)

    # 2文字以下の読みをスキップ
    # 1文字以下の表記をスキップ
    # 名詞以外をスキップ
    # 地域をスキップ
    #     地名は郵便番号データから作成する。
    # 「人名,名」をスキップ
    #     数が膨大で候補が増えすぎる。
    if len(yomi) < 3 or \
            len(hyouki) < 2 or \
            id1 != '名詞' or \
            id3 == '地域' or \
            (id3 == '人名' and id4 == '名'):
        return None

    # 読みのカタカナをひらがなに変換
    yomi = convert_to_hiragana(yomi)

    # 読みがひらがな以外を含む場合はスキップ
    if not RE_HIRAGANA.fullmatch(yomi):
        return None

    cost = int(entry[3])
    # 0 から 9999 の範囲に収める
    cost = max(0, min(cost, 9999))

    # 全体のコストを 8000 台にする
    cost = 8000 + (cost // 10)

    return [yomi, cost, hyouki]


def remove_duplicate(neologd_dict):
    # yomi -> hyouki -> cost の優先順でソート
    neologd_dict.sort(key=lambda x: (x[0], x[2], x[1]))
    neologd_dict_mod = []
    prev_key = ()

    for entry in neologd_dict:
        yomi, cost, hyouki = entry
        current_key = (yomi, hyouki)

        # 重複する UT エントリを削除
        # Mozc 形式のエントリを作成
        if prev_key != current_key:
            entry = [yomi, '0000', '0000', str(cost), hyouki]
            neologd_dict_mod.append(entry)

        prev_key = current_key

    return neologd_dict_mod


def convert_to_hiragana(entry):
    entry = jaconv.kata2hira(entry)
    entry = entry.translate(TRANS_OLD_I_E)
    return entry


if __name__ == '__main__':
    main()
