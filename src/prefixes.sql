CREATE TABLE IF NOT EXISTS prefix (
  prefix TEXT PRIMARY KEY,
  base TEXT NOT NULL
);

INSERT OR IGNORE INTO prefix VALUES
("rdf",  "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
("xsd",  "http://www.w3.org/2001/XMLSchema#"),
("owl",  "http://www.w3.org/2002/07/owl#"),
("oio",  "http://www.geneontology.org/formats/oboInOwl#"),
("dce",  "http://purl.org/dc/elements/1.1/"),
("dct",  "http://purl.org/dc/terms/"),
("foaf", "http://xmlns.com/foaf/0.1/"),

-- OBO prefixes
("obo",        "http://purl.obolibrary.org/obo/"),
("DOID",       "http://purl.obolibrary.org/obo/DOID_"),
("GAZ",        "http://purl.obolibrary.org/obo/GAZ_"),
("NCBITaxon",  "http://purl.obolibrary.org/obo/NCBITaxon_"),
("ncbitaxon",  "http://purl.obolibrary.org/obo/ncbitaxon#"),
("OBI",        "http://purl.obolibrary.org/obo/OBI_"),

-- IEDB prefixes
("annotation",    "http://purl.uniprot.org/annotation/"),
("nonpep",        "https://ontology.iedb.org/nonpeptide/"),
("ONTIE",      "https://ontology.iedb.org/ontology/ONTIE_"),
("protein",       "https://ontology.iedb.org/protein/"),
("role",          "https://ontology.iedb.org/by-role/"),
("taxon",         "https://ontology.iedb.org/taxon/"),
("taxon-protein", "https://ontology.iedb.org/taxon-protein/"),
("uniprot",       "http://www.uniprot.org/uniprot/");
