#!/usr/bin/env python3
"""
生产环境部署配置
适用于Render.com、Railway、VPS等部署平台
"""
import os
from paper_web_ui import app, db_manager

# 生产环境配置
if __name__ != '__main__':
    # 部署平台会导入这个模块，不是直接运行
    # 确保数据库初始化
    if not os.path.exists(db_manager.db_path):
        print("正在初始化数据库...")
        db_manager.init_database()
        
        # 尝试导入示例数据
        csv_files = ['index.csv', 'AwesomeFL_PDF/index.csv']
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                print(f"导入数据: {csv_file}")
                db_manager.import_from_csv(csv_file)
                break

# 本地开发环境
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 启动生产环境服务")
    print(f"📱 端口: {port}")
    print(f"🔧 调试模式: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 