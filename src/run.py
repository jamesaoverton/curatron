#! /usr/bin/env python3

import os

from flask import Flask, render_template, request
from gizmos.search import search
from gizmos.tree import tree as render_tree
from sqlalchemy import create_engine
from wsgiref.handlers import CGIHandler

app = Flask(
    __name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "resources")),
)
app.url_map.strict_slashes = False

TREES = [
    "organism",
    "subspecies",
    "protein",
    "nonpeptide",
    "molecule",
    "assay",
    "disease",
    "geolocation",
]


@app.route("/")
def index():
    return render_template("index.html", default="Hello")


@app.route("/browse")
def list_trees():
    return render_template("browse.html", trees=TREES)


@app.route("/browse/<tree>")
def show_tree(tree):
    if tree == "style.css":
        # Do nothing - workaround for unknown stylesheet
        return render_template("template.html")
    conn = create_connection(tree)
    fmt = request.args.get("format")
    if fmt and fmt == "json":
        # Return search results
        data = search(conn, request.args.get("text"))
        return data
    html = render_tree(
        conn,
        tree,
        None,
        href="./" + tree + "/{curie}",
        title="",
        include_search=True,
        standalone=True,
    )
    return render_template("tree.html", tree=html)


@app.route("/browse/<tree>/<term>")
def show_term(tree, term):
    if tree == "style.css":
        # Do nothing - workaround for unknown stylesheet
        return render_template("template.html")
    conn = create_connection(tree)
    fmt = request.args.get("format")
    if fmt and fmt == "json":
        # Return search results
        data = search(conn, request.args.get("text"))
        return data
    html = render_tree(
        conn, tree, term, href="./{curie}", title="", include_search=True, standalone=True
    )
    return render_template("tree.html", tree=html)


def create_connection(tree):
    if tree == "geolocation":
        path = "build/geolocation.db"
    else:
        path = f"build/{tree}-tree.db"
    abspath = os.path.abspath(path)
    db_url = "sqlite:///" + abspath
    return create_engine(db_url)


def main():
    #CGIHandler().run(app)
    app.run(port=5002, debug=True)


if __name__ == "__main__":
    main()
