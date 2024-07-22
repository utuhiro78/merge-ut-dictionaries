#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import urllib.request
import sys

if len(sys.argv) == 1:
	print("Usage: python script.py [FILE]")
	exit()

file_name = sys.argv[1]

# Mozc の一般名詞のID
url = "https://raw.githubusercontent.com/google/mozc/master/src/data/dictionary_oss/id.def"
with urllib.request.urlopen(url) as response:
	id_mozc = response.read().decode()

id_mozc = id_mozc.split(" 名詞,一般,")[0].split("\n")[-1]

with open(file_name, "r", encoding="utf-8") as file:
	lines = file.read().splitlines()

for i in range(len(lines)):
	entry = lines[i].split("\t")

	# IDを最新のものに変更
	entry[1:3] = [id_mozc, id_mozc]

	# 読みと表記を先頭にする
	entry.insert(1, entry[4])
	lines[i] = entry[:5]

lines.sort()

with open(file_name, "w", encoding="utf-8") as dict_file:
	for i in range(len(lines)):
		# [読み, 表記] が重複するエントリのうち、コストの大きいものをスキップ
		# あいおい	相生	1843	1843	8200
		# あいおい	相生	1843	1843	8400
		if lines[i][0:2] == lines[i - 1][0:2]:
			continue

		entry = lines[i].copy()
		entry.append(entry[1])
		entry.pop(1)
		dict_file.write("\t".join(entry) + "\n")
