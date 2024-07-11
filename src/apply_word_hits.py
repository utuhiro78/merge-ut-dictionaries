#!/usr/bin/env python
# coding: utf-8

import sys

if len(sys.argv) == 1:
	print("Usage: python script.py [FILE]")
	sys.exit()

filename = sys.argv[1]

# jawiki_hits を読み込む
# jawiki_hits	0	0	34	中居正広
with open("jawiki-latest-all-titles-in-ns0.hits", "r", encoding="utf-8") as file:
	lines = file.read().splitlines()

# mozcdic-ut を jawiki_hits に追加
with open(filename, "r", encoding="utf-8") as file:
	lines = lines + file.read().splitlines()

# 表記順に並べ替える
for i in range(len(lines)):
	# jawiki_hits	0	0	34	中居正広
	# なかいまさひろ	1843	1843	6477	中居正広

	entry1 = lines[i].split("\t")
	entry1.insert(0, entry1[4])
	lines[i] = "\t".join(entry1[0:5])

	# 中居正広	jawiki_hits	0	0	34
	# 中居正広	なかいまさひろ	1843	1843	6477

lines.sort()
entry2 = []

for i in range(len(lines)):
	# 中居正広	jawiki_hits	0	0	34

	entry1 = lines[i].split("\t")
	entry1[4] = int(entry1[4])

	if entry1[1] == "jawiki_hits":
		entry2 = entry1

		# jawiki_hits の行は後で削除するので None にする
		lines[i] = None

		# ヒット数を最大 30 にする
		if entry2[4] > 30:
			entry2[4] = 30

		continue

	# jawiki に存在しない表記で、英数字のみのものは収録しない
	if entry1[0] != entry2[0] and \
	len(entry1[0]) == len(entry1[0].encode()):
		lines[i] = None
		continue

	# jawiki に存在しない表記と、存在するが英数字のみの表記は、コストを 9000 台にする
	if entry1[0] != entry2[0] or \
	len(entry1[0]) == len(entry1[0].encode()):
		entry1[4] = str(9000 + (entry1[4] // 20))
		lines[i] = "\t".join(entry1)
		continue

	# jawiki のヒット数が 1 の表記はコストを 8000 台にする
	if entry2[4] == 1:
		entry1[4] = str(8000 + (entry1[4] // 20))
		lines[i] = "\t".join(entry1)
		continue

	# jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
	entry1[4] = str(8000 - (entry2[4] * 10))
	lines[i] = "\t".join(entry1)

lines = [line for line in lines if line is not None]

# Mozc 形式の並びに戻す
for i in range(len(lines)):
	# 中居正広	なかいまさひろ	1843	1843	6477

	entry1 = lines[i].split("\t")
	entry1.append(entry1[0])
	lines[i] = "\t".join(entry1[1:]) + "\n"

lines.sort()

with open(filename, "w", encoding="utf-8") as dicfile:
	dicfile.writelines(lines)
