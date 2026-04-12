.PHONY: data build search clean all app install

install:
	pip install -r requirements.txt

data:
	python src/download_data.py

build: data
	python src/build_bm25.py
	python src/build_semantic.py

app:
	shiny run --reload app/app.py

all: install build app

clean:
	rm -rf data/processed/* data/merged/* models/*

