#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_jawiki.py
python ../common/adjust_entries.py mozcdic-ut-jawiki.txt
python ../common/filter_unsuitable_words.py mozcdic-ut-jawiki.txt

bzip2 -k mozcdic-ut-*.txt
mv mozcdic-ut-*.txt* ../merge/
