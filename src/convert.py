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
    parser.add_argument("table")
    args = parser.parse_args()

    dir = os.path.split(args.table)[0]

    tables = []
    with open(args.table) as f:
        rows = csv.DictReader(f, delimiter="\t")
        for row in rows:
            if row["type"] is None or row["type"].strip() == "":
                tables.append(row["table"])

    columns = []
    path = os.path.join(dir, "column.tsv")
    with open(path) as f:
        rows = csv.DictReader(f, delimiter="\t")
        columns = list(rows)

    for table in tables:
        if table == "prefix":
            continue
        path = os.path.join(dir, f"{table}.json")
        data = None
        with open(path) as f:
            data = json.load(f)
        #print(path, len(data), print(type(data)))
        fieldnames = []
        for row in columns:
            if row["table"] != table:
                continue
            fieldnames.append(row["column"])
        if type(data) == dict:
            print(path, "dict")
            with open(path.replace(".json", ".tsv"), "w") as o:
                writer = csv.DictWriter(o, fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
                writer.writeheader()
                writer.writerow(data)
        elif type(data) == list:
            print(path, "list")
            with open(path.replace(".json", ".tsv"), "w") as o:
                writer = csv.DictWriter(o, fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
                writer.writeheader()
                writer.writerows(data)
        else:
            continue


if __name__ == "__main__":
    main()
