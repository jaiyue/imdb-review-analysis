# https://www.datacamp.com/tutorial/what-is-topic-modeling
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pandas as pd
import string
import nltk
import re

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# 读取 CSV
df = pd.read_csv(
    "IMDB_Scraper/reviews/1_Zootropolis_2016_reviews_20251212_143302.csv")

# 合并标题和正文
df["text"] = df["Review_Title"].fillna(
    "") + " " + df["Review_Content"].fillna("")

# 文本清洗函数
stop_words = set(stopwords.words("english"))
# 只保留真正通用的停用词，移除具体的电影相关词汇
stop_words.update([
    "like", "one", "really", "even", "good", "great", "best", "feel",
    "movie", "film", "zootopia", "disney",
    "also", "would", "make", "u", "it", "well", "get", "think", "say",
    "character", "story", "animation", "animal", "time", "world", "see", "love"
])

punctuation = set(string.punctuation)
lemmatizer = WordNetLemmatizer()

def clean_text(doc):
    # 只保留字母和数字（包括空格），删除所有其他字符
    # 使用正则表达式：只保留字母a-z、数字0-9和空格
    doc = re.sub(r'[^a-zA-Z0-9\s]', '', doc)
    
    # 小写
    doc = doc.lower()

    # 分词
    words = doc.split()

    # 去停用词和词形还原
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]

    return ' '.join(words)


# 构建清洗后的语料
df["clean_text"] = df["text"].dropna().apply(clean_text)
df_clean = pd.DataFrame({'clean_text': df["clean_text"]})
df_clean.to_csv("rq1_2_cleaned_reviews.csv", index=False)