import jieba
import pandas as pd
import re
import os
from jieba import cut_for_search

# 设置文件路径
new_path = "E:/2024Fall-IR/project/csv_data/data.csv"
temp_path = "E:/2024Fall-IR/project/csv_data/new_cut_way.csv"

path = "E:/2024Fall-IR/project/csv_data/baidu_stopwords.txt"

with open(path, 'r', encoding='utf-8') as file:
    stop_words = file.readlines()
stop_words = [stop.strip() for stop in stop_words]


def segment_text(text):
    # 处理空值
    if pd.isnull(text):
        return ''

    text = text.lower()

    text = re.sub(r'[^\w\s]', '', text)

    words = jieba.lcut_for_search(text.strip())

    filter_words = [word for word in words if word not in stop_words]

    return ' '.join(filter_words)


# 检查新 CSV 文件是否存在
if os.path.exists(new_path):
    # 读取 CSV 文件
    df = pd.read_csv(new_path, encoding='utf-8')
    # 对 ’标题‘ ’摘要‘ ’文档内容‘ 使用 cut_for_search 进行分词处理

    df['标题'] = df['标题'].apply(segment_text)
    df['摘要'] = df['摘要'].apply(segment_text)
    df['文档内容'] = df['文档内容'].apply(segment_text)

    # 将修改后的数据写入新的 CSV 文件
    df.to_csv(temp_path, index=False, encoding='utf-8')
