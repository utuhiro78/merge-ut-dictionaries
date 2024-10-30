#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_neologd.py
python ../common/adjust_entries.py mozcdic-ut-neologd.txt
python ../common/filter_unsuitable_words.py mozcdic-ut-neologd.txt

bzip2 -k mozcdic-ut-*.txt
mv mozcdic-ut-*.txt* ../merge/
