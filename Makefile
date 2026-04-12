.PHONY: data build search clean all app install

install:
	conda env create -f environment.yml
	conda activate dsci575_project

data:
	python src/download_data.py

build: data
	python src/build_bm25.py
	python src/build_semantic.py

app:
	shiny run app/app.py

all: install build app

clean:
	rm -rf data/processed/* data/merged/* models/*

