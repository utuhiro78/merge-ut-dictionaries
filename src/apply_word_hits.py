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

	s1 = lines[i].split("\t")
	s1.insert(0, s1[4])
	lines[i] = "\t".join(s1[0:5])

	# 中居正広	jawiki_hits	0	0	34
	# 中居正広	なかいまさひろ	1843	1843	6477

lines.sort()
s2 = []

for i in range(len(lines)):
	# 中居正広	jawiki_hits	0	0	34

	s1 = lines[i].split("\t")
	s1[4] = int(s1[4])

	if s1[1] == "jawiki_hits":
		s2 = s1

		# jawiki_hits の行は後で削除するので None にする
		lines[i] = None

		# ヒット数を最大 30 にする
		if s2[4] > 30:
			s2[4] = 30

		continue

	# jawiki に存在しない表記で、英数字のみのものは収録しない
	if s1[0] != s2[0] and len(s1[0]) == len(s1[0].encode()):
		lines[i] = None
		continue

	# jawiki に存在しない表記と、存在するが英数字のみの表記は、コストを 9000 台にする
	if s1[0] != s2[0] or len(s1[0]) == len(s1[0].encode()):
		s1[4] = str(9000 + (s1[4] // 20))
		lines[i] = "\t".join(s1)
		continue

	# jawiki のヒット数が 1 の表記はコストを 8000 台にする
	if s2[4] == 1:
		s1[4] = str(8000 + (s1[4] // 20))
		lines[i] = "\t".join(s1)
		continue

	# jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
	s1[4] = str(8000 - (s2[4] * 10))
	lines[i] = "\t".join(s1)

lines = [line for line in lines if line is not None]

# Mozc 形式の並びに戻す
for i in range(len(lines)):
	# 中居正広	なかいまさひろ	1843	1843	6477

	s = lines[i].split("\t")
	s.insert(5, s[0])
	lines[i] = "\t".join(s[1:])

lines.sort()

with open(filename, "w", encoding="utf-8") as dicfile:
	dicfile.write("\n".join(lines))
	# cat で結合するときのために最後は改行する
	dicfile.write("\n")
