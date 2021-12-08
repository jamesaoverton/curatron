# curatron
Prototype curation system

## Tree Browser

To run the tree browser, you first need to place the following files (from IEDB) in the `build/` directory: `assay-tree.owl`, `disease-tree.owl`, `geolocation.owl`, `molecule-tree.owl`, `nonpeptide-tree.owl`, `organism-tree.owl`, `protein-tree.owl`, and `subspecies-tree.owl`.

Then, create the SQLite databases:
```bash
make dbs
```

Finally, you can run the Flask app to see the tree browsers, which are located at the `/browse` path:
```bash
export FLASK_APP=src/run.py
flask run
```

You can also run this app as a CGI script.
