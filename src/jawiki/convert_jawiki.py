#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import bz2
import html
import jaconv
import re
import subprocess
from multiprocessing import Pool, cpu_count
from unicodedata import normalize


def main():
    # Wikipedia のダンプを取得
    subprocess.run(
        ['wget', '-N', 'https://dumps.wikimedia.org/jawiki/latest/' +
            'jawiki-latest-pages-articles-multistream.xml.bz2'])

    article_fragment = ''
    cache_size = 200 * 1024 * 1024
    core_num = cpu_count()
    jawiki_dict = []

    # Wikipedia のダンプを読み込む
    with bz2.open(
        'jawiki-latest-pages-articles-multistream.xml.bz2', 'rt',
            encoding='utf-8') as reader:
        while True:
            articles = reader.read(cache_size)

            # 最後まで読んだら終了
            if articles == '':
                break

            articles = articles.split('  </page>')
            articles[0] = article_fragment + articles[0]

            # 項目の断片を別名で保存
            article_fragment = articles[-1]

            articles = articles[0:-1]

            with Pool(processes=core_num) as p:
                jawiki_dict += p.map(convert_jawiki, articles)

    l2 = []

    for entry in jawiki_dict:
        if entry is None:
            continue

        entry = [entry[0], '0000', '0000', '8000', entry[1]]
        l2.append('\t'.join(entry) + '\n')

    # 重複する行を削除
    jawiki_dict = sorted(list(set(l2)))

    dict_name = 'mozcdic-ut-jawiki.txt'

    with open(dict_name, 'w', encoding='utf-8') as file:
        file.writelines(jawiki_dict)


def convert_jawiki(article):
    # Wikipediaの記事の例
    #     <title>あいの里公園駅</title>
    #     '''あいの里公園駅'''（あいのさとこうえんえき）は、

    article = article.split('</title>')

    if len(article) < 2:
        return

    # 表記を取得
    hyouki = article[0].split('<title>')[1]

    # 記事を取得
    article = article[1]

    # 表記の全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)

    # 表記を「 (」で切る
    # 田中瞳 (アナウンサー)
    hyouki = hyouki.split(' (')[0]

    # 表記のHTML特殊文字を変換
    hyouki = html.unescape(hyouki)

    # 表記にスペースがある場合はスキップ
    #     記事のスペースを削除して「表記(読み」を検索するので、残してもマッチしない
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    # 内部用のページをスキップ
    if ' ' in hyouki or \
            len(hyouki) > 25 or \
            hyouki.startswith('ファイル:') or \
            hyouki.startswith('Wikipedia:') or \
            hyouki.startswith('Template:') or \
            hyouki.startswith('Portal:') or \
            hyouki.startswith('Help:') or \
            hyouki.startswith('Category:') or \
            hyouki.startswith('プロジェクト:'):
        return

    # 読みにならない文字「!?」などを削除した hyouki2 を作る
    hyouki2 = hyouki.translate(str.maketrans('', '', ',.!?-+*=:/・、。×★☆'))

    # hyouki2 が1文字の場合はスキップ
    if len(hyouki2) < 2:
        return

    # hyouki2 がひらがなとカタカナだけの場合は、読みを hyouki2 から作る
    #     さいたまスーパーアリーナ
    if hyouki2 == ''.join(re.findall('[ぁ-ゔァ-ヴー]', hyouki2)):
        yomi = jaconv.kata2hira(hyouki2)
        yomi = yomi.translate(str.maketrans('ゐゑ', 'いえ'))

        jawiki_dict = [yomi, hyouki]
        return (jawiki_dict)

    # テンプレート末尾と記事本文の間に改行を入れる
    lines = article.replace("}}'''", "}}\n'''")
    lines = lines.splitlines()

    l2 = []

    # 記事の量を減らす
    for line in lines:
        # 収録語は「'''盛夏'''（せいか）」が最小なので、12文字以下の行はスキップ
        # テンプレートをスキップ
        if len(line) < 13 or \
                line[0] == '{' or \
                line[0] == '}' or \
                line[0] == '|' or \
                line[0] == '*':
            continue

        l2.append(line)

        # 記事が100行になったらbreak
        if len(l2) == 100:
            break

    lines = l2

    # 記事から読みを作る
    for line in lines:
        # 全角英数を半角に変換
        line = normalize('NFKC', line)

        # HTML特殊文字を変換
        line = html.unescape(line)

        # '{{' から '}}' までの最短一致を削除
        #     '''皆藤 愛子'''{{efn2|一部のプロフィールが「皆'''籐'''
        #     （たけかんむり）」となっている}}（かいとう あいこ、
        if '{{' in line:
            line = re.sub(r'{{.+?}}', '', line)

        # '<ref' から '/ref>' までの最短一致を削除
        #     '''井上 陽水'''（いのうえ ようすい<ref name="FMPJ">
        #     {{Cite web|和書|title=アーティスト・アーカイヴ 井上陽水|
        #     url=https://www.kiokunokiroku.jp/}}</ref>、
        line = re.sub(r'<ref.+?<\/ref>', '', line)

        # '<ref name' から '/>' までの最短一致を削除
        #     <ref name="雑誌1" />
        line = re.sub(r'<ref\ name.+?\/>', '', line)

        # 『』などを削除
        #     『不適切にもほどがある！』（ふてきせつにもほどがある）は、
        line = line.translate(str.maketrans('', '', ' "\'「」『』'))

        # 「表記(読み」から読みを取得
        if hyouki + '(' in line:
            yomi = line.split(hyouki + '(')[1]
        else:
            continue

        # 読みを「)」で切る
        yomi = yomi.split(')')[0]

        # 読みを「[[」で切る
        # ないとうときひろ[[1963年]]
        yomi = yomi.split('[[')[0]

        # 読みを「、」で切る
        # かいとうあいこ、[[1984年]]
        yomi = yomi.split('、')[0]

        # 読みを「/」で切る
        # ひみこ/ひめこ
        yomi = yomi.split('/')[0]

        # 読みにならない文字「!?」などを削除
        yomi = yomi.translate(str.maketrans('', '', ',.!?-+*=:・、。×★☆'))

        # 読みが2文字以下の場合はスキップ
        if len(yomi) < 3:
            continue

        # 読みが「ー」で始まる場合はスキップ
        # 読みが全てカタカナの場合はスキップ
        #     ミュージシャン一覧(グループ)
        if yomi[0] == 'ー' or \
                yomi == ''.join(re.findall('[ァ-ヴー]', yomi)):
            continue

        # 読みのカタカナをひらがなに変換
        yomi = jaconv.kata2hira(yomi)
        yomi = yomi.translate(str.maketrans('ゐゑ', 'いえ'))

        # 読みがひらがな以外を含む場合はスキップ
        if yomi != ''.join(re.findall('[ぁ-ゔー]', yomi)):
            continue

        jawiki_dict = [yomi, hyouki]
        return (jawiki_dict)


if __name__ == '__main__':
    main()
