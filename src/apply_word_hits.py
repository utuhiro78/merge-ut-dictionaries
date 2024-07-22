#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import sys

if len(sys.argv) == 1:
	print("Usage: python script.py [FILE]")
	sys.exit()

file_name = sys.argv[1]

# jawiki_hits を読み込む
# jawiki_hits	0	0	34	中居正広
with open("jawiki-latest-all-titles-in-ns0.hits", "r", encoding="utf-8") as file:
	lines = file.read().splitlines()

# mozcdic-ut を jawiki_hits に追加
with open(file_name, "r", encoding="utf-8") as file:
	lines = lines + file.read().splitlines()

# 表記順に並べ替える
for i in range(len(lines)):
	# jawiki_hits	0	0	34	中居正広
	# なかいまさひろ	1843	1843	6477	中居正広

	entry = lines[i].split("\t")
	entry.insert(0, entry[4])
	lines[i] = "\t".join(entry[0:5])

lines.sort()

for i in range(len(lines)):
	# 中居正広	jawiki_hits	0	0	34
	# 中居正広	なかいまさひろ	1843	1843	6477

	entry = lines[i].split("\t")
	entry[4] = int(entry[4])

	if entry[1] == "jawiki_hits":
		entry_wiki = entry

		# jawiki_hits の行は None にして、後で削除
		lines[i] = None

		# ヒット数を最大 30 にする
		if entry_wiki[4] > 30:
			entry_wiki[4] = 30

		continue

	# jawiki に存在しない表記で、英数字のみのものはスキップ
	if entry[0] != entry_wiki[0] and \
	len(entry[0]) == len(entry[0].encode()):
		lines[i] = None
		continue

	# jawiki に存在しない表記と、存在するが英数字のみの表記は、コストを 9000 台にする
	if entry[0] != entry_wiki[0] or \
	len(entry[0]) == len(entry[0].encode()):
		entry[4] = str(9000 + (entry[4] // 20))
		lines[i] = "\t".join(entry)
		continue

	# jawiki のヒット数が 1 の表記はコストを 8000 台にする
	if entry_wiki[4] == 1:
		entry[4] = str(8000 + (entry[4] // 20))
		lines[i] = "\t".join(entry)
		continue

	# jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
	entry[4] = str(8000 - (entry_wiki[4] * 10))
	lines[i] = "\t".join(entry)

lines = [line for line in lines if line is not None]

# Mozc 形式の並びに戻す
for i in range(len(lines)):
	# 中居正広	なかいまさひろ	1843	1843	6477

	entry = lines[i].split("\t")
	entry.append(entry[0])
	lines[i] = "\t".join(entry[1:]) + "\n"

lines.sort()

with open(file_name, "w", encoding="utf-8") as dict_file:
	dict_file.writelines(lines)
