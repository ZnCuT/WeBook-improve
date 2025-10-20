# WeBook - 二手书交易平台# WEBOOK - 二手书交易平台



一个基于Flask的二手书交易网站，支持用户注册、图书上传、搜索和交易功能。一个基于 Flask 的二手书交易平台，集成了**智能语义检索**功能，支持用户通过关键词或自然语言描述查找书籍。



## 🚀 功能特性## ✨ 核心功能



- 📚 **图书管理**: 上传、浏览、搜索图书- 📚 **商品管理**: 上传、浏览、搜索二手书籍

- 👥 **用户系统**: 注册、登录、个人资料管理- 🔐 **用户系统**: 注册、登录、会话管理

- 🔍 **智能搜索**: 关键词搜索 + 语义搜索- 🔍 **双模式搜索**:

- 📱 **响应式设计**: 支持多种设备访问  - 关键词搜索: 精确匹配书名和描述

- 🗄️ **数据库**: SQLite（开发）/ MySQL（生产）  - **语义搜索**: 基于 AI 理解查询含义，智能匹配相关书籍

- 🖼️ **图片上传**: 支持书籍封面上传和展示

## 📁 项目结构- 💾 **数据持久化**: MySQL 数据库存储



```## 🛠️ 技术栈

WeBook/

├── app.py                 # Flask主应用### 后端

├── config.py              # 配置文件- **Flask**: Web 框架

├── simple_semantic.py     # 轻量级语义搜索- **SQLAlchemy**: ORM 数据库映射

├── init_db.py            # 数据库初始化- **Flask-Bcrypt**: 密码加密

├── requirements.txt       # 依赖包列表- **PyMySQL**: MySQL 数据库驱动

├── .env                  # 环境变量配置

├── templates/            # HTML模板### 语义检索

│   ├── login.html- **Sentence-Transformers**: 文本向量化模型

│   ├── register.html- **Faiss**: 高效向量相似度搜索

│   ├── homepage.html- **PyTorch**: 深度学习框架

│   ├── search.html

│   ├── upload.html## 📋 环境要求

│   └── ...

├── static/               # 静态资源- Python 3.8+

│   ├── css/             # 样式文件- MySQL 5.7+ / 8.0+

│   ├── js/              # JavaScript文件- 至少 2GB 可用内存（用于加载语义模型）

│   ├── images/          # 图片资源

│   └── uploads/         # 用户上传文件## 🚀 快速开始

├── scripts/             # 安装和启动脚本

├── docs/               # 项目文档### 1. 克隆项目

└── venv/               # 虚拟环境（可选）

``````bash

cd c:\Users\12641\Desktop\WeBook

## 🛠️ 安装和运行```



1. **激活conda环境**### 2. 创建虚拟环境（推荐）

   ```bash

   conda activate base```powershell

   ```python -m venv venv

.\venv\Scripts\Activate.ps1

2. **安装依赖**```

   ```bash

   pip install -r requirements.txt### 3. 安装依赖

   ```

```powershell

3. **配置环境变量**pip install -r requirements.txt

   - 编辑 `.env` 文件设置数据库配置```



4. **启动应用****注意**: 首次安装会下载语义模型（约 100MB），请保持网络畅通。

   ```bash

   python app.py### 4. 配置数据库

   ```

#### 方式一: 使用 MySQL 命令行

5. **访问网站**

   - 打开浏览器访问: http://127.0.0.1:5003```sql

mysql -u root -p

## 🎯 主要页面CREATE DATABASE webook_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

EXIT;

- **首页**: `/` - 登录页面```

- **注册**: `/register` - 新用户注册

- **主页**: `/homepage` - 图书浏览#### 方式二: 使用 MySQL Workbench 或其他图形化工具

- **搜索**: `/search` - 图书搜索（支持语义搜索）

- **上传**: `/upload` - 图书上传创建数据库 `webook_db`，字符集选择 `utf8mb4`。

- **数据管理**: `/check_data` - 查看所有图书

### 5. 配置环境变量

## 🔧 技术栈

编辑 `.env` 文件，修改数据库连接信息：

- **后端**: Flask, SQLAlchemy, Bcrypt

- **前端**: HTML5, CSS3, JavaScript```env

- **数据库**: SQLite (默认) / MySQLDB_HOST=127.0.0.1

- **搜索**: 轻量级语义搜索 + 传统关键词搜索DB_PORT=3306

- **文件上传**: Werkzeug文件处理DB_USER=root

DB_PASSWORD=你的密码

## 📝 开发说明DB_NAME=webook_db

```

该项目已经过重新整理，采用标准的Flask项目结构：

- 所有CSS文件统一放在 `static/css/` 目录### 6. 初始化数据库和索引

- 所有JavaScript文件放在 `static/js/` 目录  

- 所有图片资源放在 `static/images/` 目录```powershell

- 用户上传文件放在 `static/uploads/` 目录python init_db.py

- 安装脚本放在 `scripts/` 目录```

- 项目文档放在 `docs/` 目录

在菜单中选择 `4` (全部执行) 以：

## 🤝 贡献- 创建数据库表

- 添加示例数据

欢迎提交Issue和Pull Request来改进这个项目！- 构建语义检索索引

### 7. 启动应用

```powershell
python app.py
```

访问: http://localhost:5003

## 📖 使用指南

### 语义搜索示例

#### 关键词搜索
输入: `Python`
结果: 精确匹配包含 "Python" 的书名或描述

#### 语义搜索
输入: `我想学习人工智能`
结果: 智能匹配《深度学习入门》、《机器学习实战》等相关书籍

输入: `编程基础教程`
结果: 匹配《Python编程从入门到实践》等入门类书籍

### API 接口

#### 语义搜索 API
```http
POST /api/semantic_search
Content-Type: application/json

{
  "query": "数据结构算法",
  "top_k": 10
}
```

#### 重建索引 API
```http
POST /api/rebuild_index
```

## 🔧 项目结构

```
WeBook/
├── app.py                  # Flask 主应用
├── config.py              # 配置文件
├── semantic_search.py     # 语义检索服务
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # 依赖清单
├── .env                  # 环境变量配置
├── templates/            # HTML 模板
│   ├── login.html
│   ├── register.html
│   ├── homepage.html
│   ├── search.html      # 搜索页面（含语义检索）
│   └── ...
├── uploads/             # 用户上传文件
│   └── images/         # 图片资源
└── data/               # 数据文件
    ├── faiss_index.bin      # Faiss 向量索引
    └── faiss_index_metadata.pkl  # 索引元数据
```

## ⚙️ 配置说明

### 语义模型配置

在 `.env` 中可以更换不同的语义模型：

```env
# 多语言模型（默认，支持中文）
SEMANTIC_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# 中文专用模型（更好的中文效果，但体积更大）
# SEMANTIC_MODEL=shibing624/text2vec-base-chinese

# 英文模型（仅英文场景）
# SEMANTIC_MODEL=all-MiniLM-L6-v2
```

### 向量维度

不同模型有不同的向量维度，需在 `.env` 中匹配：

- `paraphrase-multilingual-MiniLM-L12-v2`: 384
- `all-MiniLM-L6-v2`: 384
- `text2vec-base-chinese`: 768

## 🐛 常见问题

### 1. 导入错误: 无法解析导入 "xxx"

**原因**: 依赖未安装或虚拟环境未激活

**解决**:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 数据库连接失败

**检查清单**:
- MySQL 服务是否启动
- 数据库名称是否正确创建
- `.env` 中的用户名密码是否正确
- 防火墙是否阻止连接

### 3. 语义搜索无结果

**可能原因**:
- 索引未创建，运行 `python init_db.py` 选择选项 3
- 数据库无商品数据
- 模型加载失败，检查网络和磁盘空间

### 4. 首次运行很慢

**原因**: 首次运行需要下载语义模型（约 100MB）

**解决**: 耐心等待下载完成，模型会缓存到本地

## 🔄 数据管理

### 重建索引

当商品数据变更较多时，建议重建索引：

```powershell
python init_db.py
# 选择选项 3
```

或通过 API:
```bash
curl -X POST http://localhost:5003/api/rebuild_index
```

### 备份数据

```bash
mysqldump -u root -p webook_db > backup.sql
```

### 恢复数据

```bash
mysql -u root -p webook_db < backup.sql
```

## 📊 性能优化

- **索引缓存**: Faiss 索引会自动保存到磁盘，重启后快速加载
- **批量添加**: 新增大量商品后，使用重建索引而非逐个添加
- **模型选择**: 小模型速度快但精度略低，可根据需求调整

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**开发者**: WeBook Team  
**最后更新**: 2025年10月16日# WeBook-improve
