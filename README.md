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

The dataset, intermediate steps, models, and experiment results are either stored and tracked in a DVC remote storage on Google Drive.

If you have access to the remote storage, pull it with

```bash
dvc pull
```

Otherwise set up your own remote storage following the instructions [here](https://dvc.org/doc/user-guide/data-management/remote-storage).

Then download the dataset. See [here](data/README.md) for more information about the dataset.

```bash
cd data/raw
curl -L -o data.zip \
    https://www.kaggle.com/api/v1/datasets/download/clmentbisaillon/fake-and-real-news-dataset

unzip data.zip && rm data.zip
mv True.csv real.csv && mv Fake.csv fake.csv
cd ../..
```

## Experiments

### Reproduce Current Workspace

To reproduce the pipeline [`dvc.yaml`](dvc.yaml) in the current workspace, run

```bash
dvc repro
```

To create a new experiment, modify the hyperparameters in [`params.yaml`](params.yaml) and the pipeline in [`dvc.yaml`](dvc.yaml) as required, then run

```bash
dvc exp run
``` 

To easily compare experiments, install the [DVC](https://marketplace.visualstudio.com/items?itemName=Iterative.dvc) extension on VSCode.

### Experiment Queue / Parallel Runs

To run a series of experiments with different hyperparamters in [`params.yaml`](params.yaml), add them to an experiment queue

```bash
dvc exp run -S 'featurize.max_features=5,10' -S 'featurize.ngrams=1,2,3' --queue
```

Then, run the experiments in parallel locally

```bash
dvc queue start -j <number of parallel jobs>
# OR if you want to time the set of experiments
time dvc exp run --run-all -j <number of parallel jobs>
```

### Experiments on k8s Cluster (todo)

To run a set of experiments on a k8s cluster, add the experiments to the queue as above

```bash
dvc exp run -S 'featurize.max_features=5,10' -S 'featurize.ngrams=1,2,3' --queue
```

## Deployment

Build a docker image

```bash
rm -rf bulid # remove existing build (if any)

mlem build docker_dir --model models/random_forest --server fastapi --target build
docker build build -t mlem-model:latest
```

### Local w/ Docker

Run the docker container to serve the model with FastAPI

```bash
docker run -p 8080:8080 mlem-model:latest
```

Navigate to http://localhost:8080/docs to see the OpenAPI spec.

See [here](https://mlem.ai/doc/user-guide/building/docker) more instructions and other build and serve options.

### Minikube

Install minikube and kubectl following the instructions [here](https://minikube.sigs.k8s.io/docs/start/) and [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/).

Then start a minkube cluser and point the shell to minikube's docker-daemon

```bash
minikube start
eval $(minikube -p minikube docker-env)
```

Build the docker image in minikube

```bash
docker build build -t mlem-model:latest
```

For isolation, create a k8s [namespace](k8s/local/namespace.yaml) named `sift-app`

```bash
kubectl apply -f k8s/local/namespace.yaml
```
Then create a new context for the namespace and switch to it

```bash
kubectl config set-context sift-app --namespace sift-app --cluster=minikube --user minikube
kubectl config use-context sift-app
```
Run the following the to see all contexts and to verify that the current context is `sift-app`

```bash
kubectl config get-contexts
```

Create the deployment found in [`k8s/local/deployment.yaml`](k8s/local/deployment.yaml)

```bash
kubectl apply -f k8s/local/deployment.yaml
```

Verify that the deployment is successful by running

```bash
kubectl get deployments
```

Access the app by creating the service in [`k8s/local/service.yaml`](k8s/local/service.yaml)

```bash
kubectl apply -f k8s/local/service.yaml
minikube service sift-app-service -n sift-app --url
```

When done, clean up all resources in the namespace

```bash
kubectl delete namespace sift-app
```

To delete the context from the config

```bash
kubectl config delete-context sift-app-local
kubectl config use-context minikube # switch to default
```

## Model Registry

Models are versioned within this repository using git tags. However the model files are stored in the remote DVC repository.

First store the repo url to a shell variable

```bash
export REPO=https://github.com/imbulana/sift
```

To see registered models, run

```bash
gto show
```

To register a new model, run

```bash
gto register <path_to_model> --repo $REPO
```