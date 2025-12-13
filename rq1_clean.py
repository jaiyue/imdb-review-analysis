import pandas as pd
import string
import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# 读取 CSV
df = pd.read_csv("zootopia_reviews.csv")

# 合并标题和正文
df["text"] = df["Review_Title"].fillna("") + " " + df["Review_Content"].fillna("")

# 文本清洗函数
stop_words = set(stopwords.words("english"))
punctuation = set(string.punctuation)
lemmatizer = WordNetLemmatizer()

def clean_text(doc):
    # 小写
    doc = doc.lower()
    
    # 去停用词
    words = [w for w in doc.split() if w not in stop_words]
    
    # 去标点
    words = [w for w in words if w not in punctuation]
    
    # 词形还原
    words = [lemmatizer.lemmatize(w) for w in words]
    
    return words

# 构建清洗后的语料
clean_corpus = df["text"].dropna().apply(clean_text).tolist()
