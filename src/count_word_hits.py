#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import gzip
import subprocess

# jawiki-latest-all-titles を取得
subprocess.run(['wget', '-N', 'https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz'], check=True)

file_name = "jawiki-latest-all-titles-in-ns0.gz"
dict_name = "jawiki-latest-all-titles-in-ns0.hits"

with gzip.open(file_name, "rt", encoding="utf-8") as file:
    lines = file.read().splitlines()

l2 = []

for line in lines:
    # "BEST_(三浦大知のアルバム)" を
    # "三浦大知のアルバム)" に変更。
    # 「三浦大知」を前方一致検索できるようにする
    line = line.split("_(")[-1]

    # 表記が1文字の場合はスキップ
    if len(line) < 2:
        continue

    # "_" を " " に置き換える
    # THE_BEATLES
    line = line.replace("_", " ")

    l2.append(line)

lines = sorted(list(set(l2)))
l2 = []

for i in range(len(lines)):
    c = 1

    # 前方一致するエントリがなくなるまでカウント
    while i + c < len(lines) and lines[i + c].startswith(lines[i]):
        c = c + 1

    # "jawiki_hits" の部分は jawiki の見出しになり得ない表記にする
    entry = ["jawiki_hits", "0", "0", str(c), lines[i]]
    l2.append("\t".join(entry) + "\n")

lines = l2

with open(dict_name, "w", encoding="utf-8") as dict_file:
    dict_file.writelines(lines)
