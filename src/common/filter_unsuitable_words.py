#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import os
import re
import sys

args = sys.argv[1:]

if not args:
    print('No file specified.')
    exit()

file_name = args[0]

# Mozc 形式の辞書を読み込む
#     なかいまさひろ    1917    1917    6477    中居正広
with open(file_name, 'r', encoding='utf-8') as file:
    lines = file.read().splitlines()

# NGリストを読み込む
dir_python = os.path.dirname(__file__)

with open(f'{dir_python}/unsuitable_words.txt', 'r', encoding='utf-8') as file:
    unsuitables = file.read().splitlines()

for i in range(len(unsuitables)):
    if unsuitables[i][0] == '/':
        unsuitables[i] = re.compile(unsuitables[i][1:])

with open(file_name, 'w', encoding='utf-8') as dict_file:
    for line in lines:
        hyouki = line.split('\t')[4]

        for unsuitable in unsuitables:
            if type(unsuitable) is re.Pattern:
                if re.match(unsuitable, hyouki) is not None:
                    hyouki = None
                    break
            elif unsuitable in hyouki:
                hyouki = None
                break

        if hyouki is not None:
            dict_file.write(line + '\n')
