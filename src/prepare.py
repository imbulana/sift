import os
import io
import sys
from datetime import datetime as dt

import yaml
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import S3UploadFailedError

SOURCES = [
    '21st century wire', 'reason.com', 'hammond news', 'alternate current radio', '21wire', '21wire.tv',
    'fox news', 'news360', 'the guardian', 'wfb', 'dispatch', 'the american mirror', 'ijreview',
    'cnsnews', 'gateway pundit', 'daily mail', 'washington examiner', 'express uk', 'ktar news',
    'cnn', 'conservative treehouse', 'daily caller', 'the blaze', 'cbc', 'tmz', 'vulture', 'kmov',
    'the hayride', 'breitbart', 'brietbart', 'gp', 'mr. conservative', 'fox 2', 'chron', 'ap', 'abc news',
    'the olympian', 'the hill', 'deadline', 'tampa bay', 'politico', 'wt', 'zero hedge', 'nyp',
    'hollywood reporter', 'wxyz', 'examiner.com', 'bbc', 'la times', 'getty', 'flickr', 'screengrab',
    'youtube', 'twitter', 'facebook', 'wall street journal', 'nbcdfw', 'nyt', 'fortune',
    'washington free beacon', 'huffington post', 'bizpac review', 'washington times', 'sltrb',
    'the college fix', 'eag news', 'cnbc', 'krtv', 'bpr', 'whitehouse.gov', 'mbr', 'wesh.com',
    'screenshot', 'boston herald', 'wnd', 'wikimedia', 'politically short', 'biz pac', 'kcs', 'espn',
    'washington post', 'national review', 'reuters', 'downtrend', 'yahoo news', 'weasel zippers',
    'dfp', 'npr', 'page six', 'rcp', 'the federalist', 'tpm', 'the detroit news', 'wbrz', 
    'ny daily news', 'myfox8', 'palm beach post', 'mrctv', 'the bureau', 'detroit free press', 
    'moonbattery', 'radar online', 'gatestone institute', 'star tribune', 'business insider', 
    'the lonely conservative', 'mediaite', 'national enquirer', 'public domain', 'ai archives',
    'the lid', 'ws', 'stars and stripes', '2nd amendment files', 'israel files', 'hammond ranch',
]

def prepare(data_path, access_key_id, secret_access_key, data_share_dist, data_share_pick, seed):
    """
    Prepare data sets for training

    Args:
        data_path (folder): Dataset folder path
        data_share_size   : Percentage of data set to be prepared in a single exection
        data_share_pick   : Subset of data set to be prepared in a single execution
    """

    def _fetch_data(s3_bucket, download_path):
        try:
            raw_data_paths = []
            for obj in s3_bucket.objects.all():
                if 'raw-data' in obj.key:
                    raw_data_paths.append(obj.key)
            for path in raw_data_paths:
                filename = path.split('/')[-1]
                s3_bucket.download_file(path, f'{download_path}/{filename}')
        except ClientError as err:
            print('Something went wrong when fetching or downloading files from S3 bucket..')
            print(f"\t{err.response['Error']['Code']}:{err.response['Error']['Message']}")

    def _collate(data_path, data_share_dist, data_share_pick, seed):
        path_real = os.path.join(data_path, 'real.csv')
        path_fake = os.path.join(data_path, 'fake.csv')

        real_df = pd.read_csv(path_real)
        fake_df = pd.read_csv(path_fake)

        # add labels
        real_df['label'] = 1
        fake_df['label'] = 0

        # Combining
        collated_df = pd.concat([real_df, fake_df], ignore_index=True)

        # drop rows w/ duplicated text
        collated_df.drop_duplicates(subset='text', keep='first', inplace=True)
        collated_df.reset_index(drop=True, inplace=True)

        # Shuffling
        collated_df = collated_df.sample(frac=1, random_state=seed).reset_index(drop=True)

        collated_df.dropna(inplace=True)
        collated_df['id'] = collated_df.index

        # Split the collated_df into it's shares and get the corresponding share pick
        share_pick_amount = int(1 / data_share_dist)
        if share_pick_amount == 1:
            return collated_df
        
        share_size = int(len(collated_df) * data_share_dist)
        start_idx = share_size * (data_share_pick - 1)
        end_idx = start_idx + share_size
        if share_pick_amount == data_share_pick: # The last pick
            return collated_df[start_idx:]
        else:   # Not the last pick
            return collated_df[start_idx:end_idx]

    
    def _get_source(row):
        label, text = row
        if label == 1:
             return 'reuters' if 'reuters' in text else 'other'

        # source mentioned at end of article?
        for source in SOURCES:
                if source in text[-100:]:
                    return source
        return 'other'

    def _clean(collated_df):
        collated_df['title'] = collated_df['title'].str.lower()
        collated_df['text'] = collated_df['text'].str.lower()
        collated_df['subject'] = collated_df['subject'].str.lower()
        collated_df['date'] = collated_df['date'].str.lower()

        return collated_df
    
    def _redact_source(row):
        label, text, source = row
        
        if label == 1: # real
            source_idx = text.find(source) + len(source)
            dash_idx = text.find('-', source_idx)

            if dash_idx == -1:
                return text.replace(source, '')
            else:
                return text[dash_idx+1:].lstrip()
        
        # label == 0 (i.e., fake)
        source_idx = text.rfind(source)
        redated = text[:source_idx].rstrip()

        return redated.replace(source, '')
    
    def _upload_data(prepared_df, s3_bucket):
        # Make csv file
        filename = f'data_{data_share_dist}_{data_share_pick}.csv'
        os.makedirs(os.path.join('data', 'prepared'), exist_ok=True)
        prepared_out = os.path.join('data', 'prepared', filename)
        prepared_df.to_csv(prepared_out, index=False)

        subdirectory = f'prepared-data/{dt.now().strftime("%Y-%m-%d")}'
        obj = s3_bucket.Object(f'{subdirectory}/{filename}')

        # Write a file to s3 bucket
        try:
            obj.upload_file(prepared_out)
        except S3UploadFailedError as err:
            print(f"Couldn't upload file {prepared_out} to {bucket.name}.")
            print(f"\t{err}")
    
    # Set up S3 bucket
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )
    s3_resource = session.resource("s3")
    bucket_name = "msml605-project-sift-bucket"
    bucket = s3_resource.Bucket(bucket_name)

    # Download raw data from S3 bucket
    _fetch_data(bucket, data_path)

    # Start cleaning data
    collated_df = _collate(data_path, data_share_dist, data_share_pick, seed)
    cleaned_df = _clean(collated_df)

    # add source column
    cleaned_df['source'] = cleaned_df[['label','text']].apply(_get_source, axis=1)

    # redact sources
    cleaned_df['text'] = cleaned_df[['label', 'text', 'source']].apply(_redact_source, axis=1)

    # Remove unnecessary columns
    prepared_df = cleaned_df[['id', 'label', 'text']]

    # Upload prepared data to S3 bucket
    _upload_data(prepared_df, bucket)


def main():
    if len(sys.argv) != 4 and len(sys.argv) != 6:
        sys.stderr.write('Arguments error.\n')
        sys.stderr.write('Usage: python src/prepare/prepare.py data-path access-key-id secret-access-key [data-share-distribution data-share-pick]')
        sys.exit(1)

    params = yaml.safe_load(open('params.yaml'))['prepare']
    seed = params['seed']

    data_path = sys.argv[1]
    access_key_id = sys.argv[2]
    secret_access_key = sys.argv[3]

    data_share_dist = 1.0
    data_share_pick = 1
    if len(sys.argv) == 6:
        data_share_dist = float(sys.argv[4])
        data_share_pick = int(sys.argv[5])

    prepare(data_path, access_key_id, secret_access_key, data_share_dist, data_share_pick, seed)

if __name__ == '__main__':
    main()
    
