import re
import logging
import pandas as pd
from collections import defaultdict
from extractors.nlp_extractor import NLPExtractor

logger = logging.getLogger(__name__)

class PatternExtractor:
    """Class for extracting data based on patterns and instructions"""
    
    def __init__(self):
        """Initialize extractor components"""
        self.nlp_extractor = NLPExtractor()
    
    def load_rules_from_excel(self, excel_path):
        """
        Load extraction rules from an Excel file
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            list: List of extraction rules
        """
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            
            # Check required columns
            required_cols = ['field_name', 'search_pattern']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns in Excel file: {', '.join(missing_cols)}")
            
            # Convert to rules list
            rules = []
            for _, row in df.iterrows():
                rule = {
                    'field_name': row['field_name'],
                    'search_pattern': row['search_pattern'],
                    'context_before': row.get('context_before', ''),
                    'context_after': row.get('context_after', ''),
                    'extraction_type': row.get('extraction_type', 'exact'),
                    'instructions': row.get('instructions', '')
                }
                rules.append(rule)
            
            return rules
        
        except Exception as e:
            logger.error(f"Error loading rules from Excel: {str(e)}")
            raise
    
    def extract_from_document(self, document, rules):
        """
        Extract data from a document based on rules
        
        Args:
            document: Document data structure 
            rules: List of extraction rules
            
        Returns:
            list: List of extraction results
        """
        results = []
        
        for rule in rules:
            field_name = rule['field_name']
            search_pattern = rule['search_pattern']
            
            # Search for pattern in each page
            for page_num, content in document['pages'].items():
                if not content:
                    continue
                
                # Find matches
                matches = self._find_matches(content, search_pattern, rule)
                
                if matches:
                    for match in matches:
                        result = {
                            'document_id': document['id'],
                            'document_name': document['name'],
                            'page_number': page_num,
                            'field_name': field_name,
                            'value': match['value'],
                            'context': match['context']
                        }
                        results.append(result)
        
        return results
    
    def _find_matches(self, text, pattern, rule):
        """
        Find matches in text based on pattern and rule
        
        Args:
            text: The text to search in
            pattern: The search pattern
            rule: The extraction rule with context and instructions
            
        Returns:
            list: List of matches with value and context
        """
        matches = []
        
        try:
            # Determine extraction type
            extraction_type = rule.get('extraction_type', 'exact').lower()
            
            if extraction_type == 'nlp':
                # Use NLP-based extraction with natural language instructions
                # If pattern is empty but instructions exist, use only instructions
                instructions = rule.get('instructions', '')
                if not instructions and pattern:
                    # If no specific instructions, use the pattern as instructions
                    instructions = f"Extract {pattern} from the text"
                
                # Use our NLP extractor with the instructions
                nlp_results = self.nlp_extractor.extract_from_text(text, instructions)
                
                # Convert NLP results to the expected format
                for result in nlp_results:
                    matches.append({
                        'value': result['value'],
                        'context': result['context']
                    })
            
            elif extraction_type == 'regex':
                # Use regex pattern directly
                regex = re.compile(pattern, re.IGNORECASE)
                for match in regex.finditer(text):
                    value = match.group(0)
                    
                    # Get context around match
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(text), match.end() + 100)
                    context = text[start_pos:end_pos]
                    
                    matches.append({
                        'value': value,
                        'context': context
                    })
            
            elif extraction_type == 'after_pattern':
                # Extract content after pattern
                regex = re.compile(f"{re.escape(pattern)}(.*?)(?:\n|$)", re.IGNORECASE | re.DOTALL)
                for match in regex.finditer(text):
                    value = match.group(1).strip()
                    
                    # Get context around match
                    start_pos = max(0, match.start() - 50)
                    end_pos = min(len(text), match.end() + 50)
                    context = text[start_pos:end_pos]
                    
                    matches.append({
                        'value': value,
                        'context': context
                    })
            
            else:  # 'exact' or default
                # Look for exact match
                positions = [m.start() for m in re.finditer(re.escape(pattern), text, re.IGNORECASE)]
                for pos in positions:
                    # Get context around match
                    start_pos = max(0, pos - 50)
                    end_pos = min(len(text), pos + len(pattern) + 50)
                    context = text[start_pos:end_pos]
                    
                    matches.append({
                        'value': pattern,
                        'context': context
                    })
        
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            # Return empty list on error
        
        return matches
