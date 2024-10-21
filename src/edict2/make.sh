#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_edict2_to_mozcdic.py
python ../common/adjust_entries.py mozcdic-ut-edict2.txt

tar cjf mozcdic-ut-edict2.txt.tar.bz2 mozcdic-ut-edict2.txt
mv mozcdic-ut-edict2.txt* ../merge/
