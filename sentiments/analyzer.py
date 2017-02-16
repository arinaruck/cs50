import nltk
import string

class Analyzer():
    """Implements sentiment analysis."""
    
    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        with open("positive-words.txt") as file_pos:
            content_pos = file_pos.readlines()
            content_pos = [x.strip() for x in content_pos] 
            for x in content_pos:
                if x.startswith(";"):
                    content_pos.remove(x)
        with open("negative-words.txt") as file_neg:            
            content_neg = file_neg.readlines()
            content_neg = [x.strip() for x in content_neg] 
            for x in content_neg:
                if x.startswith(";"):
                    content_neg.remove(x)                
           # TODO
        self.positives = content_pos
        self.negatives = content_neg
        

    def analyze(self, text):
        self.tokenizer = nltk.tokenize.TweetTokenizer()
        """Analyze text for sentiment, returning its score."""
        score = 0
        tokens = self.tokenizer.tokenize(text)
        for token in tokens:
            token = token.lower()
            if token in self.positives: score += 1
            elif token in self.negatives: score -= 1
        # TODO
        return score
