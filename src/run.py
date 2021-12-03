#! /usr/bin/env python3

import csv
import json
import os

from argparse import ArgumentParser
from flask import abort, Flask, render_template, request, Response
from wsgiref.handlers import CGIHandler

app = Flask(
    __name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "resources"))
)
app.url_map.strict_slashes = False

@app.route("/")
def index():
    return render_template("template.html", content="Hello")


def main():
    CGIHandler().run(app)


if __name__ == "__main__":
    main()
