import sys
import os
import io

import boto3
from boto3.s3.transfer import S3UploadFailedError
from botocore.exceptions import ClientError

def upload_data(access_key_id, secret_access_key):
    """
    Upload data to S3 Bucket for MLOps pipeline

    Args:
        
    """

    def _get_filepaths_from(path):
        file_paths = []
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        return file_paths

    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    s3_resource = session.resource('s3')

    bucket_name = 'msml605-project-sift-bucket'
    bucket = s3_resource.Bucket(bucket_name)

    directory_path = 'data/to_upload'
    filepaths = _get_filepaths_from(directory_path)
    try:
        print('Uploads about to begin...')
        for path in filepaths:
            filename = path.split('/')[-1]
            obj = bucket.Object(f'raw-data/{filename}')
            obj.upload_file(path)
            print(f'{path} as been uploaded to raw-data/{filename}')
    except S3UploadFailedError as err:
        print(f"Couldn't upload file {path} to {bucket.name}.")
        print(f'\t{err}')
        


def main():
    access_key_id = sys.argv[1]
    secret_access_key = sys.argv[2]
    upload_data(access_key_id, secret_access_key)

if __name__ == '__main__':
    main()