#!/usr/bin/env python3
"""
论文数据库管理系统
- 从CSV导入论文数据到SQLite数据库
- 提供查询、搜索、统计等功能
- 支持数据更新和管理
"""
import sqlite3
import pandas as pd
import pathlib
import re
from datetime import datetime
import json

class PaperDatabaseManager:
    def __init__(self, db_path="papers.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建论文主表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            venue TEXT,
            category TEXT,
            pdf_url TEXT,
            file_path TEXT,
            file_size INTEGER,
            download_status TEXT DEFAULT 'unknown',
            download_date DATE,
            keywords TEXT,  -- JSON格式存储关键词
            abstract TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建分类表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            paper_count INTEGER DEFAULT 0
        )
        ''')
        
        # 创建标签表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#blue'
        )
        ''')
        
        # 创建论文-标签关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS paper_tags (
            paper_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (paper_id, tag_id),
            FOREIGN KEY (paper_id) REFERENCES papers(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
        ''')
        
        # 创建下载历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER,
            download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            error_message TEXT,
            file_size INTEGER,
            FOREIGN KEY (paper_id) REFERENCES papers(id)
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_keywords ON papers(keywords)')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库初始化完成: {self.db_path}")
    
    def import_from_csv(self, csv_path):
        """从CSV文件导入数据"""
        if not pathlib.Path(csv_path).exists():
            print(f"❌ CSV文件不存在: {csv_path}")
            return False
        
        try:
            df = pd.read_csv(csv_path)
            print(f"📊 读取CSV文件: {len(df)} 条记录")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported = 0
            updated = 0
            
            for index, row in df.iterrows():
                title = row.get('Title', '')
                year = self._extract_year(row.get('Year', ''))
                venue = row.get('Venue', '')
                category = row.get('Category', '')
                pdf_url = row.get('PDF', '')
                file_path = row.get('File', '')
                
                # 检查文件状态
                download_status = self._check_download_status(file_path)
                file_size = self._get_file_size(file_path)
                
                # 提取关键词
                keywords = self._extract_keywords(title)
                
                # 检查是否已存在
                cursor.execute('SELECT id FROM papers WHERE title = ? AND pdf_url = ?', (title, pdf_url))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录
                    cursor.execute('''
                    UPDATE papers SET 
                        year = ?, venue = ?, category = ?, file_path = ?, 
                        file_size = ?, download_status = ?, keywords = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    ''', (year, venue, category, file_path, file_size, download_status, 
                          json.dumps(keywords), existing[0]))
                    updated += 1
                else:
                    # 插入新记录
                    cursor.execute('''
                    INSERT INTO papers (title, year, venue, category, pdf_url, file_path, 
                                      file_size, download_status, keywords, download_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (title, year, venue, category, pdf_url, file_path, 
                          file_size, download_status, json.dumps(keywords), 
                          datetime.now().date() if download_status == 'downloaded' else None))
                    imported += 1
                
                # 更新分类统计
                self._update_category_count(cursor, category)
            
            conn.commit()
            conn.close()
            
            print(f"✅ 导入完成: 新增 {imported} 条，更新 {updated} 条")
            return True
            
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return False
    
    def search_papers(self, query="", category="", year=None, limit=50):
        """搜索论文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM papers WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR keywords LIKE ? OR abstract LIKE ?)"
            query_param = f"%{query}%"
            params.extend([query_param, query_param, query_param])
        
        if category:
            sql += " AND category LIKE ?"
            params.append(f"%{category}%")
        
        if year:
            sql += " AND year = ?"
            params.append(year)
        
        sql += " ORDER BY year DESC, title LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_statistics(self):
        """获取数据库统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 总体统计
        cursor.execute("SELECT COUNT(*) FROM papers")
        stats['total_papers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM papers WHERE download_status = 'downloaded'")
        stats['downloaded'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM papers WHERE download_status = 'failed'")
        stats['failed'] = cursor.fetchone()[0]
        
        # 年份分布
        cursor.execute("""
        SELECT year, COUNT(*) 
        FROM papers 
        WHERE year IS NOT NULL 
        GROUP BY year 
        ORDER BY year DESC
        """)
        stats['by_year'] = dict(cursor.fetchall())
        
        # 分类分布
        cursor.execute("""
        SELECT category, COUNT(*) 
        FROM papers 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
        """)
        stats['by_category'] = dict(cursor.fetchall())
        
        # 下载状态分布
        cursor.execute("""
        SELECT download_status, COUNT(*) 
        FROM papers 
        GROUP BY download_status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # 文件大小统计
        cursor.execute("""
        SELECT 
            COUNT(*) as count,
            AVG(file_size) as avg_size,
            SUM(file_size) as total_size
        FROM papers 
        WHERE file_size IS NOT NULL
        """)
        size_stats = cursor.fetchone()
        if size_stats[0] > 0:
            stats['file_sizes'] = {
                'count': size_stats[0],
                'average_mb': round(size_stats[1] / 1024 / 1024, 2) if size_stats[1] else 0,
                'total_mb': round(size_stats[2] / 1024 / 1024, 2) if size_stats[2] else 0
            }
        
        conn.close()
        return stats
    
    def add_tag(self, paper_id, tag_name, color="#blue"):
        """为论文添加标签"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建或获取标签
        cursor.execute("INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)", (tag_name, color))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = cursor.fetchone()[0]
        
        # 关联论文和标签
        cursor.execute("INSERT OR IGNORE INTO paper_tags (paper_id, tag_id) VALUES (?, ?)", (paper_id, tag_id))
        
        conn.commit()
        conn.close()
    
    def export_to_csv(self, output_path="papers_export.csv"):
        """导出数据库到CSV"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT 
            title as Title,
            year as Year,
            venue as Venue,
            category as Category,
            pdf_url as PDF,
            file_path as File,
            download_status as Status,
            file_size as FileSize,
            download_date as DownloadDate
        FROM papers
        ORDER BY year DESC, title
        """
        
        df = pd.read_sql_query(query, conn)
        df.to_csv(output_path, index=False)
        conn.close()
        
        print(f"✅ 数据已导出到: {output_path}")
    
    def _extract_year(self, year_str):
        """提取年份"""
        if isinstance(year_str, (int, float)) and not pd.isna(year_str):
            return int(year_str)
        
        if isinstance(year_str, str):
            match = re.search(r'(\d{4})', year_str)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_keywords(self, title):
        """从标题中提取关键词"""
        if not title:
            return []
        
        # 常见的联邦学习关键词
        fl_keywords = [
            'federated', 'federation', 'privacy', 'differential', 'secure', 'aggregation',
            'distributed', 'decentralized', 'heterogeneous', 'personalized', 'collaborative',
            'communication', 'compression', 'optimization', 'convergence', 'robust'
        ]
        
        title_lower = title.lower()
        found_keywords = []
        
        for keyword in fl_keywords:
            if keyword in title_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _check_download_status(self, file_path):
        """检查文件下载状态"""
        if not file_path:
            return 'no_url'
        
        path = pathlib.Path(file_path)
        if path.exists() and path.stat().st_size > 1000:
            return 'downloaded'
        elif path.exists():
            return 'incomplete'
        else:
            return 'failed'
    
    def _get_file_size(self, file_path):
        """获取文件大小"""
        if not file_path:
            return None
        
        path = pathlib.Path(file_path)
        if path.exists():
            return path.stat().st_size
        
        return None
    
    def _update_category_count(self, cursor, category):
        """更新分类计数"""
        if category:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            cursor.execute("""
            UPDATE categories SET 
                paper_count = (SELECT COUNT(*) FROM papers WHERE category = ?)
            WHERE name = ?
            """, (category, category))

def print_statistics(stats):
    """打印统计信息"""
    print("\n📊 论文数据库统计:")
    print(f"  📋 总论文数: {stats['total_papers']:,}")
    print(f"  ✅ 已下载: {stats['downloaded']:,}")
    print(f"  ❌ 下载失败: {stats['failed']:,}")
    
    if 'file_sizes' in stats:
        print(f"  💾 总大小: {stats['file_sizes']['total_mb']:.1f} MB")
        print(f"  📏 平均大小: {stats['file_sizes']['average_mb']:.1f} MB")
    
    print(f"\n📅 年份分布 (前10):")
    for year, count in list(stats['by_year'].items())[:10]:
        print(f"    {year}: {count} 篇")
    
    print(f"\n📂 分类分布 (前10):")
    for category, count in list(stats['by_category'].items())[:10]:
        print(f"    {category[:50]}: {count} 篇")

def main():
    """主函数"""
    print("🚀 论文数据库管理系统")
    
    # 初始化数据库
    db = PaperDatabaseManager()
    
    # 检查是否有CSV文件
    csv_files = list(pathlib.Path(".").glob("**/index*.csv"))
    
    if csv_files:
        print(f"\n📁 发现CSV文件:")
        for i, csv_file in enumerate(csv_files):
            print(f"  {i+1}. {csv_file}")
        
        choice = input(f"\n选择要导入的CSV文件 (1-{len(csv_files)}, 或按Enter跳过): ")
        
        if choice.strip() and choice.isdigit():
            csv_index = int(choice) - 1
            if 0 <= csv_index < len(csv_files):
                print(f"\n📥 导入CSV文件: {csv_files[csv_index]}")
                db.import_from_csv(csv_files[csv_index])
    
    # 显示统计信息
    stats = db.get_statistics()
    print_statistics(stats)
    
    # 简单的交互界面
    while True:
        print(f"\n🔧 操作选项:")
        print("  1. 搜索论文")
        print("  2. 查看统计")
        print("  3. 导出CSV")
        print("  4. 退出")
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            query = input("输入搜索关键词: ").strip()
            results = db.search_papers(query, limit=20)
            
            print(f"\n🔍 搜索结果 ({len(results)} 条):")
            for paper in results:
                status_icon = "✅" if paper[7] == 'downloaded' else "❌" if paper[7] == 'failed' else "⏳"
                print(f"  {status_icon} [{paper[2]}] {paper[1][:80]}...")
        
        elif choice == "2":
            stats = db.get_statistics()
            print_statistics(stats)
        
        elif choice == "3":
            output_path = input("输出文件名 (默认: papers_export.csv): ").strip()
            if not output_path:
                output_path = "papers_export.csv"
            db.export_to_csv(output_path)
        
        elif choice == "4":
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main() 