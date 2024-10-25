#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import bz2
import fcntl
import html
import jaconv
import re
import subprocess
import urllib.request
from multiprocessing import Pool, cpu_count
from unicodedata import normalize


def generate_jawiki_ut(article):
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

    # 表記にスペースがある場合はスキップ
    #     記事のスペースを削除したのち「表記(読み」を検索するので、残してもマッチしない
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    # 内部用のページをスキップ
    if ' ' in hyouki or \
            len(hyouki) > 25 or \
            '(曖昧さ回避)' in hyouki or \
            'Wikipedia:' in hyouki or \
            'ファイル:' in hyouki or \
            'Portal:' in hyouki or \
            'Help:' in hyouki or \
            'Template:' in hyouki or \
            'Category:' in hyouki or \
            'プロジェクト:' in hyouki:
        return

    # 読みにならない文字「!?」などを削除したhyouki_stripを作る
    hyouki_strip = hyouki.translate(str.maketrans('', '', ',.!?-+*=:/・、。×★☆'))

    # hyouki_stripが1文字の場合はスキップ
    if len(hyouki_strip) < 2:
        return

    # hyouki_stripがひらがなとカタカナだけの場合は、読みをhyouki_stripから作る
    #     さいたまスーパーアリーナ
    if hyouki_strip == ''.join(re.findall('[ぁ-ゔァ-ヴー]', hyouki_strip)):
        yomi = jaconv.kata2hira(hyouki_strip)
        yomi = yomi.translate(str.maketrans('ゐゑ', 'いえ'))

        entry = [yomi, id_mozc, id_mozc, '8000', hyouki]

        with open(dict_name, 'a', encoding='utf-8') as dict_file:
            fcntl.flock(dict_file, fcntl.LOCK_EX)
            dict_file.write('\t'.join(entry) + '\n')
            fcntl.flock(dict_file, fcntl.LOCK_UN)
        return

    # テンプレート末尾と記事本文の間に改行を入れる
    lines = article.replace("}}'''", "}}\n'''")
    lines = lines.splitlines()

    entry = []

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

        entry.append(line)

        # 記事が100行になったらbreak
        if len(entry) == 100:
            break

    lines = entry
    entry = ''

    # 記事から読みを作る
    for line in lines:
        # 全角英数を半角に変換
        line = normalize('NFKC', line)

        # HTML特殊文字を変換
        line = html.unescape(line)

        # '{{.*?}}' を削除
        #     '''皆藤 愛子'''{{efn2|一部のプロフィールが
        #     「皆'''籐'''（たけかんむり）」となっている}}
        #     （かいとう あいこ、[[1984年]]
        if '{{' in line:
            line = re.sub(r'{{.*?}}', '', line)

        # '<ref.*?<\/ref>' を削除
        #     '''井上 陽水'''（いのうえ ようすい<ref name="FMPJ">
        #     {{Cite web|和書|title=アーティスト・アーカイヴ 井上陽水|
        #     url=https://www.kiokunokiroku.jp/}}</ref>、
        line = re.sub(r'<ref.*?<\/ref>', '', line)

        # '<ref\ name.*?\/>' を削除
        #     <ref name="雑誌1" />
        line = re.sub(r'<ref\ name.*?\/>', '', line)

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

        entry = [yomi, id_mozc, id_mozc, '8000', hyouki]

        with open(dict_name, 'a', encoding='utf-8') as dict_file:
            fcntl.flock(dict_file, fcntl.LOCK_EX)
            dict_file.write('\t'.join(entry) + '\n')
            fcntl.flock(dict_file, fcntl.LOCK_UN)
        return


def main():
    global dict_name
    global id_mozc

    dict_name = 'mozcdic-ut-jawiki.txt'

    # Mozc の一般名詞のIDを取得
    url = 'https://raw.githubusercontent.com/' + \
        'google/mozc/master/src/data/dictionary_oss/id.def'

    with urllib.request.urlopen(url) as response:
        id_mozc = response.read().decode()

    id_mozc = id_mozc.split(' 名詞,一般,')[0].split('\n')[-1]

    subprocess.run(
        ['wget', '-N', 'https://dumps.wikimedia.org/jawiki/latest/' +
            'jawiki-latest-pages-articles-multistream.xml.bz2'])

    with open(dict_name, 'w', encoding='utf-8') as dict_file:
        dict_file.write('')

    article_fragment = ''
    cache_size = 200 * 1024 * 1024
    core_num = cpu_count()

    with bz2.open(
        'jawiki-latest-pages-articles-multistream.xml.bz2', 'rt',
            encoding='utf-8') as reader:
        while True:
            articles = reader.read(cache_size)

            # 最後まで読み切ったら終了
            if articles == '':
                break

            articles = articles.split('  </page>')
            articles[0] = article_fragment + articles[0]

            # 記事の断片を別名で保存
            article_fragment = articles[-1]

            # 記事の断片を削除
            articles = articles[0:-1]

            with Pool(processes=core_num) as pool:
                pool.map(generate_jawiki_ut, articles)

            pool.join()

    with open(dict_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 重複する行を削除
    lines = sorted(list(set(lines)))

    with open(dict_name, 'w', encoding='utf-8') as file:
        file.writelines(lines)


if __name__ == '__main__':
    main()
