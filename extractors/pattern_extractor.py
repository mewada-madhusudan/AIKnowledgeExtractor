import re
import pandas as pd
from extractors.nlp_extractor import NLPExtractor


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
            df = pd.read_excel(excel_path)
            
            # Check required columns
            if 'field_name' not in df.columns:
                raise ValueError("Excel file must have a 'field_name' column")
            
            rules = []
            
            for _, row in df.iterrows():
                rule = {
                    'field_name': row['field_name'],
                    'search_pattern': row.get('search_pattern', ''),
                    'extraction_type': row.get('extraction_type', 'exact'),
                    'context_before': row.get('context_before', ''),
                    'context_after': row.get('context_after', ''),
                    'instructions': row.get('instructions', '')
                }
                
                # Validate rule
                if not rule['field_name']:
                    continue
                
                # For NLP extraction, the search pattern might be empty
                if rule['extraction_type'] != 'nlp' and not rule['search_pattern']:
                    continue
                
                rules.append(rule)
            
            return rules
        
        except Exception as e:
            raise Exception(f"Failed to load rules from Excel: {str(e)}")
    
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
        
        for page_num, page_text in document['pages'].items():
            for rule_index, rule in enumerate(rules):
                extraction_type = rule.get('extraction_type', 'exact')
                
                # Use NLP-based extraction if specified
                if extraction_type == 'nlp':
                    # Get instructions from the rule
                    instructions = rule.get('instructions', '')
                    if not instructions:
                        continue
                    
                    nlp_result = self.nlp_extractor.extract_from_text(page_text, instructions)
                    
                    if nlp_result and nlp_result.get('value'):
                        results.append({
                            'rule_index': rule_index,
                            'page_number': page_num,
                            'value': nlp_result.get('value', ''),
                            'context': nlp_result.get('context', '')
                        })
                else:
                    # Use pattern-based extraction
                    pattern = rule.get('search_pattern', '')
                    if not pattern:
                        continue
                    
                    matches = self._find_matches(page_text, pattern, rule)
                    
                    for match in matches:
                        results.append({
                            'rule_index': rule_index,
                            'page_number': page_num,
                            'value': match.get('value', ''),
                            'context': match.get('context', '')
                        })
        
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
        extraction_type = rule.get('extraction_type', 'exact')
        context_before = rule.get('context_before', '')
        context_after = rule.get('context_after', '')
        
        matches = []
        
        if extraction_type == 'exact':
            # Find exact matches
            idx = 0
            while idx < len(text):
                found_idx = text.find(pattern, idx)
                if found_idx == -1:
                    break
                
                # Extract context
                context_start = max(0, found_idx - 100)
                context_end = min(len(text), found_idx + len(pattern) + 100)
                context = text[context_start:context_end]
                
                matches.append({
                    'value': pattern,
                    'context': context
                })
                
                idx = found_idx + 1
                
        elif extraction_type == 'regex':
            # Find regex matches
            try:
                regex = re.compile(pattern)
                for match in regex.finditer(text):
                    value = match.group(0)
                    
                    # Extract context
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(text), match.end() + 100)
                    context = text[context_start:context_end]
                    
                    matches.append({
                        'value': value,
                        'context': context
                    })
            except:
                pass
                
        elif extraction_type == 'after_pattern':
            # Extract text after pattern
            idx = 0
            while idx < len(text):
                found_idx = text.find(pattern, idx)
                if found_idx == -1:
                    break
                
                # Extract text after pattern
                start_pos = found_idx + len(pattern)
                end_pos = start_pos
                
                # If context_after is specified, use it as a delimiter
                if context_after:
                    end_match = text.find(context_after, start_pos)
                    if end_match != -1:
                        end_pos = end_match
                    else:
                        # If delimiter not found, use the next 50 characters or end of line
                        end_pos = min(start_pos + 50, len(text))
                        newline_pos = text.find('\n', start_pos)
                        if newline_pos != -1 and newline_pos < end_pos:
                            end_pos = newline_pos
                else:
                    # If no delimiter, use the next 50 characters or end of line
                    end_pos = min(start_pos + 50, len(text))
                    newline_pos = text.find('\n', start_pos)
                    if newline_pos != -1 and newline_pos < end_pos:
                        end_pos = newline_pos
                
                # Extract value and context
                value = text[start_pos:end_pos].strip()
                context_start = max(0, found_idx - 50)
                context_end = min(len(text), end_pos + 50)
                context = text[context_start:context_end]
                
                matches.append({
                    'value': value,
                    'context': context
                })
                
                idx = found_idx + 1
        
        return matches