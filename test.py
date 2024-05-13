import os
import nltk
from typing import List, Tuple
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")


def _sa_algo(text: str) -> str:
    """
    Perform sentiment analysis on the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The sentiment of the review.
    """
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    if score["compound"] >= 0.05:
        return "good"
    elif score["compound"] <= -0.05:
        return "bad"
    else:
        return "neutral"


def sentiment_analysis(texts: List[str]) -> Tuple[float, float, float]:
    # Perform sentiment analysis on each text
    sentiments = [_sa_algo(text) for text in texts]

    # Calculate percentage of each sentiment
    total_res = len(sentiments)
    good_percent = (sentiments.count("good") / total_res) * 100
    bad_percent = (sentiments.count("bad") / total_res) * 100
    neutral_percent = (sentiments.count("neutral") / total_res) * 100

    return good_percent, bad_percent, neutral_percent


print(
    sentiment_analysis(
        [
            "I love this product",
            "I hate this product",
            "I am neutral about this product",
        ]
    )
)  # (33.33333333333333, 33.33333333333333, 33.33333333333333)
