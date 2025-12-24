import pandas as pd
import nltk
from collections import Counter

# 分词资源
nltk.download('punkt')

input_csv = "rq3_cleaned_reviews.csv"
output_unigram_csv = "rq3_unigram_results.csv"
output_bigram_csv = "rq3_bigram_results.csv"
output_trigram_csv = "rq3_trigram_results.csv"


# ===== 自定义 N-gram 函数（替换 nltk.util.ngrams）=====
def generate_N_grams(tokens, ngram=1):
    temp = zip(*[tokens[i:] for i in range(ngram)])
    return list(temp)


# 读取数据
df = pd.read_csv(input_csv)

all_unigrams = []
all_bigrams = []
all_trigrams = []

for text in df["clean_text"]:
    if pd.isna(text):
        continue
    text = str(text)

    # 分词
    tokens = nltk.word_tokenize(text.lower())

    # unigram
    all_unigrams.extend(tokens)

    # bigram（使用自定义函数）
    all_bigrams.extend(generate_N_grams(tokens, 2))

    # trigram（使用自定义函数）
    all_trigrams.extend(generate_N_grams(tokens, 3))


# 统计频率
unigram_freq = Counter(all_unigrams)
bigram_freq = Counter(all_bigrams)
trigram_freq = Counter(all_trigrams)

# 转成 DataFrame（输出格式不变）
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

# 输出结果
unigram_df.to_csv(output_unigram_csv, index=False, encoding="utf-8")
bigram_df.to_csv(output_bigram_csv, index=False, encoding="utf-8")
trigram_df.to_csv(output_trigram_csv, index=False, encoding="utf-8")
