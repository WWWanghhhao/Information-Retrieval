import pandas as pd
import os
import json
import numpy as np
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


def build_invert_index(data, only_title=False, only_content=False, only_description=False):
    token_map = {}

    if only_title:
        for index, row in data.iterrows():
            token_map[index] = {}
            title = row['标题'] if pd.notnull(row['标题']) else ''
            for token in title.split(' '):
                if token == ' ':
                    continue
                if token not in token_map[index]:
                    token_map[index][token] = 1
                else:
                    token_map[index][token] += 1

    elif only_content:
        for index, row in data.iterrows():
            token_map[index] = {}
            content = row['文档内容'] if pd.notnull(row['文档内容']) else ''
            for token in content.split(' '):
                if token == ' ':
                    continue
                if token not in token_map[index]:
                    token_map[index][token] = 1
                else:
                    token_map[index][token] += 1

    elif only_description:
        for index, row in data.iterrows():
            token_map[index] = {}
            desc = row['摘要'] if pd.notnull(row['摘要']) else ''
            for token in desc.split(' '):
                if token == ' ':
                    continue
                if token not in token_map[index]:
                    token_map[index][token] = 1
                else:
                    token_map[index][token] += 1

    else:
        for index, row in data.iterrows():
            token_map[index] = {}
            # 确保每个部分都是字符串，避免 TypeError
            tokens = (
                    (row['摘要'] if pd.notnull(row['摘要']) else '') +
                    (row['标题'] if pd.notnull(row['标题']) else '') +
                    (row['文档内容'] if pd.notnull(row['文档内容']) else '')
            )

            for token in tokens.split(' '):
                if token == ' ':
                    continue
                if token not in token_map[index]:
                    token_map[index][token] = 1
                else:
                    token_map[index][token] += 1

    invert_map = {}
    for url, map in token_map.items():
        for token, f in map.items():
            if token not in invert_map:
                invert_map[token] = {}
            invert_map[token][url] = f

    return invert_map


x = 1


def calculate_tf_idf(data, only_title=False, only_content=False, only_description=False):
    # 收集文档
    documents = []

    if only_title:
        for index, row in data.iterrows():
            title = row['标题'] if pd.notnull(row['标题']) else ''
            documents.append(title)

    elif only_content:
        for index, row in data.iterrows():
            content = row['文档内容'] if pd.notnull(row['文档内容']) else ''
            documents.append(content)

    elif only_description:
        for index, row in data.iterrows():
            desc = row['摘要'] if pd.notnull(row['摘要']) else ''
            documents.append(desc)

    else:
        for index, row in data.iterrows():
            combined_text = (
                    (row['摘要'] if pd.notnull(row['摘要']) else '') +
                    (row['标题'] if pd.notnull(row['标题']) else '') +
                    (row['文档内容'] if pd.notnull(row['文档内容']) else '')
            )
            documents.append(combined_text)

    # 计算 TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    global x
    joblib.dump(vectorizer, f"tfidf_model{x}.pkl")
    return
    x = x + 1

    # 直接过滤稀疏矩阵中的 0 值，并转换为字典
    filtered_tfidf_dict = []

    for row_idx in range(tfidf_matrix.shape[0]):
        row = tfidf_matrix[row_idx]
        # 利用稀疏矩阵的非零元素访问方式
        nonzero_indices = row.nonzero()[1]  # 获取非零列索引

        # col 是词在特征词汇表中的位置
        row_dict = {int(col): row[0, col] for col in nonzero_indices}
        filtered_tfidf_dict.append(row_dict)

    return filtered_tfidf_dict


# df = pd.read_csv("./csv_data/new_cut_way.csv", encoding='utf-8')
# # 计算 TF-IDF
# tfidf_values = calculate_tf_idf(df, only_title=True)

# with open("./index_data/all_tfidf.json", 'w', encoding='utf-8') as json_file:
#     json.dump(tfidf_values, json_file, ensure_ascii=False, indent=4)
# print('1')
#
# tfidf_values = calculate_tf_idf(df, only_description=True)
# with open("./index_data/description_tfidf.json", 'w', encoding='utf-8') as json_file:
#     json.dump(tfidf_values, json_file, ensure_ascii=False, indent=4)
# print('2')
#
# tfidf_values = calculate_tf_idf(df, only_content=True)
# with open("./index_data/content_tfidf.json", 'w', encoding='utf-8') as json_file:
#     json.dump(tfidf_values, json_file, ensure_ascii=False, indent=4)
# print('3')
#
# tfidf_values = calculate_tf_idf(df, only_title=True)
# with open("./index_data/title_tfidf.json", 'w', encoding='utf-8') as json_file:
#     json.dump(tfidf_values, json_file, ensure_ascii=False, indent=4)
# print('4')

# path1 = "./index_data/all.json"
# r1 = build_invert_index(df)
# with open(path1, 'w', encoding='utf-8') as json_file:
#     json.dump(r1, json_file, ensure_ascii=False, indent=4)
#
# print('1')
#
# path2 = "./index_data/title.json"
# r2 = build_invert_index(df, only_title=True)
# with open(path2, 'w', encoding='utf-8') as json_file:
#     json.dump(r2, json_file, ensure_ascii=False, indent=4)
# print('2')
#
# path3 = "./index_data/description.json"
# r3 = build_invert_index(df, only_description=True)
# with open(path3, 'w', encoding='utf-8') as json_file:
#     json.dump(r3, json_file, ensure_ascii=False, indent=4)
# print('3')
#
# path4 = "./index_data/content.json"
# r4 = build_invert_index(df, only_content=True)
# with open(path4, 'w', encoding='utf-8') as json_file:
#     json.dump(r4, json_file, ensure_ascii=False, indent=4)
# print('4')

with open('./index_data/title_tfidf.json', 'r', encoding='utf-8') as file:
    dic = json.load(file)
model = joblib.load('./tfidf_model_title.pkl')
words = model.get_feature_names_out()
for k, v in dic[0].items():
    token = words[int(k)]
    print(token, v)
