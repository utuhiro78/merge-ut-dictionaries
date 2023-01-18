#! /usr/bin/env ruby
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

require 'open-uri'

# Mozc のバージョンを取得
uri = URI.parse("https://raw.githubusercontent.com/google/mozc/master/src/data/version/mozc_version_template.bzl")
lines = uri.read.to_s

version = lines.split('MAJOR = ')[1][0] + '.'
version = version + lines.split('MINOR = ')[1][0..1] + '.'
version = version + lines.split('BUILD_OSS = ')[1][0..3] + '.'

# Mozc の最終コミット日を取得
uri = URI.parse("https://github.com/google/mozc/commits/master")
lines = uri.read.to_s

# <relative-time datetime="2023-01-16T12:00:11Z"
date = lines.split('<relative-time datetime="')[1]
date = date[0..9]
date = date.gsub("-", "")

# 最新の Mozc アーカイブが存在する場合は終了
mozcver = version + "102." + date
mozcdir = "mozc-" + version + "102." + date

if FileTest.exist?(mozcdir + ".tar.bz2") == true
	puts mozcdir + ".tar.bz2 is up to date."
	exit
end

# Mozc を取得
`rm -rf mozc`
`git clone --depth 1 --recursive --shallow-submodules https://github.com/google/mozc.git`

`rm -rf mozc/.git/`
`mv mozc #{mozcdir}`

# Fcitx5-Mozc を取得
`wget https://github.com/fcitx/mozc/archive/refs/heads/fcitx.zip -O mozc-fcitx.zip`
`unzip -q mozc-fcitx.zip`

# 差分を Mozc にコピー
`cp -r mozc-fcitx/scripts #{mozcdir}/`
`rm -rf #{mozcdir}/src/unix`
`cp -r mozc-fcitx/src/unix #{mozcdir}/src/`
`cp -f mozc-fcitx/src/{BUILD.fcitx*.bazel,WORKSPACE.bazel} #{mozcdir}/src/`
`rm -rf mozc-fcitx*`

# Mozc のアーカイブを作成
`tar -cjf #{mozcdir}.tar.bz2 #{mozcdir}`
`rm -rf #{mozcdir}`

# PKGBUILD を更新
`sed -i -e "s,_mozcver=.*,_mozcver=#{mozcver},g" fcitx5-mozc-ut.PKGBUILD`
