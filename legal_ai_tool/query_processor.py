import logging

logger = logging.getLogger(__name__)


class QueryProcessor:
    def __init__(self, knowledge_bases):
        self.knowledge_bases = knowledge_bases

    def process_query(self, query):
        try:
            # Determine the appropriate KB based on the query content
            if 'german law' in query.lower():
                kb_name = 'hackathon-team2-legal-acts-germany'
            elif 'austrian law' in query.lower():
                kb_name = 'hackathon-team2-legal-acts-austria'
            else:
                kb_name = 'hackathon-team2-eur-lex'
            return kb_name
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            return []
