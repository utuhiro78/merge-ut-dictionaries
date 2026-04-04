#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import jaconv
import re
import sys
from unicodedata import normalize

# ひらがなとカタカナと長音のいずれか1文字にマッチ
RE_HIRAGANA_KATAKANA = re.compile(r'[ぁ-ゔァ-ヴー]+')
# ひらがなと長音のいずれか1文字にマッチ
RE_HIRAGANA = re.compile(r'[ぁ-ゔー]+')

TRANS_NON_YOMI = str.maketrans('', '', ',.!?-+*=:・、。×★☆')
TRANS_OLD_I_E = str.maketrans('ゐゑ', 'いえ', '')


def main():
    args = sys.argv[1:]

    if not args:
        print('No file specified.')
        sys.exit()

    file_name = args[0]

    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()

    lines_mod = []

    for entry in lines:
        entry = entry.split('\t')
        yomi = entry[0]
        hyouki = entry[4]

        hyouki = modify_hyouki(hyouki)
        entry[0], entry[4] = remove_unnecessary_entry(yomi, hyouki)
        if entry[0]:
            lines_mod.append(f'{"\t".join(entry)}\n')

    lines = lines_mod

    with open(file_name, 'w', encoding='utf-8') as dict_file:
        dict_file.writelines(lines)


def modify_hyouki(hyouki):
    # 表記の「~」を「〜」に置き換える
    hyouki = hyouki.replace('~', '〜')

    # 表記の全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)

    # 表記の最初が空白の場合は取る
    if hyouki.startswith(' '):
        hyouki = hyouki[1:]

    # 表記の全角カンマを半角に変換
    hyouki = hyouki.replace('，', ', ')

    # 表記の最後が空白の場合は取る（全角カンマが「, 」に変換されている）
    # 表記の最後が「。」の場合は取る
    if hyouki.endswith(' ') or hyouki.endswith('。'):
        hyouki = hyouki[:-1]

    return hyouki


def remove_unnecessary_entry(yomi, hyouki):
    # 読みにならない文字を削除して hyouki_strip を作る
    hyouki_strip = hyouki.translate(TRANS_NON_YOMI)

    # hyouki_strip がひらがなカタカナのみの場合は、
    # 読みを hyouki_strip から作る
    #     さいたまスーパーアリーナ
    if RE_HIRAGANA_KATAKANA.fullmatch(hyouki_strip):
        yomi = convert_to_hiragana(hyouki_strip)

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
            not RE_HIRAGANA.fullmatch(yomi) or \
            '\\u' in hyouki or \
            '/' in hyouki:
        return None, None

    # hyouki_stripに数字が3個以上ある場合はスキップ
    # ただし「100円ショップ」は残す
    nums = ''.join(re.findall(r'\d+', hyouki))
    if nums and int(nums) > 100:
        return None, None

    return yomi, hyouki


def convert_to_hiragana(entry):
    entry = jaconv.kata2hira(entry)
    entry = entry.translate(TRANS_OLD_I_E)
    return entry


if __name__ == '__main__':
    main()
