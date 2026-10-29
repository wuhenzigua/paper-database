# 📚 论文数据库 Web 管理系统

一个基于 Flask 的论文数据库管理系统，支持搜索、分类、统计等功能。

## 🌟 功能特性

- 📊 论文统计仪表板
- 🔍 智能搜索和筛选
- 📂 分类管理
- 📥 CSV 数据导入/导出
- 📱 响应式 Web 界面

## 🚀 在线演示

本项目已部署在 Render.com，访问地址：[https://paper-database-7xaw.onrender.com]

## 💻 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

## 📊 数据来源

基于 Awesome-FL 项目的联邦学习论文库数据。

**最新扩展 Latest Expansion:**
- 新增 **视觉-语言模型（VLM）动作识别** 领域论文（2021-2026）
- 包含 CLIP、CoOp、CoCoOp 及其在动作识别中的应用研究
- 查看综合分析文档：[VLM 动作识别技术综述](./VLM_Action_Recognition_Synthesis.md)

## 🛠️ 技术栈

- **后端**: Flask, SQLite, pandas
- **前端**: HTML, CSS, JavaScript
- **部署**: Render.com, Gunicorn

## 📝 更新日志

- 支持 958 篇论文数据
- 智能关键词提取
- 多维度统计分析
- Web 界面优化
