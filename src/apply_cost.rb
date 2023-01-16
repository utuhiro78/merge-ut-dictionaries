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

# jawiki-titles を読み込む
# jawikititles	0	0	34	中居正広
file = File.new("jawiki-latest-all-titles-in-ns0.cost", "r")
	lines = file.read.split("\n")
file.close

# mozcdic-jawiki-ut を jawiki-titles に追加
# jawikititles	0	0	34	中居正広
# なかいまさひろ	1847	1847	6477	中居正広
file = File.new(filename, "r")
	lines = lines + file.read.split("\n")
file.close

# jawiki-titles の下に mozcdic-jawiki-ut が来るよう並べ替える
# 中居正広	jawikititles	0	0	34
# 中居正広	なかいまさひろ	1847	1847	6477
lines.length.times do |i|
	s = lines[i].split("	")
	lines[i] = s[-1] + "	" + s[0..3].join("	")
end

lines = lines.sort
jawiki = []

lines.length.times do |i|
	s = lines[i].split("	")
	s[4] = s[4].to_i

	# 中居正広	jawikititles	0	0	34
	if s[1] == "jawikititles"
		jawiki = s
		# jawiki-titles の行を後で削除できるよう nil にする
		lines[i] = nil

		# jawikiのヒット数が大きいときは抑制
		if jawiki[4] > 30
			jawiki[4] = 30
		end

		next
	end

	# jawiki-titles にヒットしないかつ英数字のみの表記を除外
	if s[0] != jawiki[0] && s[0].length == s[0].bytesize
		lines[i] = nil
		next
	end

	# jawiki-titles にヒットしない表記はコストを 8000-9000 にする
	# コスト = 8000 + (元のコスト/10)
	if s[0] != jawiki[0]
		s[4] = (8000 + (s[4] / 10)).to_s
		lines[i] = s.join("	")
		next
	end

	# jawiki-titles に1回ヒットする表記はコストを 7000-8000 にする
	# 中居正広	なかいまさひろ	1847	1847	6477
	# コスト = 7000 + (元のコスト/10)
	if jawiki[4] == 1
		s[4] = (7000 + (s[4] / 10)).to_s
		lines[i] = s.join("	")
		next
	end

	# jawiki-titles に2回以上ヒットする表記はコストを 6000 前後にする
	# コスト = 6000 + (元のコスト/10) - (ヒット数*30)
	s[4] = (6000 + (s[4] / 10) - (jawiki[4] * 30)).to_s
	lines[i] = s.join("	")
end

lines = lines.compact

# Mozc 形式の並びに戻す
lines.length.times do |i|
	s = lines[i].split("	")
	lines[i] = s[1..-1].join("	") + "	" + s[0]
end

lines = lines.sort

dicfile = File.new(dicname, "w")
	dicfile.puts lines
dicfile.close
