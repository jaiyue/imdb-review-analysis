# Reference: https://www.datacamp.com/tutorial/what-is-topic-modeling

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pandas as pd
import nltk
import re

# NLTK resources
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

# Load raw reviews
df = pd.read_csv("reviews/reviews.csv")

# Merge title and content
df["text"] = df["Review_Title"].fillna("") + " " + df["Review_Content"].fillna("")

# Stopwords for RQ1 & RQ2
stop_words = set(stopwords.words("english"))
stop_words.update([
    "like", "one", "really", "even", "good", "great", "best", "feel",
    "movie", "film", "zootopia", "disney",
    "also", "would", "make", "u", "it", "well", "get", "think", "say",
    "character", "story", "animation", "animal", "time", "world", "see", "love"
])

lemmatizer = WordNetLemmatizer()


# Clean text for topic modelling
def clean_text(doc):
    doc = re.sub(r"[^a-zA-Z0-9\s]", "", doc)
    doc = doc.lower()
    words = doc.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)


# Build cleaned corpus
df["clean_text"] = df["text"].dropna().apply(clean_text)

# Save cleaned text
df_clean = pd.DataFrame({"clean_text": df["clean_text"]})
df_clean.to_csv("rq1_2_cleaned_reviews.csv", index=False)

print(f"Cleaned {len(df)} reviews and saved to rq1_2_cleaned_reviews.csv")
