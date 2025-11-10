import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class TextPreprocessor:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 
                               'is', 'are', 'was', 'were'}
    
    def clean_text(self, text):
        """Clean and normalize input text"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text):
        """Tokenize text into words"""
        try:
            tokens = word_tokenize(text)
        except:
            tokens = text.split()
        return tokens
    
    def remove_stopwords(self, tokens):
        """Remove common stopwords"""
        return [word for word in tokens if word not in self.stop_words]
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        keywords = self.remove_stopwords(tokens)
        return keywords
    
    def preprocess(self, text):
        """Full preprocessing pipeline"""
        return {
            'original': text,
            'cleaned': self.clean_text(text),
            'keywords': self.extract_keywords(text)
        }
