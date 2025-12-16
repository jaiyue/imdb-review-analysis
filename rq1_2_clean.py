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

# 读取 CSV - 使用新的文件名
df = pd.read_csv("reviews/reviews.csv")

# 合并标题和正文 - 保持原逻辑不变
df["text"] = df["Review_Title"].fillna("") + " " + df["Review_Content"].fillna("")

# 文本清洗函数
stop_words = set(stopwords.words("english"))
# 只保留真正通用的停用词，移除具体的电影相关词汇
stop_words.update([
    "like", "one", "really", "even", "good", "great", "best", "feel",
    "movie", "film", "zootopia", "disney",
    "also", "would", "make", "u", "it", "well", "get", "think", "say",
    "character", "story", "animation", "animal", "time", "world", "see", "love"
])

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

# 保持原输出格式不变，保存清洗后的文本
df_clean = pd.DataFrame({'clean_text': df["clean_text"]})
df_clean.to_csv("rq1_2_cleaned_reviews.csv", index=False)

print(f"Cleaned {len(df)} reviews and saved to rq1_2_cleaned_reviews.csv")