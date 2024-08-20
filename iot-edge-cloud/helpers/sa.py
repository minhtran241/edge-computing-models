import os
import nltk
from typing import List, Tuple
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from helpers.common import read_txt_lines

# Download the vader lexicon (if not already downloaded)
# nltk.download("vader_lexicon")


def collect_sa_data(dir: str, filename: str = "reviews.txt") -> List[str]:
    """
    Read the reviews from the specified directory.

    Args:
        dir (str): The directory containing the reviews.

    Returns:
        List[str]: The reviews read from the directory.
    """
    reviews_file = os.path.join(dir, filename)
    return read_txt_lines(reviews_file)


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

    # Calculate the percentage of good, bad, and neutral inputs
    total_res = len(sentiments)
    good_percent = (sentiments.count("good") / total_res) * 100
    bad_percent = (sentiments.count("bad") / total_res) * 100
    neutral_percent = (sentiments.count("neutral") / total_res) * 100

    return good_percent, bad_percent, neutral_percent
