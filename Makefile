.PHONY: data build search clean all app
data:
	python src/load_data.py

build: data
	python src/bm_25.py

app:
	shiny run --reload app/app.py

all: build app

clean:
	rm -rf data/processed/* data/merged/* models/*