import pickle

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from search import input_query, basic_search, snapshot
import joblib
import re

app = Flask(__name__)
app.secret_key = '123456789'

history_map = dict()
current = 0

# 文件根目录
BASE_DIRECTORY = 'E:/2024Fall-IR/project/all_html'
with open('better_words.pkl', 'rb') as f:
    better_words = pickle.load(f)


# 路由转发来访问网页快照的本地文件
@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory(BASE_DIRECTORY, filename)


@app.route('/suggest')
def suggest_queries():
    query = request.args.get('query')
    suggestions = []
    pattern = '^' + query.lower() + ".*"
    count = 0
    for word in better_words:
        if re.match(pattern, word):
            suggestions.append(word)
            count += 1
            if count >= 10:
                break
    return jsonify(suggestions)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    if query == '自杀':
        return redirect("https://www.baidu.com/baidu?ie=utf-8&wd=" + query)
    global history_map, current
    if current not in history_map.keys():
        history_map[current] = ''

    query_history = history_map[current]
    history_map[current] += query
    history_map[current] += ' '
    ot = request.form['from'] == "other"
    if ot:
        return redirect("https://www.baidu.com/baidu?ie=utf-8&wd=" + query)
    only_title = request.form.get('target') == "only_title"
    only_content = request.form.get('target') == 'only_content'
    only_description = request.form.get('target') == 'only_description'
    date = request.form.get('limit')
    limit = 0
    if date == 'month':
        limit = 31
    elif date == 'year':
        limit = 365
    else:
        limit = 0
    search_result = basic_search(
        input_query(query, only_title=only_title, only_content=only_content, only_description=only_description),
        history=query_history, only_title=only_title,
        only_content=only_content, only_description=only_description
        , result_size=100, date_limit=limit)
    index_result = [item[0] for item in search_result]
    snapshot_urls = snapshot(index_result)

    # 保存会话数据
    session.modified = True
    return render_template('search_result.html', query=query, search_result=search_result, snapshot_urls=snapshot_urls)


@app.route('/history')
def history():
    global history_map, current
    empty_flag = len(history_map) == 0 or (len(history_map) != 0 and history_map[0] == '')
    return render_template('history.html', map=history_map, current=current, empty=empty_flag)


@app.route('/clear_history')
def clear_history():
    global history_map, current
    history_map.clear()
    current = 0
    return redirect(url_for('index'))


@app.route('/new_session')
def new_session():
    global history_map, current
    if len(history_map) == 0:
        current = 0
    else:
        current += 1
    history_map[current] = ''

    return redirect(url_for('index'))


@app.route('/switch_session/<int:session_id>')
def switch_session(session_id):
    global history_map, current
    # 切换到指定的会话
    if 0 <= session_id < len(history_map):
        current = session_id
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
