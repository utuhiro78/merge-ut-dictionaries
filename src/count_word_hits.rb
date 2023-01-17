#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

require 'zlib'

# jawiki-itles を取得
`wget -N https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz`

filename = "jawiki-latest-all-titles-in-ns0.gz"
dicname = "jawiki-latest-all-titles-in-ns0.hits"

gz = Zlib::GzipReader.open(filename)
	lines = gz.read.split("\n")
gz.close


l2 = []
p = 0

lines.length.times do |i|
	# "BEST_(三浦大知のアルバム)" を
	# "三浦大知のアルバム)" に変更。
	# 「三浦大知」を前方一致検索できるようにする
	lines[i] = lines[i].split("_(")[-1]

	# 表記が1文字の場合はスキップ
	if lines[i][1] == nil
		next
	end

	# "_" を " " に置き換える
	# THE_BEATLES
	lines[i] = lines[i].gsub("_", " ")

	l2[p] = lines[i]
	p = p + 1
end

lines = l2.sort
l2 = []

dicfile = File.new(dicname, "w")

lines.length.times do |i|
	# 重複する行をスキップ
	if lines[i] == lines[i - 1]
		next
	end

	c = 1

	# 前方一致するエントリがなくなるまでカウント
	while (i + c) < lines.length && lines[i + c].index(lines[i]) == 0
		c = c + 1
	end

	dicfile.puts "jawiki_hits	0	0	" + c.to_s + "	" + lines[i]
end

dicfile.close