#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import bz2
import html
import os
import subprocess
import sys
import urllib.request
from unicodedata import normalize
from zipfile import ZipFile


def main():
    if len(sys.argv) == 1:
        print('No file specified.')
        sys.exit()

    file_ut = sys.argv[1]
    ut_dic = get_ut_dic(file_ut)

    mozc_dic = get_mozc_dic()
    id_mozc = mozc_dic[-1]
    mozc_dic = ut_dic + mozc_dic[:-1]

    ut_dic = remove_duplicates(mozc_dic)
    ut_dic += count_word_hits()

    ut_dic.append(id_mozc)
    ut_dic = apply_word_hits(ut_dic)

    with open(file_ut, 'w', encoding='utf-8') as file:
        file.writelines(ut_dic)


def get_ut_dic(file_ut):
    with open(file_ut, 'r', encoding='utf-8') as file:
        ut_dic = file.read().splitlines()

    # UT辞書のIDを 'id' にする
    for i in range(len(ut_dic)):
        entry = ut_dic[i].split('\t')
        entry[1] = entry[2] = 'id'
        ut_dic[i] = '\t'.join(entry)

    return (ut_dic)


def get_mozc_dic():
    # Mozc の最終コミット日を取得
    url = 'https://github.com/google/mozc/commits/master/'

    with urllib.request.urlopen(url) as response:
        date = response.read().decode()
        date = date.split('"committedDate":"')[1]
        date = date[:10]
        date = date.replace('-', '')

    # Mozc のアーカイブが古い場合は取得
    url = 'https://github.com/google/mozc/archive/refs/heads/master.zip'

    if os.path.exists(f'mozc-{date}.zip') is False:
        urllib.request.urlretrieve(
                url, f'mozc-{date}.zip')

    with ZipFile(f'mozc-{date}.zip') as zip_ref:
        # 一般名詞のIDを取得
        with zip_ref.open(
                'mozc-master/src/data/dictionary_oss/id.def') as file:
            id_mozc = file.read().decode()
            id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]

        # Mozc 公式辞書を取得
        mozc_dic = []

        for i in range(10):
            with zip_ref.open(
                    'mozc-master/src/data/dictionary_oss/' +
                    f'dictionary0{i}.txt') as file:
                mozc_dic += file.read().decode().splitlines()

    mozc_dic.append(id_mozc)
    return (mozc_dic)


def remove_duplicates(mozc_dic):
    for i in range(len(mozc_dic)):
        # 並び順を [読み, 表記, ID, ID, コスト] にする
        entry = mozc_dic[i].split('\t')
        entry.insert(1, entry[4])
        mozc_dic[i] = entry[:5]

    mozc_dic.sort()
    ut_dic = []

    for i in range(len(mozc_dic)):
        # あいおい\t相生\t1851\t433\t7582
        # あいおい\t相生\tid\tid\t8200
        # あいおい\t相生\tid\tid\t8400

        # Mozc 公式辞書をスキップ
        # 公式辞書と [読み, 表記] が重複するUTエントリをスキップ
        # UT辞書内で [読み, 表記] が重複するエントリをスキップ
        if mozc_dic[i][2] != 'id' or \
                mozc_dic[i][:2] == mozc_dic[i - 1][:2]:
            continue

        ut_dic.append(mozc_dic[i])

    mozc_dic = []

    for i in range(len(ut_dic)):
        # Mozc 辞書の並びに戻す
        ut_dic[i].append(ut_dic[i][1])
        ut_dic[i].pop(1)

    return (ut_dic)


def count_word_hits():
    subprocess.run(
        ['wget', '-N', 'https://dumps.wikimedia.org/jawiki/latest/' +
            'jawiki-latest-pages-articles-multistream-index.txt.bz2'],
        check=True)

    with bz2.open(
            'jawiki-latest-pages-articles-multistream-index.txt.bz2',
            'rt', encoding='utf-8') as file:
        lines = file.read().splitlines()

    l2 = []

    for line in lines:
        # 1004375:312:数学
        line = ':'.join(line.split(':')[2:])

        # 表記のHTML特殊文字を変換
        line = html.unescape(line)

        # 「BEST (三浦大知のアルバム)」を
        # 「三浦大知のアルバム)」に変更。
        # 「三浦大知」を前方一致検索できるようにする
        line = line.split(' (')[-1]

        # 表記が1文字の場合はスキップ
        # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
        # 内部用のページをスキップ
        if len(line) < 2 or \
                len(line) > 25 or \
                line.startswith('ファイル:') or \
                line.startswith('Wikipedia:') or \
                line.startswith('Template:') or \
                line.startswith('Portal:') or \
                line.startswith('Help:') or \
                line.startswith('Category:') or \
                line.startswith('プロジェクト:'):
            continue

        l2.append(line)

    lines = sorted(list(set(l2)))
    l2 = []

    lines_len = len(lines)

    for i in range(lines_len):
        c = 1

        # 前方一致するエントリがなくなるまでカウント
        while i + c < lines_len and lines[i + c].startswith(lines[i]):
            c = c + 1

        entry = ['jawiki_hits', '0', '0', str(c), lines[i]]
        l2.append(entry)

    return (l2)


def apply_word_hits(lines):
    id_mozc = lines[-1]
    lines = lines[:-1]

    for i in range(len(lines)):
        # 表記の「~」を「〜」に置き換える
        lines[i][4] = lines[i][4].replace('~', '〜')

        # 表記を正規化
        lines[i][4] = normalize('NFKC', lines[i][4])

        # 表記を先頭にする
        lines[i].insert(0, lines[i][4])
        lines[i] = lines[i][0:5]

    lines.sort()
    l2 = []

    for line in lines:
        line[4] = int(line[4])

        if line[1] == 'jawiki_hits':
            line_jawiki = line

            # jawiki のヒット数を最大 30 にする
            if line_jawiki[4] > 30:
                line_jawiki[4] = 30

            continue

        # 英数字のみの表記で jawiki に存在しないものはスキップ
        # 存在する場合はコストを 9000 台にする
        if len(line[0]) == len(line[0].encode()):
            if line[0] != line_jawiki[0]:
                continue
            else:
                line[4] = str(9000 + (line[4] // 20))
        # 英数字以外を含む表記で jawiki に存在しないものはコストを 9000 台にする
        elif line[0] != line_jawiki[0]:
            line[4] = str(9000 + (line[4] // 20))
        # jawiki のヒット数が 1 の表記はコストを 8000 台にする
        elif line_jawiki[4] == 1:
            line[4] = str(8000 + (line[4] // 20))
        # jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
        else:
            line[4] = str(8000 - (line_jawiki[4] * 10))

        # Mozc の並びに戻す
        line.append(line[0])
        line = line[1:]
        # IDを更新
        line[1] = line[2] = id_mozc
        l2.append('\t'.join(line) + '\n')

    l2.sort()
    return (l2)


if __name__ == '__main__':
    main()
