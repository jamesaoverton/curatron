### Workflow
#
# - `./src/run.py` run.py

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
