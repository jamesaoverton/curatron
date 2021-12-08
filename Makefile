### Workflow
#
# - `./src/run.py` run.py

build:
	mkdir -p $@

UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
	RDFTAB_URL := https://github.com/ontodev/rdftab.rs/releases/download/v0.1.1/rdftab-x86_64-apple-darwin
else
	RDFTAB_URL := https://github.com/ontodev/rdftab.rs/releases/download/v0.1.1/rdftab-x86_64-unknown-linux-musl
endif

build/rdftab: | build
	curl -L -o $@ $(RDFTAB_URL)
	chmod +x $@

### Tables

GSURL := "https://docs.google.com/spreadsheets/d/1oy2NSxb6er3-QQ7bZMKqSpOOVSCAeg7qPII-VD2ahk8/"

src/resources/table.tsv:
	curl -L -o $@ "$(GSURL)export?format=tsv&gid=0"

src/resources/column.tsv:
	curl -L -o $@ "$(GSURL)export?format=tsv&gid=1859463123"

src/resources/datatype.tsv:
	curl -L -o $@ "$(GSURL)export?format=tsv&gid=1518754913"

.PHONY: update-meta-tables
update-meta-tables:
	rm -f src/resources/*.tsv
	make src/resources/table.tsv src/resources/column.tsv src/resources/datatype.tsv

### Tree Browser

TREES = organism-tree subspecies-tree protein-tree nonpeptide-tree molecule-tree assay-tree disease-tree geolocation
DBS = $(foreach T,$(TREES),build/$(T).db)

dbs: $(DBS)

build/%.db: src/prefixes.sql build/%.owl | build/rdftab
	rm -rf $@
	sqlite3 $@ < $<
	./build/rdftab $@ < $(word 2,$^)
	sqlite3 $@ "CREATE INDEX idx_stanza ON statements (stanza);"
	sqlite3 $@ "CREATE INDEX idx_subject ON statements (subject);"
	sqlite3 $@ "CREATE INDEX idx_predicate ON statements (predicate);"
	sqlite3 $@ "CREATE INDEX idx_object ON statements (object);"
	sqlite3 $@ "CREATE INDEX idx_value ON statements (value);"
	sqlite3 $@ "ANALYZE;"
