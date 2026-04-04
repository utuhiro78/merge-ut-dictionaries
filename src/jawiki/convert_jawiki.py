#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import bz2
import html
import jaconv
import multiprocessing
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from unicodedata import normalize

# 「}}'''」にマッチ
RE_TEMPLATE_END_AND_BOLD = re.compile(r'\}\}(?=\'\'\'|「|『)')
# 「{{...}}」にマッチ
RE_TEMPLATE = re.compile(r'{{.*?}}')
# 「<ref .../>」と「<ref>...</ref>」にマッチ
RE_REF = re.compile(r'<ref.*?(/>|>.*?</ref>)', re.DOTALL)
# 「)、/{\[,」のいずれか1文字にマッチ
RE_YOMI_KUGIRI = re.compile(r'[)、/{\[,]')

# ひらがなとカタカナと長音にマッチ
RE_HIRAGANA_KATAKANA = re.compile(r'[ぁ-ゔァ-ヴー]+')
# カタカナと長音にマッチ
RE_KATAKANA = re.compile(r'[ァ-ヴー]+')

# 「 \'"「」『』」を削除
TRANS_KAKKO = str.maketrans('', '', ' \'"「」『』')
# 「,.!?-+*=:・、。×★☆」を削除
TRANS_NON_YOMI = str.maketrans('', '', ',.!?-+*=:・、。×★☆')
# 「ゐ」「ゑ」を「い」「え」に置換
TRANS_OLD_I_E = str.maketrans('ゐゑ', 'いえ', '')


def main():
    jawiki_dict = generate_jawiki_dict()

    with open('mozcdic-ut-jawiki.txt', 'w', encoding='utf-8') as file:
        for entry in jawiki_dict:
            entry = f'{entry[0]}\t0000\t0000\t8000\t{entry[1]}\n'
            file.write(entry)


def generate_jawiki_dict():
    # jawiki-*-articles-multistream.xml.bz2 を取得
    url = 'https://dumps.wikimedia.org/jawiki/latest/' + \
        'jawiki-latest-pages-articles-multistream.xml.bz2-rss.xml'

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

    jawiki_articles_file = url.rsplit('/', 1)[1]

    if not Path(jawiki_articles_file).exists():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, \
                    open(jawiki_articles_file, "wb") as out_file:
                # 1MB ずつ書き込む
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out_file.write(chunk)
        except urllib.error.HTTPError as e:
            print(f'Error: {e.code}')

    # Wikipedia のダンプを読み込む
    jawiki_dict = []
    c = 0

    # プロセスプールを作成
    with multiprocessing.Pool() as pool:
        for result in pool.imap(
                get_dict_entry,
                get_jawiki_article(jawiki_articles_file),
                chunksize=100):
            if result:
                jawiki_dict.append(result)
                if c % 1000 == 0:
                    print(f'{c}: {result}')

                c += 1

    # 重複するエントリを削除
    jawiki_dict = sorted(list(set(jawiki_dict)))
    return jawiki_dict


def get_jawiki_article(jawiki_articles_file):
    with bz2.open(jawiki_articles_file, 'rt', encoding='utf-8') as file:
        context = ET.iterparse(file, events=('start', 'end'))
        event, root = next(context)

        try:
            for event, elem in context:
                if event == 'end' and elem.tag.endswith('page'):
                    title = elem.findtext('{*}title')
                    text_elem = elem.find('{*}revision/{*}text')
                    article = text_elem.text or ""
                    yield (title, article)
                    elem.clear()
                    root.clear()

        except ET.ParseError:
            yield ('', '')


def get_dict_entry(data):
    title, article = data

    hyouki = get_hyouki(title)
    if not hyouki:
        return None

    yomi = get_yomi(hyouki, article)
    if not yomi:
        return None

    return (yomi, hyouki)


def get_hyouki(title):
    # title を最後の「 (」で切って表記にする
    #     スティル・ライフ (ローリング・ストーンズのアルバム)
    hyouki = title.rsplit(' (', 1)[0]

    # 表記にスペースがある場合はスキップ
    #     記事のスペースを削除して「表記(読み)」を検索するので。
    # 表記に「、」がある場合はスキップ
    #     「明日、キミと」などが1語として変換されてしまうので。
    if ' ' in hyouki or \
            '、' in hyouki:
        return None

    hyouki = remove_short_or_long_hyouki(hyouki)
    if not hyouki:
        return None

    # 全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)

    # HTMLの特殊文字を変換
    hyouki = html.unescape(hyouki)

    return hyouki


def get_yomi(hyouki, article):
    # 読みにならない文字を削除して hyouki_strip を作る
    hyouki_strip = hyouki.translate(TRANS_NON_YOMI)

    # hyouki_strip が1文字以下の場合はスキップ
    if len(hyouki_strip) < 2:
        return None

    # hyouki_strip がひらがなカタカナのみの場合は、
    # 読みを hyouki_strip から作る
    #     さいたまスーパーアリーナ
    if RE_HIRAGANA_KATAKANA.fullmatch(hyouki_strip):
        yomi = convert_to_hiragana(hyouki_strip)
        return yomi

    # 記事の最初の見出し以降を削除
    lines = article.split('\n==')[0]

    # 「}}'''」を「}}\n'''」に置換
    lines = RE_TEMPLATE_END_AND_BOLD.sub('}}\n\'\'\'', lines)

    # 「{{読み仮名」の前に改行を入れる
    lines = lines.replace('{{読み仮名', '\n{{読み仮名')

    lines = lines.splitlines()

    for line in lines:
        # 「{{読み仮名|表記|読み}}」から「表記(読み)」を作成
        #     {{読み仮名_ruby不使用|エコーチェンバー現象|
        #     エコーチェンバーげんしょう}}とは、
        if line.startswith('{{読み仮名'):
            line_mod = line.split('|')
            if len(line_mod) > 2:
                line_mod[2] = line_mod[2].split('}}')[0]
                line = f'{line_mod[1]}({line_mod[2]}) {line}'

        # 収録語は「盛夏(せいか)」が最小なので、7文字以下の行をスキップ
        # テンプレートをスキップ
        if len(line) < 8 or \
                line[0] in ('{', ' ', '|', '*'):
            continue

        # 全角英数を半角に変換
        line = normalize('NFKC', line)

        # HTMLの特殊文字を変換
        line = html.unescape(line)

        # 「{{...}}」を削除
        line = RE_TEMPLATE.sub('', line)
        # 「<ref .../>」と「<ref>...</ref>」を削除
        line = RE_REF.sub('', line)

        # 「 \'"「」『』」を削除
        line = line.translate(TRANS_KAKKO)

        # 「表記(読み)」から読みを取得
        line = line.split(f'{hyouki}(')

        if len(line) < 2:
            continue

        yomi = line[1]

        # 読みが2文字以下の場合はスキップ
        # 読みが「-」で始まる場合はスキップ
        #     スロバキア共和国(-きょうわこく
        if len(yomi) < 3 or \
                yomi.startswith('-'):
            continue

        # 読みを「)、/{[,」で切る
        yomi = RE_YOMI_KUGIRI.split(yomi)[0]

        # 読みにならない文字を削除
        yomi = yomi.translate(TRANS_NON_YOMI)

        # 読みが2文字以下の場合はスキップ
        # 読みが「ー」で始まる場合はスキップ
        # 読みがすべてカタカナの場合はスキップ
        #     ミュージシャン一覧(グループ)
        # 読みがひらがなカタカナ以外を含む場合はスキップ
        if len(yomi) < 3 or \
                yomi.startswith('ー') or \
                RE_KATAKANA.fullmatch(yomi) or \
                not RE_HIRAGANA_KATAKANA.fullmatch(yomi):
            continue

        # 読みのカタカナをひらがなに変換
        yomi = convert_to_hiragana(yomi)

        return yomi


def convert_to_hiragana(entry):
    entry = jaconv.kata2hira(entry)
    entry = entry.translate(TRANS_OLD_I_E)
    return entry


def remove_short_or_long_hyouki(hyouki):
    # 表記が1文字の場合はスキップ
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    len_hyouki = len(hyouki)
    if len_hyouki < 2 or len_hyouki > 25:
        hyouki = None

    return hyouki


if __name__ == '__main__':
    main()
