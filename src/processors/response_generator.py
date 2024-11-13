import json
import logging
from functools import lru_cache
from typing import Dict, Any

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client

    def retrieve_and_generate(self, prompt, kb_id, model_arn):
        return self.bedrock_client.agent_runtime_client.retrieve_and_generate(
            input={
                'text': prompt
            },
            retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': model_arn
                    # 'arn:aws:bedrock:eu-west-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                },
                'type': 'KNOWLEDGE_BASE'
            }
        )

    def invoke_prompt_flow(self, flow_id: str, flow_alias_id: str, node_name: str, node_output_name: str, prompt: str,
                           enable_trace: bool = False) -> Dict[str, Any]:

        try:
            # Construct the inputs for the flow
            # node_name = 'FlowInputNode'
            # node_output_name = 'FlowOutputNode'
            # flow_id = 'YPBN39JLIF'
            # flow_alias_id = '89D6BKWO9C'

            flow_inputs = [
                {
                    'nodeName': node_name,
                    'nodeOutputName': node_output_name,
                    'content': {
                        'document': {
                            'text': prompt
                        }
                    }
                }
            ]

            # Invoke the prompt flow
            response = self.bedrock_client.agent_runtime_client.invoke_flow(
                flowIdentifier=flow_id,
                flowAliasIdentifier=flow_alias_id,
                inputs=flow_inputs,
                enableTrace=False
            )

            # Process and return the response
            if 'output' in response:
                return response['output']
            else:
                logger.error("No output returned from prompt flow invocation.")
                return {}
        except ClientError as e:
            logger.error(f"ClientError invoking prompt flow: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error invoking prompt flow: {e}")
            return {}

    @lru_cache(maxsize=100)  # Adjust maxsize based on expected cache usage
    def generate_response(self, prompt, model_id, anthropic_version, max_tokens, temperature, relevant_kb):
        try:

            # Format the request payload using the model's native structure.
            native_request = {
                "anthropic_version": anthropic_version,  # "bedrock-2023-05-31",
                "max_tokens": max_tokens,  # 512,
                "temperature": temperature,  # 0.5,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
            }

            # Convert payload to JSON string
            payload_json = json.dumps(native_request)

            response = self.bedrock_client.runtime_client.invoke_model(
                body=payload_json,
                contentType='application/json',
                accept='application/json',
                modelId=model_id
            )

            # With this model you can retrieve a Response for a specific KB
            # response = self.retrieve_and_generate(prompt , 'hackathon-team2-eur-lex','arn:aws:bedrock:eu-west-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0')
            # print(response)

            # Read and decode the response body
            if 'body' in response:
                content_text = None
                # Read the contents of the StreamingBody
                body_content = json.loads(response.get("body").read())
                if 'content' in body_content and isinstance(body_content['content'], list):
                    content_text = body_content['content'][0].get('text', '')
                    print("Extracted Text:", content_text)
                else:
                    print("No content or invalid format in response.")
                return content_text
            else:
                logger.error("Response does not contain a valid 'body' attribute.")
                return None
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
