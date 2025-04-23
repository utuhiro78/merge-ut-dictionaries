#!/usr/bin/env python
# coding: utf-8

# Author: 7sDream (i at 7sdre dot am)
# License: Apache License, Version 2.0

import sys
import csv
import itertools


def convert(line):
    parts = line.strip().split("\t")
    return [parts[0], parts[4], "名詞", ""]


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input-file> <output-base-name>")
        sys.exit(1)

    input_file = sys.argv[1]
    out_base = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        data = map(convert, filter(lambda line: len(line.strip()) > 0, f))

        # Mozc user dictionaries has 1000_000 max record limit.
        volumes = []
        for i, batch in enumerate(itertools.batched(data, 1000)):
            i = i // 1000
            if len(volumes) <= i:
                o = open(
                    f"{out_base}.{i + 1:>02}.txt", "w", encoding="utf-8", newline=""
                )
                writer = csv.writer(
                    o,
                    delimiter="\t",
                    lineterminator="\n",
                    quotechar='"',
                    doublequote=False,
                    escapechar="\\",
                )
                volumes.append([o, writer])
            else:
                o, writer = volumes[i]
            writer.writerows(batch)

        for o, _ in volumes:
            o.close()


if __name__ == "__main__":
    main()
