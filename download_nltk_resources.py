"""
Script to download required NLTK resources.
Run this script before starting the application to ensure all required resources are available.
"""

import nltk
import os

# Create directory for NLTK data
nltk_data_dir = os.path.expanduser('~/nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)

# Set NLTK data path
nltk.data.path.append(nltk_data_dir)

# Download required resources
resources = [
    'punkt',          # Tokenizer
    'stopwords',      # Common stopwords
    'wordnet',        # Lexical database
    'averaged_perceptron_tagger',  # Part-of-speech tagger
    'maxent_ne_chunker',  # Named entity chunker
    'words'           # Word list
]

print("Downloading NLTK resources...")
for resource in resources:
    try:
        print(f"Downloading {resource}...")
        nltk.download(resource, download_dir=nltk_data_dir)
        print(f"Successfully downloaded {resource}")
    except Exception as e:
        print(f"Error downloading {resource}: {e}")

print("\nNLTK resources download complete!")
print(f"Resources saved to: {nltk_data_dir}")