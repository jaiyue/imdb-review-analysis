import pandas as pd
import nltk
from collections import Counter

# Tokenizer resource
nltk.download('punkt')

input_csv = "rq3_cleaned_reviews.csv"
output_unigram_csv = "rq3_unigram_results.csv"
output_bigram_csv = "rq3_bigram_results.csv"
output_trigram_csv = "rq3_trigram_results.csv"


# Custom n-gram generator
def generate_N_grams(tokens, ngram=1):
    temp = zip(*[tokens[i:] for i in range(ngram)])
    return list(temp)


# Load cleaned review text
df = pd.read_csv(input_csv)

all_unigrams = []
all_bigrams = []
all_trigrams = []

for text in df["clean_text"]:
    if pd.isna(text):
        continue
    text = str(text)

    # Tokenise text
    tokens = nltk.word_tokenize(text.lower())

    # Unigrams
    all_unigrams.extend(tokens)

    # Bigrams
    all_bigrams.extend(generate_N_grams(tokens, 2))

    # Trigrams
    all_trigrams.extend(generate_N_grams(tokens, 3))


# Count frequencies
unigram_freq = Counter(all_unigrams)
bigram_freq = Counter(all_bigrams)
trigram_freq = Counter(all_trigrams)

# Convert to DataFrame
unigram_df = pd.DataFrame(
    unigram_freq.most_common(100),
    columns=["Unigram", "Frequency"]
)

bigram_df = pd.DataFrame(
    [(" ".join(bi), freq) for bi, freq in bigram_freq.most_common(100)],
    columns=["Bigram", "Frequency"]
)

trigram_df = pd.DataFrame(
    [(" ".join(tri), freq) for tri, freq in trigram_freq.most_common(100)],
    columns=["Trigram", "Frequency"]
)

# Save results
unigram_df.to_csv(output_unigram_csv, index=False, encoding="utf-8")
bigram_df.to_csv(output_bigram_csv, index=False, encoding="utf-8")
trigram_df.to_csv(output_trigram_csv, index=False, encoding="utf-8")
