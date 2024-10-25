#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python generate_jawiki_ut.py
python ../common/adjust_entries.py mozcdic-ut-jawiki.txt
python ../common/filter_unsuitable_words.py mozcdic-ut-jawiki.txt

tar cjf mozcdic-ut-jawiki.txt.tar.bz2 mozcdic-ut-jawiki.txt
mv mozcdic-ut-*.txt* ../merge/
