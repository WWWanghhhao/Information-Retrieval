# Information-Retrieval

src/                  # 源代码目录
├── get_data.py       # 爬取网页
├── get_data2.py      # 爬取网页
├── add_content.py    # 提取网页内容
├── extract_links.py  # 提取网页超链接
├── get_token.py      # 分词处理
├── get_tfidf.py      # 计算 TF-IDF
├── get_page_rank.py  # 计算 PageRank
├── search.py         # 搜索功能实现
├── app.py            # Web 后端主程序
└── templates/        # 前端模板目录
    ├── history.html      # 搜索历史页面
    ├── index.html        # 主页
    └── search_result.html # 搜索结果页面
