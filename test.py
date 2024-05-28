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
