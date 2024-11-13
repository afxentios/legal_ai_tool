import boto3
import os
from botocore.exceptions import ClientError, BotoCoreError
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, bucket_name, aws_config, bedrock_client):
        try:
            self.bucket_name = bucket_name
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_config['access_key'],
                aws_secret_access_key=aws_config['secret_key'],
                region_name=aws_config['region']
            )
            self.bedrock_client = bedrock_client
            self.kb_name = aws_config['knowledge_base_name']
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            raise

    def upload_document(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            self.s3_client.upload_file(file_path, self.bucket_name, file_name)
            logger.info(f"Uploaded {file_name} to {self.bucket_name}")
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            raise

    def create_knowledge_base(self):
        try:
            response = self.bedrock_client.create_knowledge_base(
                name=self.kb_name,
                description='Description of my CBC knowledge base',
                roleArn='arn:aws:iam::our-account-id:role/our-role-name',
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': 'arn:aws:bedrock:your-region::model/our-model-id'
                    }
                },
                storageConfiguration={
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': 'arn:aws:aoss:our-region:our-account-id:collection/our-collection-name',
                        'fieldMapping': {
                            'metadataField': 'metadata',
                            'textField': 'text',
                            'vectorField': 'vector'
                        },
                        'vectorIndexName': 'our-vector-index-name'
                    }
                }
            )
            logger.info(f"Knowledge Base '{self.kb_name}' created successfully.")
            return response
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error creating Knowledge Base '{self.kb_name}': {e}")
            raise

    def sync_knowledge_base(self):
        try:
            response = self.bedrock_client.sync_knowledge_base(
                knowledgeBaseName=self.kb_name
            )
            logger.info(f"Knowledge Base '{self.kb_name}' synced successfully.")
            return response
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error syncing Knowledge Base '{self.kb_name}': {e}")
            raise
