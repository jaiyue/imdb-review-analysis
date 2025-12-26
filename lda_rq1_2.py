from gensim import corpora
from gensim.models import LdaModel
from gensim.models.phrases import Phrases, Phraser
import pandas as pd
import numpy as np

num_topics = 20
cleaned_csv = "rq1_2_cleaned_reviews.csv"
output_doc_topics = "rq2_doc_topic_distribution.csv"
output_combined = "rq1_2_summary_concentration.csv"

# Load cleaned text
df_clean = pd.read_csv(cleaned_csv)

# Tokenise text
tokenized_corpus = [
    text.split() for text in df_clean["clean_text"].fillna("").tolist()
]

# Train bigram model
bigram = Phrases(tokenized_corpus, min_count=3, threshold=5)
bigram_mod = Phraser(bigram)

# Apply bigrams
corpus_with_bigrams = [bigram_mod[doc] for doc in tokenized_corpus]


# Build dictionary and document-term matrix
dictionary = corpora.Dictionary(corpus_with_bigrams)

# Remove extreme terms
dictionary.filter_extremes(no_below=5, no_above=0.5)

doc_term_matrix = [
    dictionary.doc2bow(doc) for doc in corpus_with_bigrams
]

# Train LDA model
lda = LdaModel(
    doc_term_matrix,
    num_topics=num_topics,
    id2word=dictionary,
    random_state=42,
    passes=10,
    alpha="auto",
    eta="auto"
)

# Per-document topic distribution
all_doc_topics = []
dominant_topics = []

for idx, doc_bow in enumerate(doc_term_matrix):
    topic_dist = sorted(
        lda.get_document_topics(doc_bow, minimum_probability=0),
        key=lambda x: x[0]
    )
    topic_percent = [prob * 100 for _, prob in topic_dist]
    all_doc_topics.append([idx] + topic_percent)
    dominant_topics.append(
        np.argmax([prob for _, prob in topic_dist])
    )

columns = ["Review_Index"] + [
    f"Topic_{i}_%" for i in range(num_topics)
]

df_doc_topics = pd.DataFrame(all_doc_topics, columns=columns)
df_doc_topics.to_csv(output_doc_topics, index=False)


# Concentration metrics
def gini(probs):
    probs = np.sort(probs)
    cum = np.cumsum(probs)
    return (
        (len(probs) + 1 - 2 * np.sum(cum) / cum[-1]) / len(probs)
        if cum[-1] > 0 else 0
    )


def entropy(probs):
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


topic_matrix = df_doc_topics.iloc[:, 1:].values / 100
topic_counts = np.bincount(dominant_topics, minlength=num_topics)
total_reviews = len(dominant_topics)

# Combine topic summary and concentration
combined_data = []

for topic_id in range(num_topics):
    probs = topic_matrix[:, topic_id]
    keywords = ", ".join(
        [w for w, _ in lda.show_topic(topic_id, topn=6)]
    )
    count = topic_counts[topic_id]
    percent = round(count / total_reviews * 100, 2)
    g = round(gini(probs), 3)
    e = round(entropy(probs), 3)

    if g > 0.8:
        level = "Very High"
    elif g > 0.6:
        level = "High"
    elif g > 0.4:
        level = "Medium"
    else:
        level = "Low"

    combined_data.append({
        "Topic_ID": topic_id,
        "Keywords": keywords,
        "Num_of_Reviews": count,
        "Percentage": percent,
        "Avg_Probability": round(np.mean(probs) * 100, 2),
        "Gini": g,
        "Entropy": e,
        "Concentration_Level": level
    })

df_combined = (
    pd.DataFrame(combined_data)
    .sort_values("Num_of_Reviews", ascending=False)
)

df_combined.to_csv(output_combined, index=False)
