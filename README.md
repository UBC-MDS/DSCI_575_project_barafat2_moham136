# DSCI_575_project_barafat2_moham136

## Clone the Repository
```bash
git clone git@github.com:UBC-MDS/DSCI_575_project_barafat2_moham136.git
```

Then navigate into the project folder:
```bash
cd DSCI_575_project_barafat2_moham136
```

## Install the environment and activate it
```bash
conda env create -f environment.yml
conda activate dsci-575-project
```

## Install Make to run the Makefile
```bash
conda install -c conda-forge make
```

## Run the Makefile
```bash
make all
```

This will run the following commands in order:

1. `make data` - This will download the data from the specified URL and save it in the `data/raw` folder.
2. `make build` - This wiill run all the scripts in the `src` folder to process the data and build the model. The processed data will be saved in the `data/processed` folder and the model will be saved in the `models` folder.
3. `make app` - This will run the Shiny app located in the `app` folder. The app will be available at the URL specified in terminal after running this command.


