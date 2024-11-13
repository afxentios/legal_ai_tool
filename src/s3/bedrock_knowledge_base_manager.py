import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class BedrockKnowledgeBaseManager:
    """Manages Bedrock Knowledge Base creation and synchronization."""

    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client

    def create_knowledge_base(self, knowledge_base_name: str, collection_arn: str, vector_index_name: str,
                              model_arn: str, role_arn: str) -> None:
        """Creates a new Knowledge Base in Amazon Bedrock using OpenSearch Serverless as storage."""
        try:
            response = self.bedrock_client.create_knowledge_base(
                name=knowledge_base_name,
                description='Knowledge base created using OpenSearch Serverless for storage.',
                roleArn=role_arn,
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': model_arn
                    }
                },
                storageConfiguration={
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': collection_arn,
                        'fieldMapping': {
                            'metadataField': 'metadata',
                            'textField': 'text',
                            'vectorField': 'vector'
                        },
                        'vectorIndexName': vector_index_name
                    }
                }
            )
            logger.info(f"Knowledge Base '{knowledge_base_name}' created.")
            return response
        except ClientError as e:
            logger.error(f"Error creating Knowledge Base '{knowledge_base_name}': {e}")
            raise

    def sync_knowledge_base(self, knowledge_base_name: str) -> None:
        """Syncs the specified knowledge base in Bedrock."""
        try:
            response = self.bedrock_client.sync_knowledge_base(knowledgeBaseName=knowledge_base_name)
            logger.info(f"Knowledge Base '{knowledge_base_name}' synced successfully.")
            return response
        except ClientError as e:
            logger.error(f"Error syncing Knowledge Base '{knowledge_base_name}': {e}")
            raise
