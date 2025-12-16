import pandas as pd
import nltk
from nltk.util import ngrams
from collections import Counter

# 分词资源
nltk.download('punkt')

input_csv = "rq3_cleaned_reviews.csv"
output_unigram_csv = "rq3_unigram_results.csv"
output_bigram_csv = "rq3_bigram_results.csv"
output_trigram_csv = "rq3_trigram_results.csv"

# 读取数据
df = pd.read_csv(input_csv)

all_unigrams = []
all_bigrams = []  # 添加 bigram 列表
all_trigrams = []

for text in df["clean_text"]:
    if pd.isna(text):
        continue
    text = str(text)
    # 分词
    tokens = nltk.word_tokenize(text.lower())
    
    # 提取 unigram
    all_unigrams.extend(tokens)
    
    # 提取 bigram
    all_bigrams.extend(list(ngrams(tokens, 2)))

    # 提取 trigram
    all_trigrams.extend(list(ngrams(tokens, 3)))

# 统计频率
unigram_freq = Counter(all_unigrams)
bigram_freq = Counter(all_bigrams)
trigram_freq = Counter(all_trigrams)

# 转成 DataFrame
unigram_df = pd.DataFrame(unigram_freq.most_common(100), columns=["Unigram", "Frequency"])
bigram_df = pd.DataFrame([(" ".join(bi), freq) for bi, freq in bigram_freq.most_common(100)], columns=["Bigram", "Frequency"])
trigram_df = pd.DataFrame([(" ".join(tri), freq) for tri, freq in trigram_freq.most_common(100)], columns=["Trigram", "Frequency"])

# 输出结果
unigram_df.to_csv(output_unigram_csv, index=False, encoding="utf-8")
bigram_df.to_csv(output_bigram_csv, index=False, encoding="utf-8")
trigram_df.to_csv(output_trigram_csv, index=False, encoding="utf-8")