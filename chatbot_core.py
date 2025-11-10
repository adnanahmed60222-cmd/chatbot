from database import DatabaseManager
from preprocessor import TextPreprocessor
from pattern_matcher import PatternMatcher
from query_generator import QueryGenerator


class Chatbot:
    def __init__(self):
        self.db = DatabaseManager()
        self.preprocessor = TextPreprocessor()
        self.pattern_matcher = None
        self.query_generator = None
        self.is_connected = False

    def initialize(self):
        """Initialize chatbot and connect to database"""
        if self.db.connect():
            self.pattern_matcher = PatternMatcher(self.db)
            self.query_generator = QueryGenerator(self.pattern_matcher)
            self.is_connected = True
            return True
        return False

    def process_message(self, user_message):
        """Process user message and return response"""

        if not self.is_connected:
            return {
                'success': False,
                'message': 'Chatbot is not connected to database',
                'data': None
            }

        try:
            # Step 1: Preprocess input
            processed = self.preprocessor.preprocess(user_message)
            keywords = processed['keywords']

            # Step 2: Detect intent
            intent = self.pattern_matcher.detect_intent(user_message)

            # Step 3: Extract entities (improved)
            entities = self.pattern_matcher.extract_entities(user_message, keywords)

            # Step 4: Generate SQL query
            sql_query, error = self.query_generator.generate_sql(intent, entities, user_message)

            if error:
                return {
                    'success': False,
                    'message': error,
                    'data': None,
                    'debug': {
                        'intent': intent,
                        'entities': entities,
                        'keywords': keywords
                    }
                }

            # Step 5: Execute query
            results = self.db.execute_query(sql_query)

            if results is None:
                return {
                    'success': False,
                    'message': 'Error executing query',
                    'data': None,
                    'sql': sql_query,
                    'debug': {
                        'intent': intent,
                        'entities': entities,
                        'keywords': keywords
                    }
                }

            # Step 6: Format response
            response_text = self._format_response(results, intent)

            return {
                'success': True,
                'message': response_text,
                'data': results,
                'sql': sql_query,
                'count': len(results),
                'debug': {
                    'intent': intent,
                    'entities': entities,
                    'keywords': keywords
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'data': None
            }

    def _format_response(self, results, intent):
        """Format database results into human-readable text"""
        if not results:
            return "No results found for your query."

        if intent == 'count':
            count = results[0].get('count', len(results))
            return f"Found {count} records."

        # If specific field was requested and a single row returned, you could format values
        if len(results) == 1 and len(results[0]) <= 3:
            # Compact single-record summary
            kv = ', '.join(f"{k}: {v}" for k, v in results[0].items())
            return f"Found 1 result: {kv}"

        return f"Found {len(results)} results."

    def close(self):
        """Close database connection if open"""
        try:
            if self.db and getattr(self.db, 'connection', None):
                if self.db.connection.is_connected():
                    self.db.connection.close()
                print("Database connection closed.")
        except Exception as e:
            print(f"Error closing database: {e}")
