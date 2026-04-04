#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import gzip
import jaconv
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from unicodedata import normalize

# カタカナと長音のいずれか1文字にマッチ
RE_HIRAGANA_KATAKANA_CHR = re.compile(r'[ぁ-ゔァ-ヴー]')

# 「 」「=」「・」を削除
TRANS_NON_YOMI = str.maketrans('', '', ' =・')
# 「ゐ」「ゑ」を「い」「え」に置換
TRANS_OLD_I_E = str.maketrans('ゐゑ', 'いえ', '')


def main():
    url = 'http://ftp.edrdg.org/pub/Nihongo/edict2.gz'
    edict = get_edict_file(url)

    with open('mozcdic-ut-edict2.txt', 'w', encoding='utf-8') as file:
        for entry in edict:
            entry = [entry[0], '0000', '0000', '8000', entry[1]]
            file.write(f'{"\t".join(entry)}\n')


def get_edict_file(url):
    file = url.rsplit('/', 1)[1]
    current_date = datetime.now().strftime('%Y%m%d')

    file_part = file.split('.', 1)
    file = f'{file_part[0]}_{current_date}.{file_part[1]}'
    if not Path(file).exists():
        urllib.request.urlretrieve(url, file)

    edict = set()

    with gzip.open(file, 'rt', encoding='EUC-JP') as gz_file:
        for line in gz_file:
            entry = generate_dict_entry(line)
            if entry:
                edict.update(entry)

    edict = sorted(edict)

    return edict


def generate_dict_entry(entry):
    # エントリが全角スペースで始まる場合はスキップ
    # 名詞でない場合はスキップ
    #     １分;一分 [いっぷん] /(n)
    if entry[0] == '　' or \
            ' /(n' not in entry:
        return None

    entry = entry.split(' /(n', 1)[0]

    # 表記または読みが複数ある場合は、それぞれ最初のものだけを採用する
    #     暗唱;暗誦;諳誦 [あんしょう;あんじゅ(暗誦,諳誦)(ok)] /(n)
    #     ＨＤＤケース [エイチ・ディー・ディー・ケース /(n)
    if ' [' in entry:
        entry = entry.split(' [', 1)
        yomi, hyouki = entry[1], entry[0]
        yomi = yomi.split(']', 1)[0].split(';', 1)[0].split('(', 1)[0]
        hyouki = hyouki.split(';', 1)[0].split('(', 1)[0]
    # 読みが付与されていない場合は表記から読みを作る
    # 表記が複数ある場合は最初のものだけを採用する
    #     あいうえお;アイウエオ /(n)
    #     アイシャドウ(P);アイシャドー /(n)
    else:
        hyouki = entry.split(';', 1)[0].split('(', 1)[0]
        yomi = hyouki

    yomi = ''.join(RE_HIRAGANA_KATAKANA_CHR.findall(yomi))

    # 読みが2文字以下の場合はスキップ
    # 表記が1文字以下の場合はスキップ
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    if len(yomi) < 3 or \
            len(hyouki) < 2 or \
            len(hyouki) > 25:
        return None

    # 読みのカタカナをひらがなに変換
    yomi = jaconv.kata2hira(yomi)
    yomi = yomi.translate(TRANS_OLD_I_E)

    # 表記の全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)
    # 表記が半角英数のみの場合はスキップ
    if hyouki.isascii():
        return None

    return [(yomi, hyouki)]


if __name__ == '__main__':
    main()
