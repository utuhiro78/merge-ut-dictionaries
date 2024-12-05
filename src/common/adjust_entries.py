#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import jaconv
import re
import sys
from unicodedata import normalize

args = sys.argv[1:]

if not args:
    print('No file specified.')
    sys.exit()

file_name = args[0]

with open(file_name, 'r', encoding='utf-8') as file:
    lines = file.read().splitlines()

l2 = []

for i in range(len(lines)):
    entry = lines[i].split('\t')
    yomi = entry[0]
    hyouki = entry[4]

    # 表記の「~」を「〜」に置き換える
    hyouki = hyouki.replace('~', '〜')

    # 表記の全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)

    # 表記の最初が空白の場合は取る
    if hyouki[0] == ' ':
        hyouki = hyouki[1:]

    # 表記の全角カンマを半角に変換
    hyouki = hyouki.replace('，', ', ')

    # 表記の最後が空白の場合は取る（全角カンマが「, 」に変換されている）
    # 表記の最後が「。」の場合は取る
    if hyouki[-1] == ' ' or hyouki[-1] == '。':
        hyouki = hyouki[:-1]

    # 読みにならない文字「 !?」などを削除したhyouki_stripを作る
    hyouki_strip = hyouki.translate(str.maketrans('', '', ' .!?-+*=:/・。×★☆'))

    # hyouki_stripがひらがなとカタカナだけの場合は、読みをhyouki_stripから作る
    if hyouki_strip == ''.join(re.findall('[ぁ-ゔァ-ヴー]', hyouki_strip)):
        yomi = jaconv.kata2hira(hyouki_strip)
        yomi = yomi.translate(str.maketrans('ゐゑ', 'いえ'))

    # 読みが2文字以下の場合はスキップ
    # hyouki_stripが1文字の場合はスキップ
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    # hyouki_stripの1文字に対する読みが平均4文字を超える場合はスキップ
    #     「さくらざかふぉーてぃーしっくす[15文字] 櫻坂46[4文字]」までは残す
    # 読み1文字に対するhyouki_stripのバイト数が平均3バイトを超える場合はスキップ
    #     「あいてぃー[5文字] ITエンジニア[17bytes]」をスキップ
    # 読みがひらがな以外を含む場合はスキップ
    # 表記がコードポイントを含む場合はスキップ
    # 表記が「/」を含む場合はスキップ
    #     「ひかりのあと 光の跡/生命体」をスキップ
    if len(yomi) < 3 or \
            len(hyouki_strip) < 2 or \
            len(hyouki) > 25 or \
            len(yomi) / len(hyouki_strip) > 4 or \
            len(hyouki_strip.encode()) / len(yomi) > 3 or \
            yomi != ''.join(re.findall('[ぁ-ゔー]', yomi)) or \
            '\\u' in hyouki or \
            '/' in hyouki:
        continue

    # hyouki_stripに数字が3個以上ある場合はスキップ
    # ただし「100円ショップ」は残す
    n = re.findall(r'\d+', hyouki)

    if n != []:
        n = int(''.join(n))

        if n > 100:
            continue

    entry[0] = yomi
    entry[4] = hyouki
    l2.append('\t'.join(entry) + '\n')

lines = l2

with open(file_name, 'w', encoding='utf-8') as dict_file:
    dict_file.writelines(lines)
