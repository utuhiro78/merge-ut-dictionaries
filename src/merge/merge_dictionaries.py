#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import bz2
import html
import subprocess
import sys
import urllib.request
from unicodedata import normalize


def get_id_mozc():
    # Mozc の一般名詞のIDを取得
    url = 'https://raw.githubusercontent.com/' + \
            'google/mozc/master/src/data/dictionary_oss/id.def'

    with urllib.request.urlopen(url) as response:
        id_mozc = response.read().decode()

    id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]
    return (id_mozc)


def remove_duplicates(file_name):
    id_mozc = get_id_mozc()

    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()

    for i in range(len(lines)):
        entry = lines[i].split('\t')

        # IDを更新
        entry[1:3] = [id_mozc, id_mozc]

        # 並び順を [読み, 表記, ID, ID, コスト] にする
        entry.insert(1, entry[4])
        lines[i] = entry[:5]

    lines.sort()
    l2 = []

    for i in range(len(lines)):
        # [読み, 表記] が重複するエントリのうち、コストが大きいものをスキップ
        #     あいおい    相生    1843    1843    8200
        #     あいおい    相生    1843    1843    8400
        if lines[i][0:2] == lines[i - 1][0:2]:
            continue

        entry = lines[i].copy()

        # Mozc 辞書の並びに戻す
        entry.append(entry[1])
        entry.pop(1)

        l2.append(entry)

    return (l2)


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
    for i in range(len(lines)):
        # 表記の「~」を「〜」に置き換える
        lines[i][4] = lines[i][4].replace('~', '〜')

        # 表記を正規化
        lines[i][4] = normalize('NFKC', lines[i][4])

        # 表記を先頭にする
        #     中居正広    jawiki_hits    0    0    34
        #     中居正広    なかいまさひろ    1843    1843    6477
        lines[i].insert(0, lines[i][4])
        lines[i] = lines[i][0:5]

    lines.sort()
    l2 = []

    for line in lines:
        line[4] = int(line[4])

        if line[1] == 'jawiki_hits':
            line_wiki = line

            # jawiki のヒット数を最大 30 にする
            if line_wiki[4] > 30:
                line_wiki[4] = 30

            continue

        # 英数字のみの表記で jawiki に存在しないものはスキップ
        # 存在する場合はコストを 9000 台にする
        if len(line[0]) == len(line[0].encode()):
            if line[0] != line_wiki[0]:
                continue
            else:
                line[4] = str(9000 + (line[4] // 20))
        # 英数字以外を含む表記で jawiki に存在しないものはコストを 9000 台にする
        elif line[0] != line_wiki[0]:
            line[4] = str(9000 + (line[4] // 20))
        # jawiki のヒット数が 1 の表記はコストを 8000 台にする
        elif line_wiki[4] == 1:
            line[4] = str(8000 + (line[4] // 20))
        # jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
        else:
            line[4] = str(8000 - (line_wiki[4] * 10))

        # Mozc の並びに戻す
        line.append(line[0])
        line = line[1:]
        l2.append('\t'.join(line) + '\n')

    l2.sort()
    return (l2)


def main():
    if len(sys.argv) == 1:
        print('No file specified.')
        sys.exit()

    file_name = sys.argv[1]

    lines = remove_duplicates(file_name)
    lines += count_word_hits()
    lines = apply_word_hits(lines)

    with open(file_name, 'w', encoding='utf-8') as file:
        file.writelines(lines)


if __name__ == '__main__':
    main()
