import time

import requests
from bs4 import BeautifulSoup
import csv
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

# 定义重试策略
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)

# 创建一个新的 Session 对象并应用重试策略
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

t = 0
# 创建 CSV 文件并写入表头
with open('index_html.csv', 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['标题', '日期', '链接']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if csvfile.tell() == 0:  # 检查文件是否为空
        writer.writeheader()

    for page_num in range(861, 1000):
        print(page_num)
        # if 968 - page_num < 100:
        #     url = f"https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_00000000{968 - page_num}.shtml"
        # else:
        url = f"https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_000000{page_num}.shtml"
        # url = f"https://news.nankai.edu.cn/dcxy/system/count//0005000/000000000000/000/000/c0005000000000000000_0000000{page_num}.shtml"
        # url = f"http://urp.nku.cn/tzgg/list.htm"
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取新闻列表
        news_list = soup.find_all('table', width='98%')
        for news in news_list:
            title = news.find('a').text.strip()
            date = news.find('div', align='right').text.strip()
            link = news.find('a')['href']

            # 保存 CSV 文件
            writer.writerow({'标题': title, '日期': date, '链接': link})

            # 获取并保存 HTML 文件
            html_response = session.get(link)
            safe_title = ''.join(c for c in title if c.isalnum() or c in [' ', '_'])
            html_filename = f"html_files/{safe_title}.html"
            with open(html_filename, 'w', encoding='utf-8') as html_file:
                html_file.write(html_response.text)
            print(t)
            time.sleep(random.uniform(0.1, 0.4))
            t = t + 1

print('数据已保存到 media_nankai_news.csv 文件中,HTML 文件已保存到 html_files 目录。')
