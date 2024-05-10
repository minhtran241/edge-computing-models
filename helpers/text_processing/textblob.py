from textblob import TextBlob

# Sample text data (replace this with actual data input)
sample_text = "This is a sample text. It contains some words and punctuation, and we want to analyze it."

# Perform sentiment analysis using TextBlob
blob = TextBlob(sample_text)
sentiment_score = blob.sentiment.polarity

# Determine sentiment label
if sentiment_score > 0:
    sentiment_label = "Positive"
elif sentiment_score < 0:
    sentiment_label = "Negative"
else:
    sentiment_label = "Neutral"

# Print sentiment analysis results
print(f"Sentiment Score: {sentiment_score}")
print(f"Sentiment Label: {sentiment_label}")
