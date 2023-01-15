#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: APACHE LICENSE, VERSION 2.0

require 'zlib'

# jawiki-itles を取得
`wget -N https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz`

filename = "jawiki-latest-all-titles-in-ns0.gz"
dicname = "jawiki-latest-all-titles-in-ns0.cost"

gz = Zlib::GzipReader.open(filename)
	titles = gz.read.split("\n")
gz.close


l2 = []
p = 0

titles.length.times do |i|
	# "BEST_(三浦大知のアルバム)" を
	# "三浦大知のアルバム)" に変更。
	# 「三浦大知」を前方一致検索できるようにする
	titles[i] = titles[i].split("_(")[-1]

	# 表記が2文字以下の場合はスキップ
	if titles[i].length < 3
		next
	end

	# "_" を " " に置き換える
	# THE_BEATLES
	l2[p] = titles[i].gsub("_", " ")
	p = p + 1
end

titles = l2.sort
l2 = []

dicfile = File.new(dicname, "w")

t_length = titles.length

t_length.times do |i|
	# 重複行をスキップ
	# カウント対象として必要なので削除はしない。
	if titles[i] == titles[i - 1]
		next
	end

	c = 1

	# 前方一致する限りカウントし続ける
	while (i + c) < t_length && titles[i + c].index(titles[i]) == 0
		c = c + 1
	end

	dicfile.puts "jawikititles	0	0	" + c.to_s + "	" + titles[i]
end

dicfile.close
