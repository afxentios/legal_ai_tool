import logging

from src.clients.bedrock_client import BedrockClient
from src.helpers.utils import load_config, setup_logging
from src.processors.knowledge_base import KnowledgeBase
from src.processors.query_processor import QueryProcessor
from src.processors.response_generator import ResponseGenerator


def main():
    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("Application started")
    prompt = None
    try:
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

        # # Initialize Knowledge Base
        # kb = KnowledgeBase(bucket_name=config['aws']['s3_bucket'], aws_config=config['aws'],
        #                    bedrock_client=bedrock_client.agent_client)
        #
        # # Directory containing PDF documents
        # pdf_directory = '/Users/afxentios/Desktop/BedrockPDF'
        #
        # # Check if the directory exists
        # if not os.path.isdir(pdf_directory):
        #     logger.error(f"PDF directory '{pdf_directory}' does not exist.")
        #     return
        #
        # # Upload documents
        # for file in os.listdir(pdf_directory):
        #     if file.endswith('.pdf'):
        #         file_path = os.path.join(pdf_directory, file)
        #         try:
        #             kb.upload_document(file_path)
        #         except Exception as e:
        #             logger.error(f"Failed to upload '{file}': {e}")
        #
        # # Create and sync Knowledge Base
        # try:
        #     kb.create_knowledge_base()
        #     kb.sync_knowledge_base()
        # except Exception as e:
        #     logger.error(f"Error managing Knowledge Base: {e}")
        #

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
        response = response_generator.generate_response(prompt, model_id, anthropic_version, max_tokens, temperature,
                                                        relevant_kb)
        print(response)

    except Exception as e:
        logger.error(f"Error processing query '{prompt}': {e}")
    return []


if __name__ == "__main__":
    main()
