import os
import sys
from datetime import datetime as dt

import yaml
import pandas as pd
from sklearn.model_selection import train_test_split
import boto3
from botocore.exceptions import ClientError

def split(data_path, access_key_id, secret_access_key, train_out, test_out, split, seed):
    """
    Process the input data and write the output to the output files.

    Args:
        data_path (string): path to data files
        access_key_id (string): 
        secret_access_key (string): 
        train_out (string): Output file for the training data set
        test_out (string): Output file for the test data set
        split (float): Test data set split ratio
        seed (float): Random seed for reproducibility
    """

    def _find_latest_data_paths(prepared_data_paths):
        latest_date = None
        for dpath in prepared_data_paths:
            _, date_str, _ = dpath.split('/')
            parsed_date = dt.strptime(date_str, '%Y-%m-%d').date()
            if latest_date == None or latest_date < parsed_date:
                latest_date = parsed_date
        
        latest_date = str(latest_date)
        latest_prepared_data_paths = []
        for dpath in prepared_data_paths:
            if latest_date in dpath:
                latest_prepared_data_paths.append(dpath)
        
        return latest_prepared_data_paths

    def _fetch_data(s3_bucket, download_path, data_paths):
        for path in data_paths:
            file_name = path.split('/')[-1]
            s3_bucket.download_file(path, f'{download_path}/{file_name}')

    def _get_filepaths_from(path):
        file_paths = []
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        return file_paths

    def _combine_data_to_df(download_path):
        filepaths = _get_filepaths_from(download_path)
        main_df = pd.read_csv(filepaths[0])
        for path in filepaths[1:]:
            next_df = pd.read_csv(path)
            main_df = pd.concat([main_df, next_df])
        main_df.reset_index(inplace=True)

        return main_df

    # Connect to AWS
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    # Connect to S3
    s3_resource = session.resource("s3")
    bucket_name = "msml605-project-sift-bucket"
    bucket = s3_resource.Bucket(bucket_name)

    # Fetch data from S3 and download to data/prepared
    try:
        prepared_data_paths = []
        for obj in bucket.objects.all():
            if 'prepared-data' in obj.key:
                prepared_data_paths.append(obj.key)
        latest_prepared_data_paths = _find_latest_data_paths(prepared_data_paths)
        _fetch_data(bucket, data_path, latest_prepared_data_paths)
    except ClientError as err:
        print(f"Couldn't list the objects in bucket {bucket.name}.")
        print(f"\t{err.response['Error']['Code']}:{err.response['Error']['Message']}")

    # Combine all data files into a single df
    data_df = _combine_data_to_df(data_path)

    # Split
    X = data_df.drop(columns=['label'])
    y = data_df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=split, stratify=y, random_state=seed
    )

    train = pd.concat([X_train, y_train], axis=1)
    test = pd.concat([X_test, y_test], axis=1)

    # save train and test data
    os.makedirs(os.path.join("data", "split"), exist_ok=True)

    train.to_csv(train_out, index=False)
    test.to_csv(test_out, index=False)


def main():
    params = yaml.safe_load(open("params.yaml"))["prepare"]

    if len(sys.argv) != 4:
        sys.stderr.write("Arguments error.\n")
        sys.stderr.write("Usage: python3 src/split.py path-to-data access-key-id secret-access-key\n")
        sys.exit(1)

    test_split = params["split"]
    seed = params["seed"]

    train_out = os.path.join("data", "split", "train.csv")
    test_out = os.path.join("data", "split", "test.csv")

    data_path = sys.argv[1]
    access_key_id = sys.argv[2]
    secret_access_key = sys.argv[3]
    split(
        data_path,
        access_key_id,
        secret_access_key,
        train_out,
        test_out,
        test_split,
        seed,
    )

if __name__ == '__main__':
    main()