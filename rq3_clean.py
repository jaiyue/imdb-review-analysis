# Reference: https://www.analyticsvidhya.com/blog/2018/02/the-different-methods-deal-text-data-predictive-python/
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

# Tokenizer and stopwords
nltk.download("punkt")
nltk.download("stopwords")

input_csv = "reviews.csv"
output_csv = "rq3_cleaned_reviews.csv"


# Clean text for RQ3 (retain negation and evaluative words)
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = nltk.word_tokenize(text)

    stop_words = set(stopwords.words("english"))
    negations = {"not", "no", "nor"}
    stop_words = stop_words - negations

    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    return " ".join(tokens)


# Load raw review data
df = pd.read_csv(input_csv)

# Remove rows without rating
df = df.dropna(subset=["Rating"])

# Merge title and content
df["merged_text"] = (
    df["Review_Title"].fillna("") + " " + df["Review_Content"].fillna("")
)

# Apply RQ3-specific cleaning
df["clean_text"] = df["merged_text"].apply(clean_text)

# Keep required fields only
output_df = df[["clean_text"]]

# Save cleaned data
output_df.to_csv(output_csv, index=False, encoding="utf-8")
