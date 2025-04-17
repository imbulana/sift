import os
import sys
import yaml
import pandas as pd


def collate(data_path, seed):
    """
    Collate the cleaned data sets into a single dataset and shuffle

    Args:
        data_path (folder): Dataset folder path
    """

    path_real = os.path.join(data_path, "real.csv")
    path_fake = os.path.join(data_path, "fake.csv")

    real = pd.read_csv(path_real)
    fake = pd.read_csv(path_fake)

    # add labels
    real['label'] = 1
    fake['label'] = 0

    # collate and shuffle
    collated = pd.concat([real, fake], ignore_index=True)
    collated = collated.sample(frac=1, random_state=seed).reset_index(drop=True)

    collated.dropna(inplace=True)
    collated['id'] = collated.index
    collated = collated[['id', 'label', 'text']]

    # save collated dataset
    os.makedirs(os.path.join("data", "collated"), exist_ok=True)
    collated_out = os.path.join("data", "collated", "data.csv")

    collated.to_csv(collated_out, index=False)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Arguments error.\n")
        sys.stderr.write("Usage: python3 src/prepare/collate.py path-to-data\n")
        sys.exit(1)

    params = yaml.safe_load(open("params.yaml"))["prepare"]
    seed = params["seed"]

    data_path = sys.argv[1]
    collate(data_path, seed)

if __name__ == "__main__":
    main()
