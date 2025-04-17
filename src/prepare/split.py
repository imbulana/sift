import os
import sys
import yaml
import pandas as pd
from sklearn.model_selection import train_test_split


def split(dataset, train_out, test_out, split, seed):
    """
    Process the input data and write the output to the output files.

    Args:
        dataset (file): Dataset path
        train_out (file): Output file for the training data set
        test_out (file): Output file for the test data set
        split (float): Test data set split ratio
        seed (float): Random seed for reproducibility
    """

    ds = pd.read_csv(dataset)
    X = ds.drop(columns=['label'])
    y = ds['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=split, stratify=y, random_state=seed
    )

    train = pd.concat([X_train, y_train], axis=1)
    test = pd.concat([X_test, y_test], axis=1)

    # save train and test data
    os.makedirs(os.path.join("data", "prepared"), exist_ok=True)

    train.to_csv(train_out, index=False)
    test.to_csv(test_out, index=False)

def main():
    params = yaml.safe_load(open("params.yaml"))["prepare"]

    if len(sys.argv) != 2:
        sys.stderr.write("Arguments error.\n")
        sys.stderr.write("Usage: python3 src/prepare.py path-to-dataset\n")
        sys.exit(1)

    test_split = params["split"]
    seed = params["seed"]

    train_out = os.path.join("data", "prepared", "train.csv")
    test_out = os.path.join("data", "prepared", "test.csv")

    dataset = sys.argv[1]
    split(
        dataset,
        train_out,
        test_out,
        test_split,
        seed,
    )


if __name__ == "__main__":
    main()
