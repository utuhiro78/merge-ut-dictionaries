#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import csv
import io
import jaconv
import os
import re
import urllib.request
from zipfile import ZipFile

# ひらがなと長音のいずれか1文字にマッチ
RE_HIRAGANA = re.compile(r'[ぁ-ゔー]')

# 「=」「・」を削除
TRANS_NON_YOMI = str.maketrans('', '', '=・')
# 「ゐ」「ゑ」を「い」「え」に置換
TRANS_OLD_I_E = str.maketrans('ゐゑ', 'いえ', '')


def main():
    url = 'http://sudachi.s3-website-ap-northeast-1.amazonaws.com/' + \
            'sudachidict-raw/'

    with urllib.request.urlopen(url) as response:
        html = response.read().decode()

    # <a href='20250825/small_lex.zip'>
    date = html.split('/small_lex.zip')[0].split('\'')[-1]

    sudachidict = []
    base_name = ['small', 'core', 'notcore']
    for entry in base_name:
        zip_file = f'{entry}_lex_{date}.zip'
        sudachidict.extend(get_sudachi_file(zip_file, url, date))

    sudachidict = remove_duplicate(sudachidict)

    with open('mozcdic-ut-sudachidict.txt', 'w', encoding='utf-8') as file:
        for entry in sudachidict:
            file.write(f'{"\t".join(entry)}\n')


def get_sudachi_file(zip_file, url, date):
    # 'small_lex_20250825.zip' -> 'small_lex'
    file_orig = zip_file.rsplit('_', 1)[0]

    if os.path.exists(zip_file) is False:
        urllib.request.urlretrieve(
                f'{url}{date}/{file_orig}.zip', zip_file)

    sudachidict = []

    with ZipFile(zip_file) as zip_ref:
        with zip_ref.open(f'{file_orig}.csv') as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8'))
            for row in reader:
                row = generate_dict_entry(row)
                if row:
                    sudachidict.append(row)

    return sudachidict


def generate_dict_entry(entry):
    # 0 見出し (TRIE 用),1 左連接ID,2 右連接ID,3 コスト
    # 4 見出し (解析結果表示用),5 品詞1,6 品詞2,7 品詞3
    # 8 品詞4,9 品詞 (活用型),10 品詞 (活用形),11 読み
    # 8 12 正規化表記,13 辞書形ID,14 分割タイプ,15 A単位分割情報,
    # 16 B単位分割情報,17 ※未使用

    # 6角,5146,5146,4005,
    # 6角,名詞,普通名詞,一般,
    # *,*,*,ロッカク,
    # 六角,*,A,*,
    # *,*,*

    id1, id3, id4 = entry[5], entry[7], entry[8]
    yomi, hyouki = entry[11], entry[12]
    yomi = yomi.translate(TRANS_NON_YOMI)

    # 2文字以下の読みをスキップ
    # 1文字以下の表記をスキップ
    # 名詞以外をスキップ
    # 地名をスキップ
    #     地名は郵便番号データから作成する。
    # 「人名,名」をスキップ
    #     「科学（すすむ）」のような当て読みがあるので。
    if len(yomi) < 3 or \
            len(hyouki) < 2 or \
            id1 != '名詞' or \
            id3 == '地名' or \
            (id3 == '人名' and id4 == '名'):
        return None

    # 読みのカタカナをひらがなに変換
    yomi = convert_to_hiragana(yomi)

    # 読みがひらがな以外を含む場合はスキップ
    if yomi != collect_hiragana(yomi):
        return None

    cost = int(entry[3])
    # 0 から 9999 の範囲に収める
    cost = max(0, min(cost, 9999))

    # 全体のコストを 8000 台にする
    cost = 8000 + (cost // 10)

    return [yomi, cost, hyouki]


def remove_duplicate(sudachidict):
    # yomi -> hyouki -> cost の優先順でソート
    sudachidict.sort(key=lambda x: (x[0], x[2], x[1]))
    sudachidict_mod = []
    prev_key = ()

    for entry in sudachidict:
        yomi, cost, hyouki = entry
        current_key = (yomi, hyouki)

        # 重複する UT エントリを削除
        # Mozc 形式のエントリを作成
        if prev_key != current_key:
            entry = [yomi, '0000', '0000', str(cost), hyouki]
            sudachidict_mod.append(entry)

        prev_key = current_key

    return sudachidict_mod


def convert_to_hiragana(entry):
    entry = jaconv.kata2hira(entry)
    entry = entry.translate(TRANS_OLD_I_E)
    return entry


def collect_hiragana(entry):
    entry = ''.join(RE_HIRAGANA.findall(entry))
    return entry


if __name__ == '__main__':
    main()
