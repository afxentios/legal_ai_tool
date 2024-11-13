import boto3
import os
from botocore.exceptions import ClientError
from typing import List


class S3Manager:
    """Handles creation of S3 buckets and uploading files."""

    def __init__(self, config):
        self.s3_client = boto3.client('s3', region_name=config['region'],
                                      aws_access_key_id=config['access_key'],
                                      aws_secret_access_key=config['secret_key']
                                      )
        self.region = config['region']

    def create_bucket(self, bucket_name: str) -> None:
        """Creates an S3 bucket in the specified region."""
        try:
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            print(f"Bucket {bucket_name} created.")
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            raise

    def upload_pdfs(self, bucket_name: str, directory: str) -> None:
        """Uploads all PDF files from a local directory to an S3 bucket."""
        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):
                file_path = os.path.join(directory, filename)
                try:
                    self.s3_client.upload_file(file_path, bucket_name, filename)
                    print(f"Uploaded {filename} to {bucket_name}.")
                except ClientError as e:
                    print(f"Error uploading {filename}: {e}")
                    raise
