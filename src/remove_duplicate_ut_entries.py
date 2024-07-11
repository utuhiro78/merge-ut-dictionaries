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
	entry1 = lines[i].split("\t")

	# IDを最新のものに変更
	entry1[1:3] = [id_mozc, id_mozc]

	# 読みと表記を先頭にする
	entry1.insert(1, entry1[4])
	lines[i] = "\t".join(entry1[:5])

lines.sort()
l2 = []

for i in range(len(lines)):
	entry1 = lines[i].split("\t")
	entry2 = lines[i - 1].split("\t")

	# [読み, 表記] が重複するエントリのうち、コストの大きいものをスキップ
	# あいおい	相生	1843	1843	8200
	# あいおい	相生	1843	1843	8400
	if entry1[:2] == entry2[:2]:
		continue

	# Mozc 形式の並びに戻す
	entry1.append(entry1[1])
	entry1.pop(1)
	l2.append("\t".join(entry1) + "\n")

lines = l2
l2 = []

with open(filename, "w", encoding="utf-8") as dicfile:
	dicfile.writelines(lines)
