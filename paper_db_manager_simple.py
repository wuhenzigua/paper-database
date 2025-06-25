#!/usr/bin/env python3
"""
简化版论文数据库管理系统
不依赖pandas，使用内置的csv模块
"""
import sqlite3
import csv
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
            keywords TEXT,
            abstract TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category)')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库初始化完成: {self.db_path}")
    
    def import_from_csv(self, csv_path):
        """从CSV文件导入数据"""
        if not pathlib.Path(csv_path).exists():
            print(f"❌ CSV文件不存在: {csv_path}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported = 0
            updated = 0
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
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
            sql += " AND (title LIKE ? OR keywords LIKE ?)"
            query_param = f"%{query}%"
            params.extend([query_param, query_param])
        
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
        
        conn.close()
        return stats
    
    def export_to_csv(self, output_path="papers_export.csv"):
        """导出数据库到CSV"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
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
        """)
        
        results = cursor.fetchall()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 写入表头
            writer.writerow(['Title', 'Year', 'Venue', 'Category', 'PDF', 'File', 'Status', 'FileSize', 'DownloadDate'])
            # 写入数据
            writer.writerows(results)
        
        conn.close()
        print(f"✅ 数据已导出到: {output_path}")
    
    def _extract_year(self, year_str):
        """提取年份"""
        if isinstance(year_str, (int, float)):
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

def print_statistics(stats):
    """打印统计信息"""
    print("\n📊 论文数据库统计:")
    print(f"  📋 总论文数: {stats['total_papers']:,}")
    print(f"  ✅ 已下载: {stats['downloaded']:,}")
    print(f"  ❌ 下载失败: {stats['failed']:,}")
    
    print(f"\n📅 年份分布 (前10):")
    for year, count in list(stats['by_year'].items())[:10]:
        print(f"    {year}: {count} 篇")
    
    print(f"\n📂 分类分布 (前10):")
    for category, count in list(stats['by_category'].items())[:10]:
        print(f"    {category[:50]}: {count} 篇") 