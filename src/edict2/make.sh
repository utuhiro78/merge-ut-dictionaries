#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_edict2.py
python ../common/adjust_entries.py mozcdic-ut-edict2.txt

bzip2 -k mozcdic-ut-*.txt
mv mozcdic-ut-*.txt* ../merge/
