### Workflow
#
# 1. IEDB API (PostgREST)
#   - [Swagger](https://query-api.iedb.org/docs/swagger/#/)
#   - [Example JSON](https://query-api.iedb.org/reference_search?reference_id=eq.1037960)
# 2. [Sprocket](https://github.com/ontodev/sprocket)
#   - [IEDB API tables](http://localhost:5001)
#   - [reference_search](http://localhost:5001/reference_search)
#   - [reference 1037960](http://localhost:5001/reference_search?reference_id=eq.1037960&limit=1)
# 3. Fetch reference: JSONs, TSVs
# 4. Validate
#   - [Google Sheet](https://docs.google.com/spreadsheets/d/1oy2NSxb6er3-QQ7bZMKqSpOOVSCAeg7qPII-VD2ahk8/edit#gid=0)
#   - Sprocket with highlighting
# 5. HTML Forms
# 6. Excel: download, upload
# 7. Tree pages
# 8. New term requests
# 9. (Re)Submission

REFID := 1037960

all: build/ref_$(REFID)/table.tsv

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

src/resources/prefix.tsv:
	curl -L -o $@ "$(GSURL)export?format=tsv&gid=1105305212"

.PHONY: update-meta-tables
update-meta-tables:
	rm -f src/resources/*.tsv
	make src/resources/table.tsv src/resources/column.tsv src/resources/datatype.tsv src/resources/prefix.tsv

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



build/ref_$(REFID)/: src/fetch.py | build/
	mkdir $@
	$< $(REFID)

build/ref_$(REFID)/table.tsv: src/generate.py | build/ref_$(REFID)/
	$< $|

build/ref_$(REFID)/reference.tsv: src/convert.py build/ref_$(REFID)/table.tsv
	$^

build/ref_$(REFID)/reference.db: src/load.py src/validate.py build/ref_$(REFID)/table.tsv build/ref_$(REFID)/reference.tsv | build/ref_$(REFID)/
	sqlite3 $@ "VACUUM;"
	python3 $< $@ $(word 3,$^)

build/ref_$(REFID)/reference.xlsx: build/ref_$(REFID)/reference.tsv
	cd build/ref_$(REFID)/ && \
	rm -rf .axle/ && \
	axle init reference && \
	axle add reference.tsv && \
	axle add epitope.tsv && \
	axle add tcell.tsv && \
	axle push
