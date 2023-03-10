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

lines = lines.sort

dicfile = File.new(dicname, "w")

lines.length.times do |i|
	s1 = lines[i].split("	")
	s2 = lines[i - 1].split("	")

	# UT辞書内で重複するエントリをコスト順にスキップ
	# あいおい	1847	1847	9000	相生
	if s1[0] + " " + s1[-1] == s2[0] + " " + s2[-1]
		next
	end

	# IDを最新のものに変更
	s1[1..2] = [id_mozc, id_mozc]

	dicfile.puts s1.join("	")
end

dicfile.close
