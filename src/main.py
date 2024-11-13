import logging
import os

from src.clients.bedrock_client import BedrockClient
from src.helpers.utils import load_config, setup_logging
from src.processors.knowledge_base import KnowledgeBase
from src.processors.query_processor import QueryProcessor
from src.processors.response_generator import ResponseGenerator
from src.s3.s3_manager import S3Manager
from src.s3.bedrock_knowledge_base_manager import BedrockKnowledgeBaseManager


def setup_s3_bucket_and_upload_pdfs(config):
    """Sets up S3 bucket and uploads PDF files from a local directory."""
    logger = logging.getLogger(__name__)
    s3_manager = S3Manager(config['aws'])

    bucket_name = config['aws']['s3_bucket']
    pdf_directory = '/Users/afxentios/Desktop/BedrockPDF'

    # Create S3 bucket
    s3_manager.create_bucket(bucket_name)

    # Upload PDFs to S3
    if not os.path.isdir(pdf_directory):
        logger.error(f"PDF directory '{pdf_directory}' does not exist.")
        return
    s3_manager.upload_pdfs(bucket_name, pdf_directory)


def setup_bedrock_knowledge_base(config, bedrock_client):
    """Sets up and syncs a knowledge base in Amazon Bedrock using data from S3."""
    logger = logging.getLogger(__name__)

    bucket_name = config['aws']['s3_bucket']
    knowledge_base_name = config['aws']['knowledge_base_name']
    model_arn = config['aws']['model_arn']
    role_arn = config['aws']['role_arn']

    # Initialize Bedrock Knowledge Base Manager
    bedrock_kb_manager = BedrockKnowledgeBaseManager(bedrock_client)

    # Create and sync Knowledge Base
    bedrock_kb_manager.create_knowledge_base(knowledge_base_name, bucket_name, model_arn, role_arn)
    bedrock_kb_manager.sync_knowledge_base(knowledge_base_name)


def main():
    # Load configuration and set up logging
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("Application started")
    prompt = None

    try:
        # Initialize Bedrock client
        bedrock_client = BedrockClient(config)

        # # Call S3 bucket and PDF upload functionality
        # setup_s3_bucket_and_upload_pdfs(config)
        #
        # # # Call Bedrock Knowledge Base setup functionality
        # setup_bedrock_knowledge_base(config, bedrock_client.agent_client)

        # List available models in Bedrock
        models = bedrock_client.list_available_models()
        if models:
            print("Available Foundation Models:")
            for model in models:
                print(model)
        else:
            print("No models found or an error occurred.")

        # Initialize Knowledge Bases
        knowledge_bases = {
            'hackathon-team2-eur-lex': KnowledgeBase('eur-lex', config['aws'], bedrock_client),
            'hackathon-team2-legal-acts-austria': KnowledgeBase('legal-acts-austria', config['aws'], bedrock_client),
            'hackathon-team2-legal-acts-germany': KnowledgeBase('legal-acts-germany', config['aws'], bedrock_client)
        }

        # Initialize Query Processor
        query_processor = QueryProcessor(knowledge_bases)

        # Initialize Response Generator
        response_generator = ResponseGenerator(bedrock_client)

        # Example usage
        prompt = "What are the regulations for data protection in German law?"
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        anthropic_version = "bedrock-2023-05-31"
        max_tokens = 512
        temperature = 0.5
        relevant_kb = query_processor.process_query(prompt)
        response = response_generator.generate_response(
            prompt, model_id, anthropic_version, max_tokens, temperature, relevant_kb
        )
        print(response)

    except Exception as e:
        logger.error(f"Error processing query '{prompt}': {e}")
    return []


if __name__ == "__main__":
    main()
