import re
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class NLPExtractor:
    """Class for extracting data based on natural language instructions"""
    
    def __init__(self):
        """Initialize NLP components"""
        try:
            # Load spaCy model
            self.nlp = spacy.load('en_core_web_sm')
            
            # Initialize NLTK components
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            print(f"Warning: Failed to initialize NLP components: {str(e)}")
            self.nlp = None
            self.lemmatizer = None
            self.stop_words = None
    
    def extract_from_text(self, text, instructions):
        """
        Extract information from text based on natural language instructions
        
        Args:
            text: The text to extract from
            instructions: Natural language instructions for what to extract
            
        Returns:
            dict: Extracted information with value and context
        """
        if not self.nlp:
            return {'value': '', 'context': 'NLP components not initialized'}
        
        # Process the text and instructions with spaCy
        doc = self.nlp(text)
        instructions_doc = self.nlp(instructions.lower())
        
        # Extract key phrases from instructions
        key_phrases = self._extract_key_phrases(instructions)
        
        # Get entities from instructions
        entities = [ent.text.lower() for ent in instructions_doc.ents]
        
        # Find sentences that might contain the requested information
        relevant_sentences = self._find_relevant_sentences(doc, key_phrases, entities)
        
        if not relevant_sentences:
            return {'value': '', 'context': 'No relevant information found'}
        
        # Extract specific information from the relevant sentences
        extracted_info = self._extract_from_sentences(relevant_sentences, instructions)
        
        if not extracted_info:
            # If no specific info found, return the most relevant sentence
            most_relevant = relevant_sentences[0]
            return {
                'value': most_relevant.text.strip(),
                'context': most_relevant.text.strip()
            }
        
        return extracted_info
    
    def _extract_key_phrases(self, text):
        """Extract important phrases from the instructions"""
        # Convert to lowercase and tokenize
        text = text.lower()
        doc = self.nlp(text)
        
        key_phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            # Filter out stop words
            phrase = ' '.join([token.text for token in chunk if token.text.lower() not in self.stop_words])
            if phrase:
                key_phrases.append(phrase)
        
        # Extract verbs with their objects
        for token in doc:
            if token.pos_ == 'VERB':
                phrase_parts = [token.text]
                for child in token.children:
                    if child.dep_ in ('dobj', 'pobj'):
                        phrase_parts.append(child.text)
                
                phrase = ' '.join(phrase_parts)
                key_phrases.append(phrase)
        
        # Extract specific action phrases like "extract", "find", "locate"
        action_verbs = ['extract', 'find', 'locate', 'identify', 'get']
        for token in doc:
            if token.lemma_.lower() in action_verbs:
                # Get the object of this action verb
                for child in token.children:
                    if child.dep_ in ('dobj', 'pobj'):
                        phrase = child.text
                        
                        # Include any adjectives or modifiers
                        for grandchild in child.children:
                            if grandchild.dep_ in ('amod', 'compound'):
                                phrase = f"{grandchild.text} {phrase}"
                        
                        if phrase:
                            key_phrases.append(phrase)
        
        # Get named entities
        for ent in doc.ents:
            key_phrases.append(ent.text)
        
        # Clean up and deduplicate
        key_phrases = [phrase.strip() for phrase in key_phrases if len(phrase.strip()) > 1]
        key_phrases = list(set(key_phrases))
        
        return key_phrases
    
    def _find_relevant_sentences(self, doc, key_phrases, entities):
        """Find sentences in the text that might contain the requested information"""
        # Split into sentences
        sentences = list(doc.sents)
        
        # Score each sentence based on key phrases and entities
        sentence_scores = []
        
        for sentence in sentences:
            sentence_text = sentence.text.lower()
            score = 0
            
            # Check for key phrases
            for phrase in key_phrases:
                if phrase.lower() in sentence_text:
                    score += 3
                elif all(word in sentence_text for word in phrase.lower().split()):
                    score += 2
            
            # Check for entities
            for entity in entities:
                if entity in sentence_text:
                    score += 2
            
            # Check for specific entity types that might be relevant
            for ent in sentence.ents:
                if ent.label_ in ['DATE', 'TIME', 'MONEY', 'PERCENT', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
                    score += 1
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC']:
                    score += 1
            
            sentence_scores.append((sentence, score))
        
        # Sort by score and return the most relevant sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top sentences with a score above 0
        return [sent for sent, score in sentence_scores if score > 0]
    
    def _extract_from_sentences(self, sentences, instructions):
        """Extract specific information from the relevant sentences"""
        instructions_lower = instructions.lower()
        
        # Check if we're looking for specific entity types
        entity_type_mapping = {
            'date': ['DATE', 'TIME'],
            'time': ['TIME', 'DATE'],
            'money': ['MONEY', 'CARDINAL'],
            'amount': ['MONEY', 'QUANTITY', 'CARDINAL'],
            'percentage': ['PERCENT'],
            'number': ['CARDINAL', 'ORDINAL', 'QUANTITY'],
            'person': ['PERSON'],
            'name': ['PERSON', 'ORG'],
            'organization': ['ORG'],
            'company': ['ORG'],
            'location': ['LOC', 'GPE'],
            'address': ['LOC', 'GPE'],
            'city': ['GPE'],
            'country': ['GPE']
        }
        
        target_entity_types = []
        for key, entity_types in entity_type_mapping.items():
            if key in instructions_lower:
                target_entity_types.extend(entity_types)
        
        # Look for specific entities in the sentences
        if target_entity_types:
            for sentence in sentences:
                for ent in sentence.ents:
                    if ent.label_ in target_entity_types:
                        # Return context with the sentence
                        return {
                            'value': ent.text,
                            'context': sentence.text
                        }
        
        # Check for specific patterns based on the instructions
        
        # Date patterns
        if any(word in instructions_lower for word in ['date', 'when', 'time']):
            date_pattern = r'\b(?:\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{2,4}|\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{2,4})\b'
            for sentence in sentences:
                matches = re.findall(date_pattern, sentence.text, re.IGNORECASE)
                if matches:
                    return {
                        'value': matches[0],
                        'context': sentence.text
                    }
        
        # Amount patterns
        if any(word in instructions_lower for word in ['amount', 'total', 'sum', 'cost', 'price']):
            amount_pattern = r'\$\s*\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s*(?:dollars|USD|€|£|euros|pounds)'
            for sentence in sentences:
                matches = re.findall(amount_pattern, sentence.text)
                if matches:
                    return {
                        'value': matches[0],
                        'context': sentence.text
                    }
        
        # ID or reference number patterns
        if any(word in instructions_lower for word in ['id', 'number', 'reference', 'code']):
            id_pattern = r'\b(?:[A-Z0-9]{2,}-[A-Z0-9]{2,}(?:-[A-Z0-9]{2,})*|[A-Z]{2,}\d{4,}|\d{4,}[A-Z]{2,}|[A-Z]{2}\d{6,})\b'
            for sentence in sentences:
                matches = re.findall(id_pattern, sentence.text)
                if matches:
                    return {
                        'value': matches[0],
                        'context': sentence.text
                    }
        
        # If no specific information was found, return the most relevant sentence
        if sentences:
            most_relevant = sentences[0]
            return {
                'value': most_relevant.text.strip(),
                'context': most_relevant.text.strip()
            }
        
        return None