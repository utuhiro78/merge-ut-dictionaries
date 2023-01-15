#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: APACHE LICENSE, VERSION 2.0

require 'nkf'

targetfiles = ARGV

if ARGV == []
	puts "Usage: ruby script.rb [FILE]"
	exit
end

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
	if s1[0] + " " + s1[-1] == s2[0] + " " + s2[-1]
		next
	end

	dicfile.puts s1.join("	")
end

dicfile.close
