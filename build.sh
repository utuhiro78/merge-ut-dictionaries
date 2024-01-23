#!/bin/bash

docker build -t merge-ut-dictionaries ./
docker create -it --rm --name dict-build merge-ut-dictionaries
docker start dict-build

# Build dictionary
docker exec dict-build ./make.sh
# Copy built assets
mkdir -p ./dist/
docker cp dict-build:/home/ubuntu/work/mozcdic-ut.txt ./dist/

docker stop dict-build
