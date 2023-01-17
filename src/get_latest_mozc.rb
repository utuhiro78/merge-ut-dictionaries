#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

require 'open-uri'

uri = URI.parse("https://raw.githubusercontent.com/fcitx/mozc/fcitx/src/data/version/mozc_version_template.bzl")
lines = uri.read.to_s

version = lines.split('MAJOR = ')[1][0] + '.'
version = version + lines.split('MINOR = ')[1][0..1] + '.'
version = version + lines.split('BUILD_OSS = ')[1][0..3] + '.'

uri = URI.parse("https://github.com/google/mozc/commits/master")
lines = uri.read.to_s

date = lines.split('<relative-time datetime="')[1]
date = date.split('Z')[0]
date = date.tr("-T:", "")[0..7]

mozcver = version + "102." + date
mozcdir = "mozc-" + version + "102." + date

if FileTest.exist?(mozcdir + ".tar.bz2") == true
	puts mozcdir + ".tar.bz2 is up to date."
	exit
end

`rm -rf mozc`
`git clone --depth=1 --recurse-submodules --shallow-submodules https://github.com/fcitx/mozc.git`

`rm -rf mozc/.git/`
`mv mozc #{mozcdir}`

`tar -cjf #{mozcdir}.tar.bz2 #{mozcdir}`
`rm -rf #{mozcdir}`

`sed -i -e "s,_mozcver=.*,_mozcver=#{mozcver},g" fcitx5-mozc-ut.PKGBUILD`
