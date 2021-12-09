#!/usr/bin/env python3

import re


def validate_rows(config, table_name, rows):
    """Given a config map, a table name, and a list of rows (dicts from column names to column
    values), and a list of previously validated rows, return a list of validated rows."""
    result_rows = []
    for row in rows:
        result_row = {}
        for column, value in row.items():
            result_row[column] = {
                "value": value,
                "valid": True,
            }
        result_rows.append(validate_row(config, table_name, result_row, result_rows))
    return result_rows


def validate_row(config, table_name, row, prev_results):
    """Given a config map, a table name, a row to validate (a dict from column names to column
    values), and a list of previously validated rows, return the validated row."""
    duplicate = False
    for column_name, cell in row.items():
        cell = validate_cell(config, table_name, column_name, cell, prev_results)
        # If a cell violates either the unique or primary constraints, mark the row as a duplicate:
        if [msg for msg in cell["messages"] if msg["rule"] == "unique or primary key"]:
            duplicate = True
        row[column_name] = cell
    row["duplicate"] = duplicate
    return row


def validate_cell(config, table_name, column_name, cell, prev_results):
    """Given a config map, a table name, a column name, a cell to validate, and a list of previously
    validated rows (dicts mapping column names to column values), return the validated cell."""
    column = config["table"][table_name]["column"][column_name]
    cell["messages"] = []

    # If the value of the cell is one of the allowable null-type values for this column, then
    # mark it as such and return immediately:
    if column["nulltype"]:
        nt_name = column["nulltype"]
        nulltype = config["datatype"][nt_name]
        result = validate_condition(nulltype["condition"], cell["value"])
        if result:
            cell["nulltype"] = nt_name
            return cell

    # If the column has a primary or unique key constraint and the value of the cell is a duplicate
    # either of one of the previously validated rows in the batch, or of a validated row that has
    # already been inserted into the table, mark it as such:
    constraints = config["constraints"]
    if column_name in constraints["unique"][table_name] + constraints["primary"][table_name]:
        error_message = {
            "rule": "unique or primary key",
            "level": "error",
            "message": "Values of {} must be unique".format(column_name),
        }
        if [
            p[column_name]
            for p in prev_results
            if p[column_name]["value"] == cell["value"] and p[column_name]["valid"]
        ]:
            cell["valid"] = False
            cell["messages"].append(error_message)
        else:
            rows = config["db"].execute(
                "SELECT 1 FROM `{}` WHERE `{}` = '{}' LIMIT 1".format(
                    table_name, column["column"], cell["value"]
                )
            )
            if rows.fetchall():
                cell["valid"] = False
                cell["messages"].append(error_message)

    # Check the cell value against any foreign keys:
    fkeys = [fkey for fkey in constraints["foreign"][table_name] if fkey["column"] == column_name]
    for fkey in fkeys:
        rows = config["db"].execute(
            "SELECT 1 FROM `{}` WHERE `{}` = '{}' LIMIT 1".format(
                fkey["ftable"], fkey["fcolumn"], cell["value"]
            )
        )
        if not rows.fetchall():
            cell["valid"] = False
            cell["messages"].append(
                {
                    "rule": "foreign key",
                    "level": "error",
                    "message": "Value {} of column {} is not in {}.{}".format(
                        cell["value"], column_name, fkey["ftable"], fkey["fcolumn"]
                    ),
                }
            )

    # Validate that the value of the cell conforms to the datatypes associated with the column:
    def get_datatypes_to_check(dt_name):
        datatypes = []
        if dt_name is not None:
            datatype = config["datatype"][dt_name]
            if datatype["condition"] is not None:
                datatypes.append(datatype)
            datatypes += get_datatypes_to_check(datatype["parent"])
        return datatypes

    dt_name = column["datatype"]
    datatypes_to_check = get_datatypes_to_check(dt_name)
    # We use while and pop() instead of a for loop so as to check conditions in LIFO order:
    while datatypes_to_check:
        datatype = datatypes_to_check.pop()
        if datatype["condition"].startswith("exclude") == validate_condition(
            datatype["condition"], cell["value"]
        ):
            cell["messages"].append(
                {
                    "rule": "datatype:{}".format(datatype["datatype"]),
                    "level": "error",
                    "message": "{} should be {}".format(column_name, datatype["description"]),
                }
            )
            cell["valid"] = False

    return cell


def validate_condition(condition, value):
    """Given a condition string and a value string,
    return True of the condition holds, False otherwise."""
    # TODO: Implement real conditions.
    if condition == "equals('')":
        return value == ""
    elif condition == r"exclude(/\n/)":
        return "\n" in value
    elif condition == r"exclude(/\s/)":
        return bool(re.search(r"\s", value))
    elif condition == r"exclude(/^\s+|\s+$/)":
        return bool(re.search(r"^\s+|\s+$", value))
    elif condition == r"in('table', 'column', 'datatype')":
        return value in ("table", "column", "datatype")
    elif condition == r"match(/\w+/)":
        return bool(re.fullmatch(r"\w+", value))
    elif condition == r"match(/\d+/)":
        return bool(re.fullmatch(r"\d+", value))
    elif condition == r"match(/[ACDEFGHIKLMNPQRSTVWXY]+/)":
        return bool(re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWXY]+", value))
    elif condition == r"search(/:/)":
        return ":" in value
    else:
        raise Exception(f"Unhandled condition: {condition}")
