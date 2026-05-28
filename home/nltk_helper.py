import random
import nltk
from nltk.corpus import gutenberg
from nltk.tokenize import sent_tokenize

# Download required corpora if not already present
try:
    nltk.data.find('corpora/gutenberg')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('gutenberg', quiet=True)
    nltk.download('punkt', quiet=True)

def get_random_sentence():
    text = gutenberg.raw('austen-emma.txt') + gutenberg.raw('austen-persuasion.txt')
    sentences = sent_tokenize(text)
    return random.choice(sentences).strip()

# Example usage
if __name__ == '__main__':
    print(get_random_sentence())
