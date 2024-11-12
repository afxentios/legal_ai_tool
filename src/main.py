import logging
from utils import load_config, setup_logging
from bedrock_client import BedrockClient
from knowledge_base import KnowledgeBase
from query_processor.py import QueryProcessor
from response_generator import ResponseGenerator


def main():
    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("Application started")

    # Initialize Bedrock client
    bedrock_client = BedrockClient(config)

    # Initialize Knowledge Base
    kb = KnowledgeBase(bucket_name='your-s3-bucket-name', aws_config=config['aws'])

    # Initialize Query Processor
    query_processor = QueryProcessor(knowledge_base=kb)

    # Initialize Response Generator
    response_generator = ResponseGenerator(bedrock_client=bedrock_client)

    # Example usage
    query = "Who is the ECB?"
    relevant_docs = query_processor.process_query(query)
    response = response_generator.generate_response(query, relevant_docs)
    print(response)
