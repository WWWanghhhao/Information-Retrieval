"""
从 html 文件中获取摘要和文档内容信息
"""

from lxml import html
import csv
from bs4 import BeautifulSoup
import os
import re

csv_path = "E:/2024Fall-IR/project/media_nankai_news8.csv"
html_path = "E:/2024Fall-IR/project/html_files8"
new_path = "E:/2024Fall-IR/project/csv_data/test.csv"
# 读取CSV文件并添加新列
with open(csv_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    # 创建一个新的CSV文件，用于写入带有摘要和文档内容的新数据
    with open(new_path, 'a', newline='', encoding='utf-8') as new_csvfile:
        writer = csv.writer(new_csvfile)
        # 写入表头，添加新列"摘要"和"文档内容"
        # headers = next(reader)  # 获取原始CSV文件的表头
        # writer.writerow(headers + ['摘要', '文档内容'])

        for row in reader:
            safe_title = ''.join(c for c in row[0] if c.isalnum() or c in [' ', '_'])
            html_file = os.path.join(html_path, safe_title + '.htm')

            if os.path.exists(html_file):
                with open(html_file, 'r', encoding='utf-8') as hf:
                    html_content = hf.read()  # 读取HTML内容

                    # 使用BeautifulSoup提取<p>标签内容
                    soup = BeautifulSoup(html_content, 'html.parser')
                    para = soup.find_all('p')
                    article_content = ' '.join(p.get_text(strip=True) for p in para)

                    # 提取<meta>标签的description内容
                    tree = html.fromstring(html_content)
                    description = tree.xpath("//meta[@name='description']/@content")
                    if not description:
                        description = tree.xpath("//meta[contains(@name, 'description')]/@content")
                    if not description:
                        description = ''
                        for meta in tree.xpath("//meta"):
                            name = meta.xpath("./@name")
                            if name and 'description' in name[0].lower():
                                description = meta.xpath("./@content")[0]
                                break
                    des = ' '.join(description)
                    article_content = ' '.join(re.split(r'\s+', article_content))
                    des = re.sub(r'\n', ' ', des)
                    article_content = re.sub(r'\n', ' ', article_content)
                    row += [des, article_content]
                    writer.writerow(row)
