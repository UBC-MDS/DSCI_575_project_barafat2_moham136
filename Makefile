.PHONY: data build clean all app

data:
	python src/download_data.py

build: data
	python src/build_bm25.py
	python src/build_semantic.py
	python src/RAG_pipeline.py
	python src/hybrid_RAG.py


app:
	shiny run app/app.py

all: build app

clean:
	rm -rf data/processed/* data/merged/* models/*

