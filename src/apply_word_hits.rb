#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

require 'nkf'

targetfiles = ARGV

if ARGV == []
	puts "Usage: ruby script.rb [FILE]"
	exit
end

filename = ARGV[0]
dicname = filename

# jawiki_hits を読み込む
# jawiki_hits	0	0	34	中居正広
file = File.new("jawiki-latest-all-titles-in-ns0.hits", "r", encoding: "UTF-8")
	lines = file.read.split("\n")
file.close

# mozcdic-ut を jawiki_hits に追加
file = File.new(filename, "r", encoding: "UTF-8")
	lines = lines + file.read.split("\n")
file.close

# 表記順に並べ替える
lines.length.times do |i|
	# jawiki_hits	0	0	34	中居正広
	# なかいまさひろ	1843	1843	6477	中居正広

	s1 = lines[i].split("	")
	lines[i] = s1[-1] + "	" + s1[0..3].join("	")

	# 中居正広	jawiki_hits	0	0	34
	# 中居正広	なかいまさひろ	1843	1843	6477
end

lines = lines.sort
s2 = []

lines.length.times do |i|
	# 中居正広	jawiki_hits	0	0	34

	s1 = lines[i].split("	")
	s1[4] = s1[4].to_i

	if s1[1] == "jawiki_hits"
		s2 = s1

		# jawiki_hits の行は後で削除するので nil にする
		lines[i] = nil

		# ヒット数を最大 30 にする
		if s2[4] > 30
			s2[4] = 30
		end

		next
	end

	# jawiki に存在しない表記で、英数字のみのものは収録しない
	if s1[0] != s2[0] && s1[0].length == s1[0].bytesize
		lines[i] = nil
		next
	end

	# jawiki に存在しない表記と、存在するが英数字のみの表記は、コストを 9000 台にする
	if s1[0] != s2[0] || s1[0].length == s1[0].bytesize
		s1[4] = (9000 + (s1[4] / 20)).to_s
		lines[i] = s1.join("	")
		next
	end

	# jawiki のヒット数が 1 の表記はコストを 8000 台にする
	if s2[4] == 1
		s1[4] = (8000 + (s1[4] / 20)).to_s
		lines[i] = s1.join("	")
		next
	end

	# jawiki のヒット数が 2 以上の表記はコストを 7000 台にする
	s1[4] = (8000 - (s2[4] * 10)).to_s
	lines[i] = s1.join("	")
end

lines = lines.compact

# Mozc 形式の並びに戻す
lines.length.times do |i|
	# 中居正広	なかいまさひろ	1843	1843	6477

	s = lines[i].split("	")
	lines[i] = s[1..-1].join("	") + "	" + s[0]

	# なかいまさひろ	1843	1843	6477	中居正広
end

lines = lines.sort

dicfile = File.new(dicname, "w")
	dicfile.puts lines
dicfile.close
