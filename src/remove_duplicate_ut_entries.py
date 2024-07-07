#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import urllib.request
import sys

if len(sys.argv) == 1:
	print("Usage: python script.py [FILE]")
	exit()

filename = sys.argv[1]

# Mozc の一般名詞のID
url = "https://raw.githubusercontent.com/google/mozc/master/src/data/dictionary_oss/id.def"
with urllib.request.urlopen(url) as response:
	id_mozc = response.read().decode()

id_mozc = id_mozc.split(" 名詞,一般,")[0].split("\n")[-1]

with open(filename, "r", encoding="utf-8") as file:
	lines = file.read().splitlines()

for i in range(len(lines)):
	s1 = lines[i].split()

	# IDを最新のものに変更
	s1[1:3] = [id_mozc, id_mozc]

	# 読みと表記を先頭にする
	s1.insert(1, s1[4])
	lines[i] = "\t".join(s1[0:5])

lines.sort()
l2 = []

for i in range(len(lines)):
	s1 = lines[i].split("\t")

	if i > 0:
		s2 = lines[i - 1].split("\t")

		# 「読み + 表記」が重複するエントリのうち、コストの大きいものをスキップ
		# あいおい	相生	1843	1843	8200
		# あいおい	相生	1843	1843	8400
		if s1[:2] == s2[:2]:
			continue

	# Mozc 形式の並びに戻す
	s1.insert(5, s1[1])
	s1.pop(1)
	l2.append("\t".join(s1))

lines = l2
l2 = []

with open(filename, "w", encoding="utf-8") as dicfile:
	dicfile.write("\n".join(lines))
