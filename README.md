## SIFT: Semantically dIscerning Fact from Tale

## Setup

Create a conda environment with python 3.12

```bash
conda create -n sift python=3.12
conda activate sift
```

Clone this repo and install the required packages

```bash
git clone https://github.com/imbulana/sift.git

cd sift
python3 -m pip install -r requirements.txt
```

## Dataset

Download the dataset. See [here](data/README.md) for more information about the dataset.

```bash
cd data/raw
curl -L -o data.zip \
    https://www.kaggle.com/api/v1/datasets/download/clmentbisaillon/fake-and-real-news-dataset

unzip data.zip && rm data.zip
mv True.csv real.csv && mv Fake.csv fake.csv
cd ../..
```

The dataset, intermediate steps, and experiment results are tracked in a DVC remote storage on Google Drive.

To set up your own remote storage follow the instructions [here](https://dvc.org/doc/user-guide/data-management/remote-storage).

## Usage

To reproduce the pipeline [`dvc.yaml`](dvc.yaml) in the current workspace, run

```bash
dvc repro
```

To create a new experiment, modify the hyperparameters in [`params.yaml`](params.yaml) and the pipeline in [`dvc.yaml`](dvc.yaml) as required, then run

```bash
dvc exp run
``` 

