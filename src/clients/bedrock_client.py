import json
import logging

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockClient:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.runtime_client = None
        self.agent_client = None
        self.model_id = config['bedrock']['model_id']
        self._initialize_client()

    def _initialize_client(self):
        try:
            # session = boto3.Session(
            #     aws_access_key_id=self.config['aws']['access_key'],
            #     aws_secret_access_key=self.config['aws']['secret_key'],
            #     region_name=self.config['aws']['region']
            # )

            # # Retrieve AWS credentials from environment variables
            # aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
            # aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
            # region_name = self.config['aws']['region']

            aws_access_key_id = self.config['aws']['access_key']
            aws_secret_access_key = self.config['aws']['secret_key']
            region_name = self.config['aws']['region']

            # Initialize a boto3 session with the retrieved credentials
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )

            retry_config = Config(
                region_name=self.config['aws']['region'],
                retries={
                    "max_attempts": 10,
                    "mode": "standard",
                },
            )

            self.client = session.client(
                service_name='bedrock',
                endpoint_url=self.config['bedrock']['endpoint_url']
            )
            self.runtime_client = session.client(
                service_name='bedrock-runtime'

            )
            self.agent_client = session.client(
                service_name='bedrock-agent',
                endpoint_url=self.config['bedrock']['endpoint_url']
            )
            self.agent_runtime_client = session.client(
                service_name='bedrock-agent-runtime',
                endpoint_url=self.config['bedrock']['endpoint_url']
            )
        except ClientError as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

    def invoke_model(self, input_text, max_tokens=100, temperature=0.7):
        try:
            # Prepare the request body
            body = json.dumps({
                'inputText': input_text,
                'textGenerationConfig': {
                    'maxTokenCount': max_tokens,
                    'temperature': temperature
                }
            })

            # Invoke the model
            response = self.runtime_client.invoke_model(
                body=body,
                contentType='application/json',
                accept='application/json',
                modelId=self.model_id
            )

            # Process the response
            response_body = json.loads(response['body'].read())
            return response_body
        except ClientError as e:
            logger.error(f"Model invocation failed: {e}")
            return None

    def list_available_models(self):
        """
        Retrieves and returns a list of available foundation models in Amazon Bedrock.

        Returns:
        - list: A list of dictionaries, each containing 'ModelId' and 'ModelName' of a foundation model.
        """
        try:
            response = self.client.list_foundation_models()
            # models = response.get('ModelSummaries', [])
            # model_list = [{'ModelId': model['ModelId'], 'ModelName': model['ModelName']} for model in models]
            return response.get('modelSummaries', [])
        except ClientError as e:
            logger.error(f"Failed to list foundation models: {e}")
            return []
