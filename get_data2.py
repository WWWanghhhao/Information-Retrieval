import requests
from bs4 import BeautifulSoup
import os
import csv
import random
import time

t = 1
with open('综合信息门户media_nankai_news11.csv', 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['标题', '日期', '链接']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if csvfile.tell() == 0:  # 检查文件是否为空
        writer.writeheader()

    # 循环爬取
    for page in range(57+5+28+92+320+20, 1408):
        url = f"http://urp.nku.cn/tzgg/list{page}.htm"
        response = requests.get(url)

        # 假设 response 是您从某个 URL 获取的响应
        if response.status_code == 200:
            response.encoding = response.apparent_encoding  # 自动检测编码
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取新闻列表
            news_items = soup.find('ul', class_='news_list list2').find_all('li')
            # print(news_items[0])
            for item in news_items:
                title_tag = item.find('a')  # 找到每个条目的链接
                if title_tag:
                    title = title_tag['title']
                    link = title_tag['href']
                    if link[0] == '/':
                        link = 'http://urp.nku.cn' + title_tag['href']  # 获取链接
                    date = item.find('span', class_='news_meta').get_text()
                    # print(date,link,title)
                    # 保存 CSV 文件
                    if '</' in title:
                        continue


                    # 下载对应的网页
                    try:
                        download_response = requests.get(link)
                        if 'Content-Type' in download_response.headers and download_response.headers['Content-Type'].startswith('text/html'):
                            sp = BeautifulSoup(download_response.text, 'html.parser')
                            writer.writerow({'标题': title, '日期': date, '链接': link})
                        else:
                            print(f'下载的内容不是 HTML')
                            continue
                        if download_response.status_code == 200:
                            download_response.encoding = download_response.apparent_encoding
                            # 创建文件名，替换非法字符

                            file_name = ''.join(c for c in title if c.isalnum() or c in [' ', '_'])
                            file_name = 'html_files11/'+file_name + ".htm"

                            # 解析下载的网页
                            sp = BeautifulSoup(download_response.text, 'html.parser')

                            # 修改 img 标签的 src 属性
                            for img in sp.find_all('img'):
                                src = img.get('src')
                                if src and src.startswith('/'):
                                    img['src'] = "http://urp.nku.cn" + src


                            # 写入修改后的 HTML 内容
                            with open(file_name, 'w', encoding='utf-8') as file:
                                file.write(str(sp))  # 确保写入修改后的 soup 对象

                            print(t)
                            t += 1
                            time.sleep(random.uniform(0.2, 0.4))
                    except requests.exceptions.RequestException as e:
                        print(f'下载失败，状态码：{download_response.status_code}, 错误: {e}')
        else:
            print(f'请求失败，状态码：{response.status_code}')
