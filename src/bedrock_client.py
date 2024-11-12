import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


# Establish a client to interact with AWS Bedrock services.
class BedrockClient:
    def __init__(self, config):
        self.config = config
        self.client = self._initialize_client()

    def _initialize_client(self):
        try:
            session = boto3.Session(
                aws_access_key_id=self.config['aws']['access_key'],
                aws_secret_access_key=self.config['aws']['secret_key'],
                region_name=self.config['aws']['region']
            )
            return session.client(
                service_name='bedrock',
                endpoint_url=self.config['bedrock']['endpoint_url']
            )
        except ClientError as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

    def invoke_model(self, prompt, max_tokens=100, temperature=0.7):
        try:
            response = self.client.invoke_model(
                ModelId=self.config['bedrock']['model_id'],
                Prompt=prompt,
                MaxTokens=max_tokens,
                Temperature=temperature
            )
            return response['GeneratedText']
        except ClientError as e:
            logger.error(f"Model invocation failed: {e}")
            return None
