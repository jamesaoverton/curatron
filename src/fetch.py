import json
import logging
import os
import requests

from argparse import ArgumentParser
from collections import defaultdict

QUERY_URL = "https://query-api.iedb.org"
OUTPUTS = {
    "tcell": [
        {"key": "tcell_ids", "table": "tcell_search", "id": "tcell_id"},
        {"key": "structure_ids", "table": "epitope_search", "id": "structure_id"},
    ],
    "bcell": [{"key": "bcell_ids", "table": "bcell_search", "id": "bcell_id"}],
    "mhc": [{"key": "elution_ids", "table": "mhc_search", "id": "elution_id"}],
    "tcr": [
        {"key": "tcr_receptor_group_ids", "table": "tcr_search", "id": "receptor_group_id"},
        {"key": "bcr_receptor_group_ids", "table": "bcr_search", "id": "receptor_group_id"},
    ],
}


def main():
    parser = ArgumentParser()
    parser.add_argument("reference_id", help="One or more space-separated reference IDs to fetch", nargs="+")
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
        outputs = defaultdict(list)
        for file, search_details in OUTPUTS.items():
            for sd in search_details:
                ids = data[sd["key"]]
                if not ids:
                    continue
                if file not in outputs:
                    outputs[file] = list()
                table = sd["table"]

                id_field = sd["id"]
                logging.info("Querying " + table)

                # Partition into sublists of max 354 (502 error when we hit 355 items)
                chunks = [ids[x : x + 354] for x in range(0, len(ids), 354)]
                for chunk in chunks:
                    q = f"{QUERY_URL}/{table}?{id_field}=in.({','.join([str(x) for x in chunk])})"
                    r = requests.get(q)
                    table_data = r.json()
                    outputs[file].extend(table_data)

        if not os.path.exists(f"build/ref:{ref_id}"):
            os.makedirs(f"build/ref:{ref_id}")
        for file, contents in outputs.items():
            if contents:
                with open(f"build/ref:{ref_id}/{file}.json", "w") as f:
                    f.write(json.dumps(contents, indent=4))


if __name__ == "__main__":
    main()
