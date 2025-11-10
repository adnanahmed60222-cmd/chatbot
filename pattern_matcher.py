import re
from fuzzywuzzy import fuzz, process

class PatternMatcher:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Define intent patterns with better specificity
        self.intent_patterns = {
            'select_all': [
                r'show (all|me all|me|list)? ?(.*)',
                r'list (all)? ?(.*)',
                r'get (all)? ?(.*)',
                r'display (all)? ?(.*)',
                r'fetch (all)? ?(.*)'
            ],
            'count': [
                r'how many (.*)',
                r'count (.*)',
                r'number of (.*)'
            ],
            'specific_field': [
                r'what is (the)? ?(.*?) of (.*)',
                r'get (the)? ?(.*?) (of|for) (.*)',
                r'show (the)? ?(.*?) (of|for) (.*)',
                r'what.*?(.*?) (of|for) (.*)'
            ],
            'filter_numeric': [
                r'(.*?) (greater than|more than|above|>|>=|less than|below|under|<|<=) (\d+)',
                r'(.*?) (=|equals?|is) (\d+)',
                r'(.*?) under (\d+)',
                r'(.*?) over (\d+)'
            ],
            'filter_text': [
                r'(.*?) (where|in) (.*?) (=|is|equals?|are) ["\']?(.*?)["\']?$',
                r'(.*?) where (.*?) = (.*)',
                r'(.*?) in (.*?) category (.*)',
            ]
        }
        
        self.table_mappings = {}
        self.column_mappings = {}
        self._load_schema()
    
    def _load_schema(self):
        """Load database schema for fuzzy matching"""
        tables = self.db_manager.get_all_tables()
        for table in tables:
            self.table_mappings[table] = table
            schema = self.db_manager.get_table_schema(table)
            if schema:
                self.column_mappings[table] = [col['Field'] for col in schema]
    
    def detect_intent(self, text):
        """Detect user intent from text using pattern matching"""
        text_lower = text.lower()
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        return 'unknown'
    
    def fuzzy_match_table(self, keyword, threshold=60):
        """Find best matching table name using fuzzy matching"""
        if not self.table_mappings:
            return None
        result = process.extractOne(keyword, self.table_mappings.keys(), 
                                    scorer=fuzz.token_sort_ratio)
        if result and result[1] >= threshold:
            return result[0]
        return None
    
    def fuzzy_match_column(self, table, keyword, threshold=60):
        """Find best matching column name for a table"""
        if table not in self.column_mappings:
            return None
        columns = self.column_mappings[table]
        result = process.extractOne(keyword, columns, 
                                    scorer=fuzz.token_sort_ratio)
        if result and result[1] >= threshold:
            return result[0]
        return None
    
    def extract_entities(self, text, keywords):
        """Extract table names, column names, and values from text"""
        entities = {
            'table': None,
            'columns': [],
            'filter_column': None,
            'filter_value': None,
            'filter_operator': '=',
            'values': []
        }
        
        # Try to match table name - prioritize longer keywords (product vs duct)
        keywords_sorted = sorted(keywords, key=len, reverse=True)
        for keyword in keywords_sorted:
            table = self.fuzzy_match_table(keyword)
            if table:
                entities['table'] = table
                break
        
        # If table found, match columns
        if entities['table']:
            for keyword in keywords:
                column = self.fuzzy_match_column(entities['table'], keyword)
                if column:
                    entities['columns'].append(column)
        
        # Extract numeric values
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        entities['values'] = numbers
        
        # Extract quoted strings (for name/category matching)
        quoted = re.findall(r'["\']+(.*?)["\']', text)
        entities['values'].extend(quoted)
        
        # Extract filter conditions
        entities = self._extract_filter_conditions(text, entities)
        
        return entities
    
    def _extract_filter_conditions(self, text, entities):
        """Extract WHERE clause conditions"""
        text_lower = text.lower()
        
        # Look for common filter patterns
        # Pattern: "price under 500" or "price less than 500"
        numeric_filter = re.search(r'(\w+)\s+(under|over|less than|greater than|above|below|>|<|>=|<=)\s+(\d+)', text_lower)
        if numeric_filter:
            col_keyword = numeric_filter.group(1)
            operator = numeric_filter.group(2)
            value = numeric_filter.group(3)
            
            if entities['table']:
                filter_col = self.fuzzy_match_column(entities['table'], col_keyword)
                if filter_col:
                    entities['filter_column'] = filter_col
                    entities['filter_value'] = value
                    entities['filter_operator'] = self._normalize_operator(operator)
                    return entities
        
        # Pattern: "category = furniture" or "category is electronics"
        text_filter = re.search(r'(\w+)\s*(?:=|is|equals?|are)\s+["\']?(\w+)["\']?', text_lower)
        if text_filter:
            col_keyword = text_filter.group(1)
            value = text_filter.group(2)
            
            if entities['table']:
                filter_col = self.fuzzy_match_column(entities['table'], col_keyword)
                if filter_col:
                    entities['filter_column'] = filter_col
                    entities['filter_value'] = value
                    entities['filter_operator'] = '='
                    return entities
        
        return entities
    
    def _normalize_operator(self, op):
        """Normalize operator strings to SQL operators"""
        op = op.lower()
        if op in ['under', 'less than', 'below', '<']:
            return '<'
        elif op in ['over', 'greater than', 'above', '>']:
            return '>'
        elif op in ['>=']:
            return '>='
        elif op in ['<=']:
            return '<='
        else:
            return '='
