import time
from datetime import datetime, timedelta
import jieba
from jieba import cut_for_search
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import joblib
import numpy as np
from concurrent.futures import ProcessPoolExecutor

data_filename = './csv_data/data_with_pagerank.csv'

all_ri_filename = './index_data/all.json'
content_ri_filename = './index_data/content.json'
description_ri_filename = './index_data/description.json'
title_ri_filename = './index_data/title.json'

all_tfidf_filename = './index_data/all_tfidf.json'
content_tfidf_filename = './index_data/content_tfidf.json'
description_tfidf_filename = './index_data/description_tfidf.json'
title_tfidf_filename = './index_data/title_tfidf.json'

all_tfidf_model = './tfidf_model_all.pkl'
content_tfidf_model = './tfidf_model_content.pkl'
description_tfidf_model = './tfidf_model_description.pkl'
title_tfidf_model = './tfidf_model_title.pkl'

all_model = joblib.load(all_tfidf_model)
content_model = joblib.load(content_tfidf_model)
description_model = joblib.load(description_tfidf_model)
title_model = joblib.load(title_tfidf_model)

pagerank_path = './index_data/pagerank.json'
date_path = "./index_data/date.json"
url_path = "./index_data/url.json"
name_path = "./index_data/name.json"


def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        file = json.load(f)
        return file


date = load_json(date_path)
pagerank = load_json(pagerank_path)
name = load_json(name_path)
urls = load_json(url_path)


def input_query(query, only_title=False, only_description=False, only_content=False):
    query = query.strip()

    wildcard = re.search(r'[\*\?]', query)

    if wildcard:
        # 表示需要进行通配查询
        if only_title:
            words = title_model.get_feature_names_out()
        elif only_content:
            words = content_model.get_feature_names_out()
        elif only_description:
            words = description_model.get_feature_names_out()
        else:
            words = all_model.get_feature_names_out()

        # 将 query 转换为正则表达式，替换通配符并添加开头匹配
        # '^' 表示以 query 开头
        pattern = '^' + query.replace('*', '.*').replace('?', '.')

        # 查找匹配的词
        tokens = [word for word in words if re.match(pattern + '$', word)]
    else:
        query = re.sub(r'[\.\^\$\*\+\?\{\}\[\]\|\(\)]', '', query)
        tokens = [token for token in jieba.lcut(query) if token.strip()]

    return ' '.join(tokens)


def compute_cosine(query_vector, doc_vector):
    """
    :param query_vector: 查询语句构成的字典 key: token在特征词汇表的下标 value: token的tf-idf值
    :param doc_vector: 单个文档构成的字典
    :return: 对位tf-idf相乘结果，且不除以向量的长度
    """
    # 找到查询向量和文档向量中都有的 tokens, 累加二者 tf-idf 相乘的结果
    common_tokens = query_vector.keys() & doc_vector.keys()
    if len(common_tokens) == 0:
        return 0.0
    result = sum(query_vector.get(token, 0) * doc_vector.get(token, 0) for token in common_tokens)
    return result


def basic_search(input_tokens, history=None, only_title=False, only_description=False, only_content=False,
                 result_size=20, date_limit=0):
    """
    :param input_tokens: 已经分词的输入内容
    :param history: 当前会话的历史查询记录
    :param only_title: 只查询标题
    :param only_description: 只查询摘要
    :param only_content: 只查询文档内容
    :param result_size: 返回的结果大小
    :param date_limit: 日期限制，0表示不限制
    :return: 文档四元组（索引，标题，链接，日期）
    """

    history = re.sub(r'[\.\^\$\*\+\?\{\}\[\]\|\(\)]', '', history.strip())
    history_tokens = [token for token in jieba.lcut(history) if token.strip()]
    history_tokens = ' '.join(history_tokens)

    # 加载 TF-IDF 模型
    if only_title:
        tfidf = load_json(title_tfidf_filename)
        sparse_query_tfidf = title_model.transform([input_tokens])
        sparse_history_tfidf = title_model.transform([history_tokens])
    elif only_content:
        tfidf = load_json(content_tfidf_filename)
        sparse_query_tfidf = content_model.transform([input_tokens])
        sparse_history_tfidf = content_model.transform([history_tokens])
    elif only_description:
        tfidf = load_json(description_tfidf_filename)
        sparse_query_tfidf = description_model.transform([input_tokens])
        sparse_history_tfidf = description_model.transform([history_tokens])
    else:
        tfidf = load_json(description_tfidf_filename)
        sparse_query_tfidf = description_model.transform([input_tokens])
        sparse_history_tfidf = description_model.transform([history_tokens])

    # 将稀疏矩阵转为 index-tfidf 的字典结构
    rows, cols = sparse_query_tfidf.nonzero()
    values = sparse_query_tfidf.data
    query_tfidf = {str(col): val for col, val in zip(cols, values)}

    rows, cols = sparse_history_tfidf.nonzero()
    values = sparse_history_tfidf.data
    history_tfidf = {str(col): val for col, val in zip(cols, values)}

    # 计算余弦相似度
    similarities = []
    for i in range(len(tfidf)):
        cos = compute_cosine(query_tfidf, tfidf[i])  # 计算余弦相似度
        his_cos = compute_cosine(history_tfidf, tfidf[i])

        score = cos * 0.85 + pagerank[str(i)] * 0.1 + his_cos * 0.05
        similarities.append((i, score))

    # 按照相似度从大到小排序，并返回前 result_size 个结果
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    # 满足日期限制
    basic_indexes = [index for index, cosine in similarities if cosine > 1e-05]
    results = []
    limit = datetime.now() - timedelta(days=date_limit)
    for index in basic_indexes:
        if date_limit != 0 and str(date[str(index)]) == "nan":
            continue
        if date_limit == 0 and str(date[str(index)]) == 'nan':
            results.append((index, name[str(index)], urls[str(index)], 'NaN'))
            continue

        # 解析日期
        doc_date = datetime.strptime(date[str(index)], '%Y-%m-%d')
        if date_limit == 0 or limit <= doc_date:
            results.append((index, name[str(index)], urls[str(index)], date[str(index)]))
            if len(results) >= result_size:
                break

    # 返回文档的四元组（索引，标题，链接，日期）
    return results


def snapshot(indexes):
    """
    :param indexes: 需要进行网页快照的文档索引
    :return: 在本地的位置（相对路径）
    """
    pdf = ["2024年暑假值班表", "关于2021年同等学力人员申请硕士学位课程水平考试题库考试报名的通知",
           "关于2021年同等学力人员申请硕士学位课程水平考试题库考试报名的通知天津考点", '关于端午节放假的通知',
           '关于放暑假的通知', '关于劳动节放假的通知', '关于清明节放假的通知',
           '南开大学经济学院本科生转专业转入实施细则 ', '我院在学校实验室安全工作会议上的经验交流汇报']
    results = []
    for index in indexes:
        doc_name = name[str(index)]

        file_name = ''.join(c for c in doc_name if c.isalnum() or c in [' ', '_'])
        if file_name in pdf:
            file_name = file_name + ".pdf"
        else:
            file_name = file_name + ".html"
        results.append(file_name)
    return results


if __name__ == '__main__':
    q = str(input())
    x = basic_search(input_query(q), history="", only_title=True, result_size=10, date_limit=0)
    for i in x:
        print(i)


    q = str(input())
    x = basic_search(input_query(q), history="", only_title=True, result_size=10, date_limit=0)
    for i in x:
        print(i)