import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER lexicon if not already downloaded
nltk.download("vader_lexicon")


def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of a given text using the VADER sentiment analysis tool.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The sentiment label (Positive, Negative, or Neutral).
    """
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(text)

    # Determine sentiment label based on compound score
    compound_score = sentiment_scores["compound"]
    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    return sentiment_label
