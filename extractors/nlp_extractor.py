import re
import logging
import spacy
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

logger = logging.getLogger(__name__)

class NLPExtractor:
    """Class for extracting data based on natural language instructions"""
    
    def __init__(self):
        """Initialize NLP components"""
        self.nlp = spacy.load('en_core_web_sm')
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def extract_from_text(self, text, instructions):
        """
        Extract information from text based on natural language instructions
        
        Args:
            text: The text to extract from
            instructions: Natural language instructions for what to extract
            
        Returns:
            dict: Extracted information with value and context
        """
        try:
            # Parse instructions with spaCy
            doc_instructions = self.nlp(instructions)
            
            # Extract key entities and concepts from instructions
            entities = [ent.text for ent in doc_instructions.ents]
            key_phrases = self._extract_key_phrases(instructions)
            
            # Parse the target text
            doc_text = self.nlp(text)
            
            # Extract sentences that might contain the requested information
            relevant_sentences = self._find_relevant_sentences(doc_text, key_phrases, entities)
            
            if not relevant_sentences:
                return []
            
            # Extract specific information from the relevant sentences
            extraction_results = self._extract_from_sentences(relevant_sentences, instructions)
            
            return extraction_results
            
        except Exception as e:
            logger.error(f"Error in NLP extraction: {str(e)}")
            return []
    
    def _extract_key_phrases(self, text):
        """Extract important phrases from the instructions"""
        # Tokenize and remove stop words
        tokens = word_tokenize(text.lower())
        filtered_tokens = [self.lemmatizer.lemmatize(word) for word in tokens 
                          if word.isalnum() and word not in self.stop_words]
        
        # Extract noun phrases using spaCy
        doc = self.nlp(text)
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        
        # Find important words based on POS tagging
        important_words = []
        for token in doc:
            # Keep nouns, verbs, adjectives, and proper nouns
            if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PROPN'] and token.is_alpha:
                important_words.append(token.lemma_.lower())
        
        # Combine all key phrases
        all_phrases = set(filtered_tokens + important_words + noun_phrases)
        return list(all_phrases)
    
    def _find_relevant_sentences(self, doc, key_phrases, entities):
        """Find sentences in the text that might contain the requested information"""
        relevant_sentences = []
        
        # Process each sentence
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if not sent_text:
                continue
                
            # Check for key phrases and entities
            relevance_score = 0
            
            # Check for entities
            for entity in entities:
                if entity.lower() in sent_text.lower():
                    relevance_score += 3
            
            # Check for key phrases
            for phrase in key_phrases:
                if phrase.lower() in sent_text.lower():
                    relevance_score += 1
            
            # If sentence seems relevant, add it
            if relevance_score > 0:
                relevant_sentences.append({
                    'text': sent_text,
                    'score': relevance_score
                })
        
        # Sort by relevance score (highest first)
        relevant_sentences.sort(key=lambda x: x['score'], reverse=True)
        
        # Return the top most relevant sentences
        return relevant_sentences[:5]
    
    def _extract_from_sentences(self, sentences, instructions):
        """Extract specific information from the relevant sentences"""
        results = []
        instruction_doc = self.nlp(instructions)
        
        # Determine what types of information we're looking for
        looking_for_date = any(token.lemma_ in ["date", "when", "time"] for token in instruction_doc)
        looking_for_money = any(token.lemma_ in ["amount", "money", "cost", "price", "dollar"] for token in instruction_doc)
        looking_for_person = any(token.lemma_ in ["person", "who", "name"] for token in instruction_doc)
        looking_for_location = any(token.lemma_ in ["where", "location", "place", "address"] for token in instruction_doc)
        looking_for_organization = any(token.lemma_ in ["organization", "company", "business"] for token in instruction_doc)
        
        # Process each relevant sentence
        for sentence_obj in sentences:
            sentence = sentence_obj['text']
            sent_doc = self.nlp(sentence)
            
            # Check for different entity types based on what we're looking for
            extracted_entities = []
            
            for ent in sent_doc.ents:
                if looking_for_date and ent.label_ == "DATE":
                    extracted_entities.append({"value": ent.text, "type": "DATE"})
                elif looking_for_money and ent.label_ == "MONEY":
                    extracted_entities.append({"value": ent.text, "type": "MONEY"})
                elif looking_for_person and ent.label_ == "PERSON":
                    extracted_entities.append({"value": ent.text, "type": "PERSON"})
                elif looking_for_location and ent.label_ in ["GPE", "LOC"]:
                    extracted_entities.append({"value": ent.text, "type": "LOCATION"})
                elif looking_for_organization and ent.label_ == "ORG":
                    extracted_entities.append({"value": ent.text, "type": "ORGANIZATION"})
                # Always extract numeric values as they're often important
                elif ent.label_ in ["CARDINAL", "QUANTITY", "PERCENT"]:
                    extracted_entities.append({"value": ent.text, "type": ent.label_})
            
            # If no specific entities found, try to extract based on syntax
            if not extracted_entities:
                # Look for numbers if instructions mention numeric values
                if any(word in instructions.lower() for word in ["number", "amount", "quantity", "how many"]):
                    for token in sent_doc:
                        if token.is_digit or token.like_num:
                            extracted_entities.append({"value": token.text, "type": "NUMBER"})
                
                # Look for noun phrases if nothing else works
                if not extracted_entities:
                    noun_chunks = list(sent_doc.noun_chunks)
                    if noun_chunks:
                        best_chunk = max(noun_chunks, key=lambda chunk: len(chunk.text))
                        extracted_entities.append({"value": best_chunk.text, "type": "PHRASE"})
            
            # Add extracted information to results
            for entity in extracted_entities:
                results.append({
                    "value": entity["value"],
                    "context": sentence,
                    "entity_type": entity["type"]
                })
        
        # If no structured entities were found, return the most relevant sentence
        if not results and sentences:
            most_relevant = sentences[0]['text']
            results.append({
                "value": most_relevant,
                "context": most_relevant,
                "entity_type": "SENTENCE"
            })
            
        return results