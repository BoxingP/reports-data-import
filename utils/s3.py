import os

import boto3
import botocore
from decouple import config as decouple_config

from utils.config import config


class S3(object):
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=decouple_config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=decouple_config('AWS_SECRET_ACCESS_KEY'),
            region_name=decouple_config('AWS_REGION')
        )

    def empty_s3_directory(self, s3_directory, s3_bucket):
        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_directory):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    print('Deleting %s ...' % key)
                    self.client.delete_object(Bucket=s3_bucket, Key=key)

    def upload_files_to_s3(self, local_directory, s3_directory, s3_bucket=decouple_config('AWS_S3_BUCKET'),
                           del_pre_upload=False):
        if del_pre_upload:
            self.empty_s3_directory(s3_directory=s3_directory, s3_bucket=s3_bucket)
        for root, dirs, files in os.walk(local_directory):
            for file in files:
                if config.CST_NOW_STR in file:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, local_directory)
                    s3_path = os.path.join(s3_directory, relative_path).replace('\\', '/')
                    print('Searching "%s" in "%s"' % (s3_path, s3_bucket))
                    try:
                        self.client.head_object(Bucket=s3_bucket, Key=s3_path)
                        print('File found, skipped %s' % s3_path)
                    except botocore.exceptions.ClientError:
                        print('Uploading %s ...' % s3_path)
                        self.client.upload_file(file_path, s3_bucket, s3_path)
