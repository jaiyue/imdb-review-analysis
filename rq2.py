import pandas as pd

# 读取数据（这里假设数据已经作为字符串提供）
input_csv = "rq2_doc_topic_distribution.csv"

# 因为数据量很大，这里假设数据已经以字符串形式传入
# 实际使用时可以直接读取CSV文件
df = pd.read_csv(input_csv)

# 设定阈值，比如80%
threshold = 80.0

# 统计单一主题和多主题的数量
single_topic_count = 0
multi_topic_count = 0

for idx, row in df.iterrows():
    # 获取所有主题的百分比
    topic_cols = [col for col in df.columns if col.startswith('Topic_')]
    percentages = row[topic_cols].values
    
    # 检查是否有主题超过阈值
    if any(p >= threshold for p in percentages):
        single_topic_count += 1
    else:
        multi_topic_count += 1

total_reviews = len(df)
single_topic_ratio = single_topic_count / total_reviews * 100
multi_topic_ratio = multi_topic_count / total_reviews * 100

print(f"总评论数: {total_reviews}")
print(f"聚焦单一主题的评论数: {single_topic_count} ({single_topic_ratio:.2f}%)")
print(f"多主题分布的评论数: {multi_topic_count} ({multi_topic_ratio:.2f}%)")

if single_topic_count > multi_topic_count:
    print("\n结论: 观众在写评论时更多聚焦于单一主题")
else:
    print("\n结论: 观众在写评论时更多涉及多个主题")