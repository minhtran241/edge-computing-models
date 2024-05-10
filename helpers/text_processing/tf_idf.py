import time
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize NLTK resources (download if necessary)
nltk.download("stopwords")

# Sample text data (replace this with actual data input)
sample_text = "This is a sample text. It contains some words and punctuation, and we want to analyze it."

start_time = time.time()
# Remove punctuation and convert to lowercase
preprocessed_text = sample_text.lower()

# Remove stop words
stop_words = set(stopwords.words("english"))
preprocessed_text = " ".join(
    word for word in preprocessed_text.split() if word not in stop_words
)

# Calculate TF-IDF
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform([preprocessed_text])

# Get the feature names (words)
feature_names = tfidf_vectorizer.get_feature_names_out()

# Create a dictionary to store word and its corresponding TF-IDF score
word_tfidf = {}
for word, score in zip(feature_names, tfidf_matrix.toarray()[0]):
    word_tfidf[word] = score

end_time = time.time()

# Print the TF-IDF scores for the words
print("TF-IDF Scores:")
for word, score in sorted(word_tfidf.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"{word}: {score:.4f}")

print(f"Execution time: {end_time - start_time:.4f} seconds")
