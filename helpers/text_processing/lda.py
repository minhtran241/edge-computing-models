import nltk

nltk.download("stopwords")
nltk.download("punkt")

import time
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Sample text data (replace this with actual data input)
sample_text = """
This is a sample text. It contains some words and punctuation, and we want to analyze it.
We are trying to demonstrate topic modeling using Latent Dirichlet Allocation (LDA).
Topic modeling is a useful technique for discovering topics from a collection of text documents.
"""

start_time = time.time()
# Tokenize and preprocess the text
tokens = word_tokenize(sample_text.lower())
stop_words = set(stopwords.words("english"))
tokens = [
    token
    for token in tokens
    if token not in stop_words and token not in string.punctuation
]

# Create a Gensim dictionary
dictionary = Dictionary([tokens])

# Create a Gensim corpus
corpus = [dictionary.doc2bow(tokens)]

# Perform LDA topic modeling
lda_model = LdaModel(corpus, num_topics=2, id2word=dictionary)

end_time = time.time()

# Print the topics
print("LDA Topics:")

# Print information about topics


# Print the top words for each topic along with their probabilities
for topic_id in range(lda_model.num_topics):
    topic_words = lda_model.show_topic(topic_id)
    print(f"Topic {topic_id + 1}:")
    for word, prob in topic_words:
        print(f"{word}: {prob:.4f}")
    print()

print(f"Execution time: {end_time - start_time:.4f} seconds")
