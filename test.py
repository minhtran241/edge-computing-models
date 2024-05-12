import nltk
from typing import List, Tuple
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def sentiment_analysis(review):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(review)
    print(review, score["compound"])
    if score["compound"] >= 0.05:
        return "good"
    elif score["compound"] <= -0.05:
        return "bad"
    else:
        return "neutral"


def analyze_reviews(text_list: List[str]) -> Tuple[float, float, float]:
    # Perform sentiment analysis on each review
    sentiments = [sentiment_analysis(text) for text in text_list]

    # Calculate percentage of each sentiment
    total_res = len(sentiments)
    good_percent = (sentiments.count("good") / total_res) * 100
    bad_percent = (sentiments.count("bad") / total_res) * 100
    neutral_percent = (sentiments.count("neutral") / total_res) * 100

    return good_percent, bad_percent, neutral_percent
