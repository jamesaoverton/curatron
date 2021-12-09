#!/usr/bin/env python3

import csv
import json
import os

from argparse import ArgumentParser
from fetch import OUTPUTS
from shutil import copy2

def main():
    """Give a directory, read the `reference.json` file,
    then copy the relevant parts of the src/reference/*.tsv files
    into the given directory."""
    parser = ArgumentParser()
    parser.add_argument("dir")
    args = parser.parse_args()

    reference = None
    path = os.path.join(args.dir, "reference.json")
    with open(path) as f:
        reference = json.load(f)

    tables = ["table", "column", "datatype", "prefix", "reference"]
    for table, value in OUTPUTS.items():
        ids = value["key"]
        if ids not in reference:
            continue
        if not reference[ids]:
            continue
        tables.append(table)

    for table in ["table", "column"]:
        with open(f"src/resources/{table}.tsv") as infile:
            rows = csv.DictReader(infile, delimiter="\t")
            path = os.path.join(args.dir, f"{table}.tsv")
            with open(path, "w") as outfile:
                writer = csv.DictWriter(outfile, rows.fieldnames, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                for row in rows:
                    if "path" in row:
                        row["path"] = os.path.join(args.dir, row["path"])
                    if row["table"] in tables:
                        writer.writerow(row)

    path = os.path.join(args.dir, "datatype.tsv")
    copy2("src/resources/datatype.tsv", path)

    path = os.path.join(args.dir, "prefix.tsv")
    copy2("src/resources/prefix.tsv", path)

if __name__ == "__main__":
    main()
