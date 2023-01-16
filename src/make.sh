#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

edict="true"
jawiki="true"
neologd="true"
personal_names="true"
place_names="true"
sudachidict="true"

rm -f mozcdic-ut.txt

if [[ $edict = "true" ]]; then
cat mozcdic-ut-edict2.txt >> mozcdic-ut.txt
fi

if [[ $jawiki = "true" ]]; then
cat mozcdic-ut-jawiki.txt >> mozcdic-ut.txt
fi

if [[ $neologd = "true" ]]; then
cat mozcdic-ut-neologd.txt >> mozcdic-ut.txt
fi

if [[ $personal_names = "true" ]]; then
cat mozcdic-ut-personal-names.txt >> mozcdic-ut.txt
fi

if [[ $place_names = "true" ]]; then
cat mozcdic-ut-place-names.txt >> mozcdic-ut.txt
fi

if [[ $sudachidict = "true" ]]; then
cat mozcdic-ut-sudachidict.txt >> mozcdic-ut.txt
fi

ruby remove_duplicate_ut_entries.rb mozcdic-ut.txt

ruby generate_cost.rb
ruby apply_cost.rb mozcdic-ut.txt

mv mozcdic-ut.txt ../

rm -rf ../../merge-ut-dictionaries-release/
rsync -a ../* ../../merge-ut-dictionaries-release --exclude=jawiki-* --exclude=mozcdic-*
