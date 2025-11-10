import re

class QueryGenerator:
    def __init__(self, pattern_matcher):
        self.pattern_matcher = pattern_matcher
        
    def generate_sql(self, intent, entities, original_text):
        """Generate SQL query based on intent and entities"""
        
        if not entities.get('table'):
            return None, "Could not identify which table to query"
        
        table = entities['table']
        
        if intent == 'select_all':
            return self._generate_select_all(table, entities)
        
        elif intent == 'count':
            return self._generate_count(table, entities)
        
        elif intent == 'specific_field':
            return self._generate_specific_field(table, entities, original_text)
        
        elif intent == 'filter_numeric':
            return self._generate_filter_numeric(table, entities, original_text)
        
        elif intent == 'filter_text':
            return self._generate_filter_text(table, entities, original_text)
        
        else:
            return self._generate_select_all(table, entities)
    
    def _generate_select_all(self, table, entities):
        """Generate SELECT * query, with WHERE clause if filter exists"""
        query = f"SELECT * FROM {table}"
        
        # Add WHERE clause if filter condition exists
        if entities.get('filter_column') and entities.get('filter_value'):
            column = entities['filter_column']
            value = entities['filter_value']
            operator = entities.get('filter_operator', '=')
            
            # Quote string values, don't quote numbers
            try:
                float(value)
                query += f" WHERE {column} {operator} {value}"
            except:
                query += f" WHERE {column} {operator} '{value}'"
        
        return query, None
    
    def _generate_count(self, table, entities):
        """Generate COUNT query"""
        query = f"SELECT COUNT(*) as count FROM {table}"
        
        # Add WHERE clause if filter condition exists
        if entities.get('filter_column') and entities.get('filter_value'):
            column = entities['filter_column']
            value = entities['filter_value']
            operator = entities.get('filter_operator', '=')
            
            try:
                float(value)
                query += f" WHERE {column} {operator} {value}"
            except:
                query += f" WHERE {column} {operator} '{value}'"
        
        return query, None
    
    def _generate_specific_field(self, table, entities, original_text):
        """Generate query for specific field (e.g., 'salary of John Doe')"""
        
        if not entities.get('columns'):
            # Try to infer column from context
            text_lower = original_text.lower()
            if 'price' in text_lower:
                entities['columns'] = ['price']
            elif 'salary' in text_lower:
                entities['columns'] = ['salary']
            elif 'email' in text_lower:
                entities['columns'] = ['email']
            else:
                return None, "Could not identify which field to retrieve"
        
        columns = ', '.join(entities['columns'])
        query = f"SELECT {columns} FROM {table}"
        
        # Look for "of" or "for" pattern to extract WHERE condition
        name_match = re.search(r'(?:of|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', original_text)
        if name_match:
            name = name_match.group(1)
            query += f" WHERE name = '{name}'"
        
        return query, None
    
    def _generate_filter_numeric(self, table, entities, original_text):
        """Generate query with numeric filters"""
        
        text_lower = original_text.lower()
        query = f"SELECT * FROM {table}"
        
        # Use extracted filter condition if available
        if entities.get('filter_column') and entities.get('filter_value'):
            column = entities['filter_column']
            value = entities['filter_value']
            operator = entities.get('filter_operator', '<')
            query += f" WHERE {column} {operator} {value}"
        else:
            # Fallback: try to infer
            if 'price' in text_lower:
                column = 'price'
            elif 'salary' in text_lower:
                column = 'salary'
            elif 'quantity' in text_lower:
                column = 'stock_quantity'
            else:
                return None, "Could not determine which field to filter"
            
            if not entities.get('values'):
                return None, "Could not extract numeric value"
            
            value = entities['values'][0]
            
            if re.search(r'(greater than|more than|above|>)', text_lower):
                operator = '>'
            elif re.search(r'(less than|below|under|<)', text_lower):
                operator = '<'
            else:
                operator = '='
            
            query += f" WHERE {column} {operator} {value}"
        
        return query, None
    
    def _generate_filter_text(self, table, entities, original_text):
        """Generate query with text filters"""
        
        query = f"SELECT * FROM {table}"
        
        if entities.get('filter_column') and entities.get('filter_value'):
            column = entities['filter_column']
            value = entities['filter_value']
            query += f" WHERE {column} = '{value}'"
        
        return query, None
