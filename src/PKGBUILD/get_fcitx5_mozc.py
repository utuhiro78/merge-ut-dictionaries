#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import os
import re
import shutil
import subprocess
import urllib.request

# Mozc のバージョンを取得
url = "https://raw.githubusercontent.com/google/mozc/master/src/data/version/mozc_version_template.bzl"
with urllib.request.urlopen(url) as response:
	lines = response.read().decode()

s = lines.split('MAJOR = ')[1].split('\n')[0]
version = s + '.'
s = lines.split('MINOR = ')[1].split('\n')[0]
version = version + s + '.'
s = lines.split('BUILD_OSS = ')[1].split('\n')[0]
version = version + s + '.102.'

# Mozc の最終コミット日を取得
url = "https://github.com/google/mozc/commits/master/"
response = urllib.request.urlopen(url)
lines = response.read().decode()

# "committedDate":"2024-01-16T06:05:57.000Z"
date = lines.split('"committedDate":"')[1]
date = date[0:10]
date = date.replace("-", "")

# Mozc のアーカイブが古い場合は取得
mozcver = version + date
mozcdir = "mozc-" + mozcver

if not os.path.exists(mozcdir + ".tar.zst"):
	if os.path.exists("mozc"):
		shutil.rmtree('mozc')

	subprocess.run(['git', 'clone', '--depth', '1', '--recursive', '--shallow-submodules', 'https://github.com/fcitx/mozc.git'], check=True)
	shutil.rmtree('mozc/.git')
	os.rename('mozc', mozcdir)
else:
	print(mozcdir + " is up to date.")
	subprocess.run(['tar', 'xf', '{}.tar.zst'.format(mozcdir)], check=True)

subprocess.run(['wget', '-N', 'https://github.com/fcitx/mozc/archive/refs/heads/fcitx.zip'], check=True)
subprocess.run(['unzip', '-q', 'fcitx.zip', 'mozc-fcitx/src/unix/*'], check=True)
shutil.rmtree(mozcdir + '/src/unix')
os.rename('mozc-fcitx/src/unix', mozcdir + '/src/unix')
shutil.rmtree('mozc-fcitx')

# Mozc のアーカイブを作成
subprocess.run(['tar', '--zstd', '-cf', '{}.tar.zst'.format(mozcdir), '{}'.format(mozcdir)], check=True)
shutil.rmtree(mozcdir)

# PKGBUILD を更新
f = open("fcitx5-mozc-ut.PKGBUILD", "r")
lines = f.read()

lines = re.sub('_mozcver=.*\n', '_mozcver={}\n'.format(mozcver), lines)

dicfile = open("fcitx5-mozc-ut.PKGBUILD", "w")
dicfile.write(lines)