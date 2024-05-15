# # Generate random keywords file (about 100 keywords) from the text using the Aho-Corasick automaton for testing.


# import ahocorasick
# import os
# import random
# import string
# from typing import List, Tuple


# def generate_random_keywords(
#     text: str, keyword_len: int, num_keywords: int = 100
# ) -> List[str]:
#     """
#     Generate random keywords from the text using the Aho-Corasick automaton.

#     Args:
#     - text (str): Input text to generate keywords.
#     - keyword_len (int): Length of the keyword.
#     - num_keywords (int): Number of keywords to generate.

#     Returns:
#     - list: List of generated keywords.
#     """
#     keywords = set()
#     while len(keywords) < num_keywords:
#         start = random.randint(0, len(text) - keyword_len)
#         keyword = text[start : start + keyword_len]
#         keywords.add(keyword)
#     return list(keywords)


# def generate_random_keywords_2(
#     alphabet: List[str], keyword_len: int, num_keywords: int = 50
# ):
#     keywords = []
#     while len(keywords) < num_keywords:
#         keyword = "".join(random.choices(alphabet, k=keyword_len))
#         keywords.append(keyword)
#     return keywords


# with open("data/ac/small/dna.txt", "r") as file:
#     text = file.read()

# keywords1 = generate_random_keywords_2(["A", "C", "G", "T"], 100, 400)
# keywords2 = generate_random_keywords(text, 100, 400)

# keywords = keywords1 + keywords2

# # Append the keywords to the file
# with open("data/ac/small/keywords.txt", "a") as file:
#     for keyword in keywords:
#         file.write(keyword + "\n")

import random

# Read reviews file and get n random reviews
with open("reviews.txt", "r") as file:
    neg_reviews = file.readlines()

with open("TrainingDataPositive.txt", "r") as file:
    pos_reviews = file.readlines()

n = 30
neg_reviews = random.sample(neg_reviews, n)
pos_reviews = random.sample(pos_reviews, n)

# Write the reviews to the file
with open("data/reviews/small/reviews.txt", "w") as file:
    for review in neg_reviews:
        file.write(review)
    for review in pos_reviews:
        file.write(review)
