#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import os
import re
import sys


def main():
    args = sys.argv[1:]

    if not args:
        print('No file specified.')
        sys.exit()

    file_name = args[0]

    # NG エントリを読む
    unsuitables = get_unsuitables()

    # UT エントリを読む
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()

    lines_mod = []

    for line in lines:
        hyouki = line.rsplit('\t', 1)[1]
        hyouki = remove_unsuitable_entry(hyouki, unsuitables)
        if not hyouki:
            continue

        lines_mod.append(f'{line}\n')

    lines = lines_mod

    with open(file_name, 'w', encoding='utf-8') as dict_file:
        dict_file.writelines(lines)


def get_unsuitables():
    # NG エントリを読む
    dir_python = os.path.dirname(__file__)

    with open(
            f'{dir_python}/unsuitable_words.txt', 'r',
            encoding='utf-8') as file:
        unsuitables = file.read().splitlines()

    for i in range(len(unsuitables)):
        if unsuitables[i].startswith('/'):
            unsuitables[i] = re.compile(unsuitables[i][1:])

    return unsuitables


def remove_unsuitable_entry(hyouki, unsuitables):
    for unsuitable in unsuitables:
        if type(unsuitable) is re.Pattern:
            if re.match(unsuitable, hyouki):
                return None
        elif unsuitable in hyouki:
            return None

    return hyouki


if __name__ == '__main__':
    main()
