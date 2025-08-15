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
    jawiki_dict = get_articles()

    with open('mozcdic-ut-jawiki.txt', 'w', encoding='utf-8') as file:
        file.writelines(jawiki_dict)


def get_articles():
    # Wikipedia のダンプを取得
    subprocess.run(
        ['wget', '-N', 'https://dumps.wikimedia.org/jawiki/latest/' +
            'jawiki-latest-pages-articles-multistream.xml.bz2'])

    buffer = 100 * 1024 ** 2
    article_part = ''
    cpu_cores = cpu_count()
    jawiki_dict = []

    # Wikipedia のダンプを読み込む
    with bz2.open(
        'jawiki-latest-pages-articles-multistream.xml.bz2', 'rt',
            encoding='utf-8') as file:
        while True:
            articles = file.read(buffer)

            # 最後まで読んだら終了
            if articles == '':
                break

            articles = articles.split('  </page>')
            articles[0] = article_part + articles[0]

            # ページの断片を保存
            article_part = articles[-1]

            with Pool(processes=cpu_cores) as p:
                jawiki_dict += p.map(get_hyouki, articles[:-1])

    c = 0

    for line in jawiki_dict:
        if type(line) is not list:
            continue

        jawiki_dict[c] = f'{line[0]}\t0000\t0000\t8000\t{line[1]}\n'
        c += 1

    jawiki_dict = jawiki_dict[:c]

    # 重複する行を削除
    jawiki_dict = sorted(list(set(jawiki_dict)))

    return (jawiki_dict)


def get_hyouki(article):
    # title から表記を取得
    #     <title>あいの里公園駅</title>
    article = article.split('</title>')

    if len(article) == 1:
        return

    hyouki = article[0].split('<title>')[1]

    # 記事を取得
    article = article[1].split('xml:space="preserve">')

    if len(article) == 1:
        return

    article = article[1]

    # 表記を「 (」で切る
    #     田中瞳 (アナウンサー)
    hyouki = hyouki.split(' (')[0]

    # 全角英数を半角に変換
    hyouki = normalize('NFKC', hyouki)

    # HTMLの特殊文字を変換
    hyouki = html.unescape(hyouki)

    # 表記にスペースがある場合はスキップ
    #     記事のスペースを削除して「表記(読み)」を検索するので、
    #     残してもマッチしない
    # 表記が26文字以上の場合はスキップ。候補ウィンドウが大きくなりすぎる
    if ' ' in hyouki or \
            len(hyouki) > 25:
        return

    hyouki = [hyouki, article]
    jawiki_dict = get_yomi(hyouki)
    return (jawiki_dict)


def get_yomi(hyouki):
    article = hyouki[1]
    hyouki = hyouki[0]

    # 表記から記号を削除して hyouki2 を作る
    hyouki2 = remove_kigou(hyouki)

    # hyouki2 が1文字以下の場合はスキップ
    if len(hyouki2) < 2:
        return

    # hyouki2 がひらがなとカタカナだけの場合は、読みを hyouki2 から作る
    #     さいたまスーパーアリーナ
    if hyouki2 == ''.join(re.findall('[ぁ-ゔァ-ヴー]', hyouki2)):
        yomi = convert_to_hira(hyouki2)
        jawiki_dict = [yomi, hyouki]
        return (jawiki_dict)

    # 最初の見出し以降を削除
    lines = article.split('\n==')[0]

    # テンプレート末尾と記事本文の間に改行を入れる
    lines = lines.replace('}}\'\'\'', '}}\n\'\'\'')
    lines = lines.replace('}}「\'\'\'', '}}\n\'\'\'')
    lines = lines.replace('}}『\'\'\'', '}}\n\'\'\'')

    # 「{{読み仮名」の前に改行を入れる
    lines = lines.replace('{{読み仮名', '\n{{読み仮名')

    lines = lines.splitlines()

    for line in lines:
        # 「{{読み仮名|表記|読み}}」から「表記(読み)」を作成
        #     {{読み仮名_ruby不使用|エコーチェンバー現象|
        #     エコーチェンバーげんしょう}}とは、
        if line[:6] == '{{読み仮名':
            l2 = line.split('|')

            if len(l2) > 2:
                l2[2] = l2[2].split('}}')[0]
                line = f'{l2[1]}({l2[2]}) {line}'

        # 収録語は「盛夏(せいか)」が最小なので、7文字以下の行をスキップ
        # テンプレートをスキップ
        if len(line) < 8 or \
                line[0] == '{' or \
                line[0] == ' ' or \
                line[0] == '|' or \
                line[0] == '*':
            continue

        # 全角英数を半角に変換
        line = normalize('NFKC', line)

        # HTMLの特殊文字を変換
        line = html.unescape(line)

        # '{{' から '}}' までの最短一致を削除
        # '<ref' から '/ref>' までの最短一致を削除
        # '<ref name' から '/>' までの最短一致を削除
        line = re.sub(r'{{.*?}}', '', line)
        line = re.sub(r'<ref.*?/ref>', '', line)
        line = re.sub(r'<ref name.*?/>', '', line)

        # ' \'"「」『』' を削除
        table = str.maketrans('', '', ' \'"「」『』')
        line = line.translate(table)

        # 「表記(読み)」から読みを取得
        line = line.split(f'{hyouki}(')

        if len(line) < 2:
            continue

        yomi = line[1]

        # 読みを「)」「、」「/」「{」「[」で切る
        yomi = yomi.split(')')[0].split('、')[0].split('/')[0].\
            split('{')[0].split('[')[0]

        # 読みから記号を削除
        yomi = remove_kigou(yomi)

        # 読みが2文字以下の場合はスキップ
        # 読みが「ー」で始まる場合はスキップ
        # 読みが全てカタカナの場合はスキップ
        #     ミュージシャン一覧(グループ)
        if len(yomi) < 3 or \
                yomi[0] == 'ー' or \
                yomi == ''.join(re.findall('[ァ-ヴー]', yomi)):
            continue

        # 読みがひらがなとカタカナだけでない場合はスキップ
        if yomi != ''.join(re.findall('[ぁ-ゔァ-ヴー]', yomi)):
            continue

        # 読みのカタカナをひらがなに変換
        yomi = convert_to_hira(yomi)

        jawiki_dict = [yomi, hyouki]
        return (jawiki_dict)


def remove_kigou(entry):
    table = str.maketrans('', '', ',.!?-+*=:・、。×★☆')
    return (entry.translate(table))


def convert_to_hira(entry):
    entry = jaconv.kata2hira(entry)
    table = str.maketrans('ゐゑ', 'いえ', '')
    return (entry.translate(table))


if __name__ == '__main__':
    main()
