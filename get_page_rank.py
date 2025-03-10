import pandas as pd
import networkx as nx
import ast
import random

# 读取数据
df = pd.read_csv("./csv_data/url2links.csv", encoding='utf-8')

# 确保 links 是列表格式
df['links'] = df['links'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# 构建有向图
G = nx.DiGraph()
for i, row in df.iterrows():
    print(i)
    url = row['url']
    links = row['links']
    if url not in G:
        G.add_node(url)  # 确保每个 URL 都在图中
    for link in links:
        G.add_edge(url, link)


# 检查孤立节点并添加随机链接
isolated_nodes = list(nx.isolates(G))
for node in isolated_nodes:
    random_target = random.choice(list(G.nodes()))
    G.add_edge(node, random_target)

# 计算 PageRank
pr = nx.pagerank(G, alpha=0.85)

# 创建新的数据框并保存到 CSV 文件
pagerank_df = pd.DataFrame({'url': list(pr.keys()), 'pagerank': list(pr.values())})
pagerank_df.to_csv('./csv_data/pagerank.csv', index=True, index_label='index')
