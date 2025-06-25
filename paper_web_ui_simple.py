#!/usr/bin/env python3
"""
简化版论文数据库Web管理界面 - 不依赖pandas
"""
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import json
from paper_db_manager_simple import PaperDatabaseManager

app = Flask(__name__)
app.secret_key = 'paper_db_secret_key'

# 初始化数据库管理器
db_manager = PaperDatabaseManager()

# HTML模板 (与原版相同)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>论文数据库管理系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: #007bff; color: white; padding: 20px; border-radius: 6px; text-align: center; }
        .stat-card h3 { margin: 0; font-size: 2em; }
        .stat-card p { margin: 5px 0 0 0; }
        .search-box { margin-bottom: 20px; padding: 20px; background: #f8f9fa; border-radius: 6px; }
        .search-box input, .search-box select { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        .search-box button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .search-box button:hover { background: #0056b3; }
        .paper-list { margin-top: 20px; }
        .paper-item { border: 1px solid #ddd; margin-bottom: 10px; padding: 15px; border-radius: 6px; background: white; }
        .paper-title { font-weight: bold; color: #333; margin-bottom: 5px; }
        .paper-meta { color: #666; font-size: 0.9em; }
        .paper-status { float: right; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; }
        .status-downloaded { background: #d4edda; color: #155724; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .status-unknown { background: #d1ecf1; color: #0c5460; }
        .nav-tabs { border-bottom: 2px solid #dee2e6; margin-bottom: 20px; }
        .nav-tab { display: inline-block; padding: 10px 20px; background: #f8f9fa; border: 1px solid #dee2e6; border-bottom: none; cursor: pointer; margin-right: 5px; }
        .nav-tab.active { background: white; border-bottom: 2px solid white; position: relative; z-index: 1; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 论文数据库管理系统</h1>
            <p>简化版 - 不依赖pandas</p>
        </div>
        
        <div class="nav-tabs">
            <div class="nav-tab active" onclick="showTab('dashboard')">📊 仪表板</div>
            <div class="nav-tab" onclick="showTab('search')">🔍 搜索论文</div>
            <div class="nav-tab" onclick="showTab('import')">📥 导入数据</div>
        </div>
        
        <!-- 仪表板选项卡 -->
        <div id="dashboard" class="tab-content active">
            <div class="stats">
                <div class="stat-card">
                    <h3>{{ stats.total_papers }}</h3>
                    <p>总论文数</p>
                </div>
                <div class="stat-card" style="background: #28a745;">
                    <h3>{{ stats.downloaded }}</h3>
                    <p>已下载</p>
                </div>
                <div class="stat-card" style="background: #dc3545;">
                    <h3>{{ stats.failed }}</h3>
                    <p>下载失败</p>
                </div>
            </div>
            
            <h3>📅 年份分布</h3>
            <div style="max-height: 200px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 6px;">
                {% for year, count in stats.by_year.items() %}
                <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                    <span>{{ year }}</span>
                    <span><strong>{{ count }} 篇</strong></span>
                </div>
                {% endfor %}
            </div>
            
            <h3>📂 分类分布</h3>
            <div style="max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 6px;">
                {% for category, count in stats.by_category.items() %}
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #e9ecef;">
                    <span title="{{ category }}">{{ category[:60] }}{% if category|length > 60 %}...{% endif %}</span>
                    <span><strong>{{ count }} 篇</strong></span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- 搜索选项卡 -->
        <div id="search" class="tab-content">
            <div class="search-box">
                <form method="GET" action="/" style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
                    <input type="hidden" name="tab" value="search">
                    <input type="text" name="query" placeholder="搜索关键词..." value="{{ request.args.get('query', '') }}" style="flex: 1; min-width: 200px;">
                    <select name="category" style="min-width: 150px;">
                        <option value="">所有分类</option>
                        {% for category in categories %}
                        <option value="{{ category }}" {% if request.args.get('category') == category %}selected{% endif %}>
                            {{ category[:30] }}{% if category|length > 30 %}...{% endif %}
                        </option>
                        {% endfor %}
                    </select>
                    <input type="number" name="year" placeholder="年份" value="{{ request.args.get('year', '') }}" style="width: 100px;">
                    <button type="submit">🔍 搜索</button>
                </form>
            </div>
            
            {% if papers %}
            <div class="paper-list">
                <h3>搜索结果 ({{ papers|length }} 条)</h3>
                {% for paper in papers %}
                <div class="paper-item">
                    <div class="paper-status status-{{ paper[8] }}">
                        {% if paper[8] == 'downloaded' %}✅ 已下载
                        {% elif paper[8] == 'failed' %}❌ 失败
                        {% else %}⏳ 未知{% endif %}
                    </div>
                    <div class="paper-title">{{ paper[1] }}</div>
                    <div class="paper-meta">
                        📅 {{ paper[2] or 'N/A' }} | 📖 {{ paper[3] or 'N/A' }} | 📂 {{ paper[4][:50] }}{% if paper[4] and paper[4]|length > 50 %}...{% endif %}
                    </div>
                    {% if paper[5] %}
                    <div class="paper-meta">
                        🔗 <a href="{{ paper[5] }}" target="_blank">{{ paper[5][:80] }}{% if paper[5]|length > 80 %}...{% endif %}</a>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        
        <!-- 导入选项卡 -->
        <div id="import" class="tab-content">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 6px;">
                <h3>📥 导入CSV数据</h3>
                <p>由于这是简化版本，暂不支持通过Web界面导入数据。</p>
                <p>数据已在部署时自动导入。</p>
                
                <div style="margin-top: 20px;">
                    <h4>📤 导出数据</h4>
                    <a href="/export" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">导出为CSV</a>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            const tabs = document.querySelectorAll('.nav-tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # 获取统计信息
    stats = db_manager.get_statistics()
    
    # 获取所有分类
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM papers WHERE category IS NOT NULL ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # 处理搜索
    papers = []
    if request.args.get('query') or request.args.get('category') or request.args.get('year'):
        papers = db_manager.search_papers(
            query=request.args.get('query', ''),
            category=request.args.get('category', ''),
            year=int(request.args.get('year')) if request.args.get('year') else None,
            limit=100
        )
    
    return render_template_string(HTML_TEMPLATE, 
                                stats=stats, 
                                categories=categories, 
                                papers=papers,
                                request=request)

@app.route('/export')
def export_csv():
    from flask import send_file
    import tempfile
    import os
    from datetime import datetime
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    temp_file.close()
    
    # 导出数据
    db_manager.export_to_csv(temp_file.name)
    
    return send_file(temp_file.name, 
                    as_attachment=True, 
                    download_name=f'papers_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 