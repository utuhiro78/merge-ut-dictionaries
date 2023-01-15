---
title: Merge UT Dictionaries
date: 2023-01-15
---

## Overview

Merge UT Dictionaries merges multiple UT dictionaries into one and modify the costs.

## License

mozcdic-ut.txt (Not provided in this repository): Combined

Merge UT Dictionaries uses jawiki-latest-all-titles (License: [CC BY-SA 3.0](https://ja.wikipedia.org/wiki/Wikipedia:ウィキペディアを二次利用する)) for cost modification.

Source code: Apache License, Version 2.0

## Usage

Clone necessary Mozc UT dictionaries and extract them.

```
git clone https://github.com/utuhiro78/merge-ut-dictionaries.git

cd merge-ut-dictionaries/src/

git clone https://github.com/utuhiro78/mozcdic-ut-jawiki.git
git clone https://github.com/utuhiro78/mozcdic-ut-neologd.git
git clone https://github.com/utuhiro78/mozcdic-ut-personal-names.git
git clone https://github.com/utuhiro78/mozcdic-ut-place-names.git

cp mozcdic-ut-*/mozcdic-ut-*.txt.tar.bz2 .

for f in mozcdic-ut-*.txt.tar.bz2; do tar xf "$f"; done
```

Comment out unnecessary UT dictionaries in make.sh.

```
mousepad make.sh
```

If you need only mozcdic-ut-neologd, edit the lines as follows:

```
#jawiki="true"
neologd="true"
#personal_names="true"
#place_names="true"
```

Run make.sh.

```
sh make.sh
```

Add mozcdic-ut.txt to dictionary00.txt and build Mozc as usual.

```
cd ..
ls mozcdic-ut.txt

cat ../mozc-master/src/data/dictionary_oss/dictionary00.txt mozcdic-ut.txt > dictionary00.txt.new
mv dictionary00.txt.new ../mozc-master/src/data/dictionary_oss/dictionary00.txt
```

[HOME](http://linuxplayers.g1.xrea.com/mozc-ut.html)
