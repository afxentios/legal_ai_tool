import logging
import os

from bedrock_client import BedrockClient
from knowledge_base import KnowledgeBase
from query_processor import QueryProcessor
from response_generator import ResponseGenerator
from utils import load_config, setup_logging


def main():
    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    # Initialize Bedrock client
    bedrock_client = BedrockClient(config)

    # List available models
    models = bedrock_client.list_available_models()
    if models:
        print("Available Foundation Models:")
        for model in models:
            print(model)
    else:
        print("No models found or an error occurred.")

    # Initialize Knowledge Base
    kb = KnowledgeBase(bucket_name=config['aws']['s3_bucket'], aws_config=config['aws'],
                       bedrock_client=bedrock_client.agent_client)

    # Directory containing PDF documents
    pdf_directory = '/Users/afxentios/Desktop/BedrockPDF'

    # Check if the directory exists
    if not os.path.isdir(pdf_directory):
        logger.error(f"PDF directory '{pdf_directory}' does not exist.")
        return

    # Upload documents
    for file in os.listdir(pdf_directory):
        if file.endswith('.pdf'):
            file_path = os.path.join(pdf_directory, file)
            try:
                kb.upload_document(file_path)
            except Exception as e:
                logger.error(f"Failed to upload '{file}': {e}")

    # Create and sync Knowledge Base
    try:
        kb.create_knowledge_base()
        kb.sync_knowledge_base()
    except Exception as e:
        logger.error(f"Error managing Knowledge Base: {e}")

    # Initialize Query Processor
    query_processor = QueryProcessor(knowledge_base=kb)

    # Initialize Response Generator
    response_generator = ResponseGenerator(bedrock_client)

    # Example usage
    query = "Who is the ECB"
    relevant_docs = query_processor.process_query(query)
    response = response_generator.generate_response(query, relevant_docs)
    print(response)

if __name__ == "__main__":
    main()
