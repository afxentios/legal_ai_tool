import boto3
from botocore.exceptions import ClientError
import logging
import os

logger = logging.getLogger(__name__)


# Handle document ingestion and retrieval, utilizing Amazon S3 for storage.
class KnowledgeBase:
    def __init__(self, bucket_name, aws_config):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_config['access_key'],
            aws_secret_access_key=aws_config['secret_key'],
            region_name=aws_config['region']
        )

    def upload_document(self, file_path):
        file_name = None
        try:
            file_name = os.path.basename(file_path)
            self.s3_client.upload_file(file_path, self.bucket_name, file_name)
            logger.info(f"Uploaded {file_name} to {self.bucket_name}")
        except ClientError as e:
            if file_name:
                logger.error(f"Failed to upload {file_name}: {e}")
            else:
                logger.error(f"Failed to process {file_path}: {e}")

    def list_documents(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [item['Key'] for item in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"Failed to list documents: {e}")
            return []
