#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import sys
from unicodedata import normalize

if len(sys.argv) == 1:
    print("Usage: python script.py [FILE]")
    sys.exit()

file_name = sys.argv[1]

# jawiki_hits を読み込む
# jawiki_hits    0    0    34    中居正広
with open("jawiki-latest-all-titles-in-ns0.hits", "r", encoding="utf-8") as file:
    lines = file.read().splitlines()

# mozcdic-ut を jawiki_hits に追加
with open(file_name, "r", encoding="utf-8") as file:
    lines = lines + file.read().splitlines()

# 表記順に並べ替える
for i in range(len(lines)):
    # jawiki_hits    0    0    34    中居正広
    # なかいまさひろ    1843    1843    6477    中居正広

    lines[i] = lines[i].split("\t")

    # 表記を正規化
    lines[i][4] = normalize("NFKC", lines[i][4])

    lines[i].insert(0, lines[i][4])
    lines[i] = lines[i][0:5]

lines.sort()
l2 = []

for line in lines:
    # 中居正広    jawiki_hits    0    0    34
    # 中居正広    なかいまさひろ    1843    1843    6477
    line[4] = int(line[4])

    if line[1] == "jawiki_hits":
        line_wiki = line

        # jawiki のヒット数を最大 30 にする
        if line_wiki[4] > 30:
            line_wiki[4] = 30

        continue

    # jawiki に存在しない英数字のみの表記はスキップ
    # jawiki のヒット数が 1 以上の英数字のみの表記はコストを 9000 台にする
    if len(line[0]) == len(line[0].encode()):
        if line[0] != line_wiki[0]:
            continue
        else:
            line[4] = str(9000 + (line[4] // 20))
    # jawiki に存在しない英数字以外を含む表記はコストを 9000 台にする
    elif line[0] != line_wiki[0]:
        line[4] = str(9000 + (line[4] // 20))
    # jawiki のヒット数が 1 の表記はコストを 8000 台にする
    elif line_wiki[4] == 1:
        line[4] = str(8000 + (line[4] // 20))
    # jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
    else:
        line[4] = str(8000 - (line_wiki[4] * 10))

    line.append(line[0])
    line = line[1:]
    l2.append(line)

lines = sorted(l2)

with open(file_name, "w", encoding="utf-8") as dict_file:
    for line in lines:
        dict_file.write("\t".join(line) + "\n")
