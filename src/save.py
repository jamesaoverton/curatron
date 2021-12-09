#!/usr/bin/env python3

import csv
import json
import os
import sqlite3
import sys

from argparse import ArgumentParser
from sqlalchemy.sql.expression import text as sql_text
from load import sqlite_types, special_table_types


def read_config_tables(conn):
    config = {"db": conn, "table": {}, "datatype": {}, "special": {}}
    for t in special_table_types:
        config["special"][t] = None

    # Load table table
    table_name = "table"
    rows = config["db"].execute(f"SELECT * FROM `{table_name}`")
    for row in rows:
        for column in ["table", "path", "type"]:
            if column not in row:
                raise Exception(f"Missing required column '{column}' reading '{table_name}'")
        for column in ["table", "path"]:
            if row[column].strip() == "":
                raise Exception(f"Missing required value for '{column}' reading '{table_name}'")
        for column in ["type"]:
            if not row[column]:
                continue
            if not type(row[column]) == str:
                continue
            if row[column].strip() == "":
                row[column] = None
        if row["type"] in special_table_types:
            if config["special"][row["type"]]:
                raise Exception(f"Multiple tables with type '{row['type']}' declared in '{table_name}'")
            config["special"][row["type"]] = row["table"]
        if row["type"] and row["type"] not in special_table_types:
            raise Exception(f"Unrecognized table type '{row['type']}' in '{table_name}'")
        row["column"] = {}
        config["table"][row["table"]] = row

    for table_type in special_table_types:
        if config["special"][table_type] is None:
            raise Exception(f"Missing required '{table_type}' table in '{path}'")

    # Load datatype table
    table_name = config["special"]["datatype"]
    rows = config["db"].execute(f"SELECT * FROM `{table_name}`")
    for row in rows:
        for column in ["datatype", "parent", "condition", "SQL type"]:
            if column not in row:
                raise Exception(f"Missing required column '{column}' reading '{table_name}'")
        for column in ["datatype"]:
            if not row[column]:
                continue
            if not type(row[column]) == str:
                continue
            if row[column].strip() == "":
                raise Exception(f"Missing required value for '{column}' reading '{table_name}'")
        for column in ["parent", "condition", "SQL type"]:
            if not row[column]:
                continue
            if not type(row[column]) == str:
                continue
            if row[column].strip() == "":
                row[column] = None
        # TODO: validate conditions
        config["datatype"][row["datatype"]] = row
    # TODO: Check for required datatypes: text, empty, line, word

    # Load column table
    table_name = config["special"]["column"]
    rows = config["db"].execute(f"SELECT * FROM `{table_name}`")
    for row in rows:
        for column in ["table", "column", "nulltype", "datatype"]:
            if column not in row:
                raise Exception(f"Missing required column '{column}' reading '{table_name}'")
        for column in ["table", "column", "datatype"]:
            if not row[column]:
                continue
            if not type(row[column]) == str:
                continue
            if row[column].strip() == "":
                raise Exception(f"Missing required value for '{column}' reading '{table_name}'")
        for column in ["nulltype"]:
            if not row[column]:
                continue
            if not type(row[column]) == str:
                continue
            if row[column].strip() == "":
                row[column] = None
        if row["table"] not in config["table"]:
            raise Exception(f"Undefined table '{row['table']}' reading '{table_name}'")
        if row["nulltype"] and row["nulltype"] not in config["datatype"]:
            raise Exception(f"Undefined nulltype '{row['nulltype']}' reading '{table_name}'")
        if row["datatype"] not in config["datatype"]:
            raise Exception(f"Undefined datatype '{row['datatype']}' reading '{table_name}'")
        row["configured"] = True
        config["table"][row["table"]]["column"][row["column"]] = row

    return config

def save_tables(config):
    for table in config["table"].keys():
        save_table(config, table)

    # save message.tsv
    path = config["message_path"]
    with open(path, "w") as f:
        fieldnames = ["table", "cell", "rule", "level", "message"]
        writer = csv.DictWriter(f, fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(config["message"])

def save_table(config, table):
    path = config["table"][table]["path"]
    table_name = table
    rows = config["db"].execute(f"SELECT * FROM `{table_name}`")
    fieldnames = []
    for column in rows.description:
        if column[0].endswith("_meta"):
            continue
        fieldnames.append(column[0])
    r = 1
    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            r += 1
            for column in fieldnames:
                if f"{column}_meta" not in row:
                    continue
                meta = json.loads(row[f"{column}_meta"][5:-1])
                if "value" in meta:
                    row[column] = meta["value"]
                if "messages" not in meta:
                    continue
                cidx = fieldnames.index(column)
                c = "ABCDEFGHIJK"[cidx]
                cell = f"{c}{r}"
                for message in meta["messages"]:
                    message["table"] = table
                    message["cell"] = cell
                    config["message"].append(message)
            writer.writerow(row)

def safe_sql(template, params):
    """Given a SQL query template with variables and a dict of parameters,
    return an escaped SQL string."""
    stmt = sql_text(template).bindparams(**params)
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))

def main():
    parser = ArgumentParser()
    parser.add_argument("db")
    args = parser.parse_args()
    dir = os.path.split(args.db)[0]
    try:
        with sqlite3.connect(args.db) as conn:
            conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
            config = read_config_tables(conn)
            config["message"] = []
            config["message_path"] = os.path.join(dir, "message.tsv")
            save_tables(config)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(e)

if __name__ == "__main__":
    main()
