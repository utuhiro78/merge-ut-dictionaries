#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

require 'open-uri'
require 'nkf'

targetfiles = ARGV

if ARGV == []
	puts "Usage: ruby script.rb [FILE]"
	exit
end

url = "https://raw.githubusercontent.com/google/mozc/master/src/data/dictionary_oss/id.def"
id_mozc = URI.open(url).read.split(" 名詞,一般,")[0]
id_mozc = id_mozc.split("\n")[-1]

filename = ARGV[0]
dicname = filename

file = File.new(filename, "r")
	lines = file.read.split("\n")
file.close

lines.length.times do |i|
	s1 = lines[i].split("	")

	# IDを最新のものに変更
	s1[1..2] = [id_mozc, id_mozc]

	# 読みと表記を先頭にする
	s1 = [s1[0], s1[4], s1[3], s1[1],s1[2]]
	lines[i] = s1.join("	")
end

lines = lines.sort

dicfile = File.new(dicname, "w")

lines.length.times do |i|
	s1 = lines[i].split("	")
	s2 = lines[i - 1].split("	")

	# UT辞書内で重複するエントリのうち、コスト値の大きいものをスキップ
	# あいおい	相生	1847	1847	8200
	# あいおい	相生	1847	1847	8400
	if s1[0..1] == s2[0..1]
		next
	end

	s1 = [s1[0], s1[3], s1[4], s1[2], s1[1]]
	dicfile.puts s1.join("	")
end

dicfile.close
