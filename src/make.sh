#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

#alt_cannadic="true"
#edict="true"
jawiki="true"
#neologd="true"
personal_names="true"
place_names="true"
#skk_jisyo="true"
sudachidict="true"

rm -f mozcdic-ut.txt
rm -rf mozcdic-ut-*/

if [[ $alt_cannadic = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-alt-cannadic.git
fi

if [[ $edict = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-edict2.git
fi

if [[ $jawiki = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-jawiki.git
fi

if [[ $neologd = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-neologd.git
fi

if [[ $personal_names = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-personal-names.git
fi

if [[ $place_names = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-place-names.git
fi

if [[ $skk_jisyo = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-skk-jisyo.git
fi

if [[ $sudachidict = "true" ]]; then
git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-sudachidict.git
fi

# UT辞書を展開して結合
mv mozcdic-ut-*/mozcdic-ut-*.txt.tar.bz2 .
for f in mozcdic-ut-*.txt.tar.bz2; do tar xf "$f"; done

cat mozcdic-ut-*.txt > mozcdic-ut.txt

# mozcdic-ut.txt の重複エントリを削除
python remove_duplicate_ut_entries.py mozcdic-ut.txt

# mozcdic-ut.txt の単語コストを変更
python count_word_hits.py
python apply_word_hits.py mozcdic-ut.txt
