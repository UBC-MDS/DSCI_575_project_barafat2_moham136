# .PHONY: data build clean all app

# data:
# 	python src/download_data.py

# build: data
# 	python src/build_bm25.py
# 	python src/build_semantic.py
# 	python src/RAG_pipeline.py
# 	python src/hybrid_RAG.py


# app:
# 	shiny run app/app.py

# all: build app

# clean:
# 	rm -rf data/processed/* data/merged/* models/*

.PHONY: data build clean all app check

# Ensure scripts always run from project root
PYTHON = python
ROOT_DIR := $(shell pwd)

data:
	cd $(ROOT_DIR) && $(PYTHON) src/download_data.py

build: data
	cd $(ROOT_DIR) && $(PYTHON) src/build_bm25.py
	cd $(ROOT_DIR) && $(PYTHON) src/build_semantic.py

app:
	cd $(ROOT_DIR) && shiny run app/app.py

all: build app

# Check if all required artifacts exist
check:
	@test -f data/processed/faiss_index/index_products.faiss || (echo "Missing: faiss index" && exit 1)
	@test -f data/processed/new_products.parquet            || (echo "Missing: new_products.parquet" && exit 1)
	@test -f data/processed/documents.parquet               || (echo "Missing: documents.parquet" && exit 1)
	@test -f models/bm25_model.pkl                          || (echo "Missing: bm25_model.pkl" && exit 1)
	@echo "All artifacts present."

clean:
	rm -rf data/processed/* data/raw/* models/*