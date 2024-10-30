#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_sudachidict.py
python ../common/adjust_entries.py mozcdic-ut-sudachidict.txt
python ../common/filter_unsuitable_words.py mozcdic-ut-sudachidict.txt

bzip2 -k mozcdic-ut-*.txt
mv mozcdic-ut-*.txt* ../merge/
