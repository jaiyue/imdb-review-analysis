import pandas as pd

# Input file
input_csv = "rq2_doc_topic_distribution.csv"

# Load topic distribution data
df = pd.read_csv(input_csv)

# Threshold for dominant topic
threshold = 80.0

# Counters
single_topic_count = 0
multi_topic_count = 0

for idx, row in df.iterrows():
    # Topic percentage columns
    topic_cols = [col for col in df.columns if col.startswith("Topic_")]
    percentages = row[topic_cols].values

    # Check dominant topic
    if any(p >= threshold for p in percentages):
        single_topic_count += 1
    else:
        multi_topic_count += 1

total_reviews = len(df)
single_topic_ratio = single_topic_count / total_reviews * 100
multi_topic_ratio = multi_topic_count / total_reviews * 100

print(f"Total reviews: {total_reviews}")
print(f"Single-topic reviews: {single_topic_count} ({single_topic_ratio:.2f}%)")
print(f"Multi-topic reviews: {multi_topic_count} ({multi_topic_ratio:.2f}%)")

if single_topic_count > multi_topic_count:
    print("\nConclusion: Reviews mainly focus on a single topic")
else:
    print("\nConclusion: Reviews mainly cover multiple topics")
