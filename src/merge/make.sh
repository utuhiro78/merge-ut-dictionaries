#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

#alt_cannadic="true"
#edict2="true"
jawiki="true"
#neologd="true"
personal_names="true"
place_names="true"
#skk_jisyo="true"
sudachidict="true"

#generate_latest="true"

rm -rf mozcdic-ut*

if [[ $alt_cannadic = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-alt-cannadic.git
fi

if [[ $alt_cannadic = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../alt-cannadic/
    bash make.sh
    cd -
fi

if [[ $edict2 = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-edict2.git
fi

if [[ $edict2 = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../edict2/
    bash make.sh
    cd -
fi

if [[ $jawiki = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-jawiki.git
fi

if [[ $jawiki = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../jawiki/
    bash make.sh
    cd -
fi

if [[ $neologd = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-neologd.git
fi

if [[ $neologd = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../neologd/
    bash make.sh
    cd -
fi

if [[ $personal_names = "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-personal-names.git
fi

if [[ $place_names = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-place-names.git
fi

if [[ $place_names = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../place-names/
    bash make.sh
    cd -
fi

if [[ $skk_jisyo = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-skk-jisyo.git
fi

if [[ $skk_jisyo = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../skk-jisyo/
    bash make.sh
    cd -
fi

if [[ $sudachidict = "true" ]] && [[ $generate_latest != "true" ]]; then
    git clone --depth 1 https://github.com/utuhiro78/mozcdic-ut-sudachidict.git
fi

if [[ $sudachidict = "true" ]] && [[ $generate_latest = "true" ]]; then
    cd ../sudachidict/
    bash make.sh
    cd -
fi

if [[ $generate_latest != "true" ]]; then
    bzip2 -dfk mozcdic-ut-*/mozcdic-ut-*.txt.bz2
    mv mozcdic-ut-*/mozcdic-ut-*.txt .
fi

cat mozcdic-ut-*.txt > mozcdic-ut.txt

# IDを更新、重複エントリを削除、コストを調整
python merge_dictionaries.py mozcdic-ut.txt
