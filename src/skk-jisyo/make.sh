#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_skk_jisyo.py

bzip2 -k mozcdic-ut-*.txt
mv mozcdic-ut-*.txt* ../merge/
