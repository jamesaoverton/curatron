#!/usr/bin/env python3

import json
import logging
import os
import requests

from argparse import ArgumentParser
from collections import defaultdict

# Max number of elements in list for querying (in.(...))
CHUNK_SIZE = 354

# Output files and corresponding tables
OUTPUTS = {
    "epitope": {"key": "structure_ids", "table": "epitope_search", "id": "structure_id"},
    "tcell": {"key": "tcell_ids", "table": "tcell_search", "id": "tcell_id"},
    "bcell": {"key": "bcell_ids", "table": "bcell_search", "id": "bcell_id"},
    "mhc": {"key": "elution_ids", "table": "mhc_search", "id": "elution_id"},
    "tcr": {"key": "tcr_receptor_group_ids", "table": "tcr_search", "id": "receptor_group_id"},
    "bcr": {"key": "bcr_receptor_group_ids", "table": "bcr_search", "id": "receptor_group_id"},
}

# API URL
QUERY_URL = "https://query-api.iedb.org"


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "reference_id", help="One or more space-separated reference IDs to fetch", nargs="+"
    )
    parser.add_argument("-v", "--verbose", help="Run with increased logging", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARN)

    for ref_id in args.reference_id:
        logging.info(f"Retrieving data for reference ID {ref_id}")
        r = requests.get(f"{QUERY_URL}/reference_search?reference_id=eq.{ref_id}")
        data = r.json()[0]
        with open(f"build/ref_{ref_id}/reference.json", "w") as f:
            f.write(json.dumps(data, indent=4))

        outputs = defaultdict(list)
        for file, sd in OUTPUTS.items():
            ids = data[sd["key"]]
            if not ids:
                continue
            if file not in outputs:
                outputs[file] = list()
            table = sd["table"]
            id_field = sd["id"]
            logging.info("Querying " + table)

            # Partition into sublists of max CHUNK_SIZE to prevent 502 error
            chunks = [ids[x : x + CHUNK_SIZE] for x in range(0, len(ids), CHUNK_SIZE)]
            for chunk in chunks:
                q = f"{QUERY_URL}/{table}?{id_field}=in.({','.join([str(x) for x in chunk])})"
                r = requests.get(q)
                table_data = r.json()
                outputs[file].extend(table_data)

        if not os.path.exists(f"build/ref_{ref_id}"):
            os.makedirs(f"build/ref_{ref_id}")
        for file, contents in outputs.items():
            if contents:
                with open(f"build/ref_{ref_id}/{file}.json", "w") as f:
                    f.write(json.dumps(contents, indent=4))


if __name__ == "__main__":
    main()
