#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_neologd_to_mozcdic.py
python ../common/adjust_entries.py mozcdic-ut-neologd.txt
python ../common/filter_unsuitable_words.py mozcdic-ut-neologd.txt

tar cjf mozcdic-ut-neologd.txt.tar.bz2 mozcdic-ut-neologd.txt
mv mozcdic-ut-neologd.txt* ../merge/
