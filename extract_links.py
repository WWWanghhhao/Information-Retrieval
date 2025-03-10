import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_links(url):
    """从给定的 URL 中提取链接"""
    try:
        parts = url.split('/')
        base_url = '/'.join(parts[:3])

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if href.startswith('/'):
                    absolute_url = base_url + href
                    links.append(absolute_url)
                else:
                    links.append(href)
        return links
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return []


# 读取 CSV 文件
df = pd.read_csv("E:/2024Fall-IR/project/csv_data/cutted_data.csv", encoding='utf-8')

# 创建一个列表用来保存结果
results = []

for index, row in df.iterrows():
    url = row['链接']
    links = extract_links(url)
    results.append({
        'index': index,
        'url': url,
        'links': links
    })
    print(f"index-size: {index}-{len(links)}")
    # time.sleep(0.8)

# 将结果转换为 DataFrame
results_df = pd.DataFrame(results)

# 保存到本地 CSV 文件
results_df.to_csv("E:/2024Fall-IR/project/csv_data/url2links.csv", index=False, encoding='utf-8')
