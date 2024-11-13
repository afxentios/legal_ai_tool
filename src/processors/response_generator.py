import json
import logging
from functools import lru_cache

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
