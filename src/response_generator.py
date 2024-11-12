import logging

logger = logging.getLogger(__name__)


# Generate responses by interacting with the Bedrock model.
class ResponseGenerator:
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client

    def generate_response(self, query, documents):
        # Combine query and documents to create a prompt
        prompt = f"Query: {query}\n\nDocuments:\n"
        for doc in documents:
            prompt += f"{doc}\n"
        logger.info(f"Generated prompt for model: {prompt}")
        response = self.bedrock_client.invoke_model(prompt)
        return response
