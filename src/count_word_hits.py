#! /usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import gzip
import subprocess

# jawiki-latest-all-titles を取得
subprocess.run(['wget', '-N', 'https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz'], check=True)

filename = "jawiki-latest-all-titles-in-ns0.gz"
dicname = "jawiki-latest-all-titles-in-ns0.hits"

with gzip.open(filename, "rt", encoding="utf-8") as file:
	lines = file.read().splitlines()

l2 = []

for i in range(len(lines)):
	# "BEST_(三浦大知のアルバム)" を
	# "三浦大知のアルバム)" に変更。
	# 「三浦大知」を前方一致検索できるようにする
	lines[i] = lines[i].split("_(")[-1]

	# 表記が1文字の場合はスキップ
	if len(lines[i]) <= 1:
		continue

	# "_" を " " に置き換える
	# THE_BEATLES
	lines[i] = lines[i].replace("_", " ")

	l2.append(lines[i])

lines = list(set(l2))
l2 = []
lines.sort()

for i in range(len(lines)):
	c = 1

	# 前方一致するエントリがなくなるまでカウント
	while i + c < len(lines) and lines[i + c].startswith(lines[i]):
		c = c + 1

	l2.append("jawiki_hits\t0\t0\t" + str(c) + "\t" + lines[i])

lines = l2
l2 = []

with open(dicname, "w", encoding="utf-8") as dicfile:
	dicfile.write("\n".join(lines))
