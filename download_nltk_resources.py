"""
Script to download required NLTK resources.
Run this script before starting the application to ensure all required resources are available.
"""
import os
import nltk

def download_nltk_resources():
    """Download required NLTK resources"""
    
    # Create directory for NLTK data
    nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Set NLTK data path
    nltk.data.path.append(nltk_data_dir)
    
    # List of resources to download
    resources = [
        ('punkt', 'tokenizers/punkt'),
        ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger'),
        ('stopwords', 'corpora/stopwords'),
        ('wordnet', 'corpora/wordnet')
    ]
    
    # Download each resource
    for resource, path in resources:
        try:
            nltk.download(resource, download_dir=nltk_data_dir)
            print(f"Downloaded {resource} to {os.path.join(nltk_data_dir, path)}")
        except Exception as e:
            print(f"Error downloading {resource}: {str(e)}")
    
    print("NLTK resources download complete.")

if __name__ == "__main__":
    download_nltk_resources()