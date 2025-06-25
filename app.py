#!/usr/bin/env python3
"""
Render.com 部署入口文件
"""
import os
from paper_web_ui_simple import app, db_manager

# 确保数据库初始化
if not os.path.exists('papers.db'):
    print("🔧 初始化数据库...")
    
    # 检查是否有示例数据
    if os.path.exists('index.csv'):
        print("📥 导入示例数据...")
        db_manager.import_from_csv('index.csv')
        print("✅ 数据导入完成")
    else:
        print("ℹ️  没有找到示例数据，数据库为空")

# 获取端口
port = int(os.environ.get('PORT', 10000))

# 导出app供gunicorn使用
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False) 