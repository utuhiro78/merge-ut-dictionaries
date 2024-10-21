#!/bin/bash

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

python convert_alt_cannadic_to_mozcdic.py

tar cjf mozcdic-ut-alt-cannadic.txt.tar.bz2 mozcdic-ut-alt-cannadic.txt
mv mozcdic-ut-alt-cannadic.txt* ../merge/
