#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import bz2
import csv
import html
import io
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from unicodedata import normalize
from zipfile import ZipFile


def main():
    if len(sys.argv) == 1:
        print('No file specified.')
        sys.exit()

    file_ut = sys.argv[1]
    ut_entry = get_ut_entry(file_ut)
    mozc_entry, id_mozc = get_mozc_entry()

    ut_entry = remove_duplicate(mozc_entry, ut_entry)
    jawiki_hit_dict = generate_jawiki_hit_dict()
    ut_entry = apply_jawiki_hit(ut_entry, jawiki_hit_dict)

    with open(file_ut, 'w', encoding='utf-8') as file:
        for entry in ut_entry:
            entry[1] = entry[2] = id_mozc
            file.write(f'{'\t'.join(entry)}\n')


def get_ut_entry(file_ut):
    ut_entry = []

    with open(file_ut, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')

        for row in reader:
            yomi, id1, id2, cost, hyouki = row

            # 不要な表記をスキップ
            hyouki = remove_short_or_long_hyouki(hyouki)
            if not hyouki:
                continue

            # 表記を正規化
            hyouki = normalize_entry(hyouki)

            # ID はソートしたとき Mozc エントリより後になるものにする
            id1 = id2 = 'id_ut'

            ut_entry.append([yomi, id1, id2, cost, hyouki])

    return ut_entry


def get_mozc_entry():
    # Mozc の最終コミット日を取得
    url = 'https://api.github.com/repos/google/mozc/commits/master'

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        date_str = data['commit']['committer']['date']

    date_str = datetime.fromisoformat(date_str)
    date_str = date_str.strftime('%Y%m%d')

    # Mozc のアーカイブを取得
    url = 'https://github.com/google/mozc/archive/refs/heads/master.zip'

    if not Path(f'mozc-{date_str}.zip').exists():
        urllib.request.urlretrieve(
                url, f'mozc-{date_str}.zip')

    with ZipFile(f'mozc-{date_str}.zip') as zip_ref:
        # 一般名詞の ID を取得
        with zip_ref.open(
                'mozc-master/src/data/dictionary_oss/id.def') as file:
            for line in file:
                line = line.decode()

                if ' 名詞,一般,' in line:
                    id_mozc = line.split(' 名詞,一般,')[0]
                    break

        # Mozc 辞書のファイルリストを取得
        all_files = zip_ref.namelist()
        dict_path = 'mozc-master/src/data/dictionary_oss/dictionary0'
        dict_files = [f for f in all_files if f.startswith(dict_path)]

        # Mozc 辞書のエントリを取得
        mozc_entry = []

        for dict_file in dict_files:
            with zip_ref.open(dict_file) as file:
                # バイナリストリームをテキストストリームに変換
                file_text = io.TextIOWrapper(file, encoding='utf-8')
                reader = csv.reader(file_text, delimiter='\t')
                mozc_entry.extend(list(reader))

        mozc_entry_mod = []

        for entry in mozc_entry:
            yomi, id1, id2, cost, hyouki = entry[:5]

            # 不要な表記をスキップ
            hyouki = remove_short_or_long_hyouki(hyouki)
            if not hyouki:
                continue

            # 表記を正規化
            hyouki = normalize_entry(hyouki)

            mozc_entry_mod.append([yomi, id1, id2, cost, hyouki])

    return mozc_entry_mod, id_mozc


def remove_duplicate(mozc_entry, ut_entry):
    all_entry = mozc_entry + ut_entry
    mozc_entry = []
    ut_entry = []

    # yomi -> hyouki -> id1 の優先順でソート
    all_entry.sort(key=lambda x: (x[0], x[4], x[1]))
    prev_key = ()

    for entry in all_entry:
        yomi, id1, id2, cost, hyouki = entry
        current_key = (yomi, hyouki)

        # 重複する UT エントリを削除
        if id1 == 'id_ut' and prev_key != current_key:
            ut_entry.append(entry)

        prev_key = current_key

    return ut_entry


def generate_jawiki_hit_dict():
    # jawiki-*-multistream-index.txt.bz2 を取得
    url = 'https://dumps.wikimedia.org/jawiki/latest/' + \
        'jawiki-latest-pages-articles-multistream-index.txt.bz2-rss.xml'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        Chrome/91.0.4472.124"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            root = ET.fromstring(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f'Error: {e.code}')

    description_text = root.find('.//item/description').text
    url = re.search(r'href="([^"]+)"', description_text).group(1)

    jawiki_index_file = url.rsplit('/', 1)[1]

    if not Path(jawiki_index_file).exists():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, \
                    open(jawiki_index_file, "wb") as out_file:
                # 1MB ずつ書き込む
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out_file.write(chunk)
        except urllib.error.HTTPError as e:
            print(f'Error: {e.code}')

    jawiki_index = []

    with bz2.open(jawiki_index_file, 'rt', encoding='utf-8') as file:
        entry_to_skip = (
            'ファイル:', 'Wikipedia:', 'Template:', 'Portal:',
            'Help:', 'Category:', 'プロジェクト:', '曖昧さ回避')

        for entry in file:
            # 1004375:312:数学\n
            entry = entry.rstrip()
            entry = entry.split(':', 2)[2]

            # HTML特殊文字を変換
            entry = html.unescape(entry)

            # 「BEST (三浦大知のアルバム)」を
            # 「三浦大知のアルバム)」に変更。
            # 「三浦大知」を前方一致検索できるようにする
            entry = entry.split(' (')[-1]

            # 不要な表記をスキップ
            entry = remove_short_or_long_hyouki(entry)
            if not entry or \
                    entry.startswith(entry_to_skip):
                continue

            # 表記を正規化
            entry = normalize_entry(entry)

            jawiki_index.append(entry)

    # 重複を削除してリストに戻してソート
    jawiki_index = sorted(list(set(jawiki_index)))

    jawiki_hit_dict = {}
    i = 0
    jawiki_index_len = len(jawiki_index)

    while i < jawiki_index_len:
        jawiki_entry = jawiki_index[i]
        c = 1

        # 前方一致するエントリがなくなるまでカウント
        while i + c < jawiki_index_len and \
                jawiki_index[i + c].startswith(jawiki_entry):
            c = c + 1

        jawiki_hit_dict[jawiki_entry] = c
        i += 1

    return jawiki_hit_dict


def apply_jawiki_hit(ut_entry, jawiki_hit_dict):
    ut_entry_mod = []

    for entry in ut_entry:
        yomi, id1, id2, cost, hyouki = entry
        cost = int(cost)
        jawiki_hit_count = jawiki_hit_dict.get(hyouki, 0)

        # 最大ヒット数を抑制する
        jawiki_hit_count = min(jawiki_hit_count, 30)
        is_ascii = hyouki.isascii()

        # 英数字のみの表記で、
        # jawiki のヒット数が 0 の場合はスキップ
        # jawiki のヒット数が 1 以上の場合はコストを 9000 台にする
        if is_ascii:
            if jawiki_hit_count == 0:
                continue
            else:
                cost = 9000 + (cost // 20)
        # 英数字以外を含む表記で、
        # jawiki のヒット数が 0 の場合はコストを 9000 台にする
        # jawiki のヒット数が 1 の場合はコストを 8000 台にする
        # jawiki のヒット数が 2 以上の場合はコストを 7000 台にする
        elif jawiki_hit_count == 0:
            cost = 9000 + (cost // 20)
        elif jawiki_hit_count == 1:
            cost = 8000 + (cost // 20)
        else:
            cost = 8000 - (jawiki_hit_count * 10)

        ut_entry_mod.append([yomi, id1, id2, str(cost), hyouki])

    ut_entry = ut_entry_mod
    ut_entry_mod = []
    ut_entry.sort()
    return ut_entry


def remove_short_or_long_hyouki(hyouki):
    # 表記が1文字の場合はスキップ
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    len_hyouki = len(hyouki)
    if len_hyouki < 2 or len_hyouki > 25:
        hyouki = None

    return hyouki


def normalize_entry(entry):
    entry = normalize('NFKC', entry)
    entry = entry.replace('~', '〜')
    return entry


if __name__ == '__main__':
    main()
