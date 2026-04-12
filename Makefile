.PHONY: data build search clean all
data:
	python src/load_data.py

build:
	python src/bm_25.py

all: data build

clean:
	rm -rf data/processed/* data/merged/* models/*