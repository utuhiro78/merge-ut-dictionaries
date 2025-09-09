#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import jaconv
import os
import re
import urllib.request
from zipfile import ZipFile


def main():
    lines = get_files()
    lines = generate_dict(lines)
    lines = remove_duplicates(lines)

    with open('mozcdic-ut-sudachidict.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)


def get_files():
    url = 'http://sudachi.s3-website-ap-northeast-1.amazonaws.com/' + \
            'sudachidict-raw/'

    with urllib.request.urlopen(url) as response:
        date = response.read().decode()
        date = date.split('/core_lex.zip')[0].split("'")[-1]

    if os.path.exists(f'small_lex_{date}.zip') is False:
        urllib.request.urlretrieve(
                f'{url}{date}/small_lex.zip', f'small_lex_{date}.zip')

    if os.path.exists(f'core_lex_{date}.zip') is False:
        urllib.request.urlretrieve(
                f'{url}{date}/core_lex.zip', f'core_lex_{date}.zip')

    if os.path.exists(f'notcore_lex_{date}.zip') is False:
        urllib.request.urlretrieve(
                f'{url}{date}/notcore_lex.zip', f'notcore_lex_{date}.zip')

    with ZipFile(f'small_lex_{date}.zip') as zip_ref:
        with zip_ref.open('small_lex.csv') as file:
            lines = file.read().decode()

    with ZipFile(f'core_lex_{date}.zip') as zip_ref:
        with zip_ref.open('core_lex.csv') as file:
            lines += file.read().decode()

    with ZipFile(f'notcore_lex_{date}.zip') as zip_ref:
        with zip_ref.open('notcore_lex.csv') as file:
            lines += file.read().decode()

    lines = lines.splitlines()
    return (lines)


def generate_dict(lines):
    l2 = []

    for i in range(len(lines)):
        # https://github.com/WorksApplications/Sudachi/blob/develop/docs/user_dict.md
        # 見出し (TRIE 用),左連接ID,右連接ID,コスト,\
        # 見出し (解析結果表示用),品詞1,品詞2,品詞3,品詞4,品詞 (活用型),品詞 (活用形),
        # 読み,正規化表記,辞書形ID,分割タイプ,A単位分割情報,B単位分割情報,※未使用

        # ihi corporation,4785,4785,5000,
        # ihi corporation,名詞,固有名詞,一般,*,*,*,
        # アイエイチアイ,IHI,*,A,*,*,*,*

        entry = lines[i].split(',')

        # 「読み」を読みにする
        yomi = entry[11].replace('=', '')
        yomi = yomi.replace('・', '')

        # 「正規化表記」を表記にする
        hyouki = entry[12]

        # 2文字以下の読みをスキップ
        # 1文字以下の表記をスキップ
        # 名詞以外をスキップ
        # 地名をスキップ
        #     地名は郵便番号データから作成する。
        # 「人名,名」をスキップ
        #     「科学（すすむ）」のような当て読みがあるので。
        if len(yomi) < 3 or \
                len(hyouki) < 2 or \
                entry[5] != '名詞' or \
                entry[7] == '地名' or \
                (entry[7] == '人名' and entry[8] == '名'):
            continue

        # 読みのカタカナをひらがなに変換
        yomi = convert_to_hiragana(yomi)

        # 読みがひらがな以外を含む場合はスキップ
        if yomi != collect_hiragana(yomi):
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

    return (l2)


def remove_duplicates(lines):
    lines.sort()
    l2 = []

    for i in range(len(lines)):
        entry1 = lines[i].split('\t')
        entry2 = lines[i - 1].split('\t')

        # [読み, 表記] が重複するエントリをスキップ
        if entry1[0:2] == entry2[0:2]:
            continue

        # Mozc 辞書の並びに変更
        entry1 = [entry1[0], '0000', '0000', entry1[2], entry1[1]]
        l2.append('\t'.join(entry1) + '\n')

    return (l2)


def convert_to_hiragana(entry):
    entry = jaconv.kata2hira(entry)
    entry = entry.translate(str.maketrans('ゐゑ', 'いえ', ''))
    return (entry)


def collect_hiragana(entry):
    entry = ''.join(re.findall('[ぁ-ゔー]', entry))
    return (entry)


if __name__ == '__main__':
    main()
