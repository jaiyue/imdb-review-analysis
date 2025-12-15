import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob

# 下载所需资源
nltk.download("stopwords")
nltk.download("punkt")

input_csv = "IMDB_Scraper/reviews/1_Zootropolis_2016_reviews_20251212_143302.csv"
output_csv = "rq3_cleaned_reviews.csv"

# 读取数据
df = pd.read_csv(input_csv)

# 删除没有评分的评论
df = df.dropna(subset=["Rating"])
df = df[~df["Rating"].astype(str).str.lower().isin(["no rating", "norating"])]

# 合并标题和正文
df["full_text"] = df["Review_Title"].fillna("") + " " + df["Review_Content"].fillna("")

# 1. 小写化
df["clean_text"] = df["full_text"].str.lower()

# 2. 去除标点
df["clean_text"] = df["clean_text"].str.replace(r"[^\w\s]", "", regex=True)

# 3. 去除停用词，但保留否定词
negation_words = {"not", "no", "nor"}
stop_words = set(stopwords.words("english")) - negation_words
df["clean_text"] = df["clean_text"].apply(
    lambda x: " ".join(w for w in x.split() if w not in stop_words)
)

# 4. 去除最常见的10个词，但保留评价性词
freq = pd.Series(" ".join(df["clean_text"]).split()).value_counts()
common_words = set(freq.head(10).index)
key_eval_words = {"good", "bad", "love", "hate", "boring", "fun", "amazing", "worst", "best", "great"}
common_words_to_remove = common_words - key_eval_words
df["clean_text"] = df["clean_text"].apply(
    lambda x: " ".join(w for w in x.split() if w not in common_words_to_remove)
)

# 5. 去除罕见词（出现1次）但保留评价性词
rare_words = set(freq[freq == 1].index) - key_eval_words
df["clean_text"] = df["clean_text"].apply(
    lambda x: " ".join(w for w in x.split() if w not in rare_words)
)

# 保留最终列
df_clean = df[["Review_Index", "Rating", "clean_text"]]

# 输出清理后的文件
df_clean.to_csv(output_csv, index=False, encoding="utf-8")
