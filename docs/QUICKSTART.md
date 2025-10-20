# WeBook 快速参考指南

## 🚀 快速启动（5 分钟）

```powershell
# 1. 激活虚拟环境（如果使用）
.\venv\Scripts\Activate.ps1

# 2. 安装依赖（首次）
pip install -r requirements.txt

# 3. 配置 .env 文件（修改数据库密码）

# 4. 初始化数据库（首次）
python init_db.py  # 选择选项 4

# 5. 启动应用
python app.py

# 访问 http://localhost:5003
```

## 📌 常用命令

### 环境管理
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 退出虚拟环境
deactivate

# 查看已安装包
pip list
```

### 数据库操作
```powershell
# 环境检查
python check_env.py

# 数据库初始化
python init_db.py

# 创建数据库（MySQL）
mysql -u root -p
CREATE DATABASE webook_db CHARACTER SET utf8mb4;
```

### 应用运行
```powershell
# 标准启动
python app.py

# 使用快速启动脚本
powershell -ExecutionPolicy Bypass -File start.ps1

# 测试语义搜索
python test_semantic.py
```

## 🔧 配置文件说明

### .env 配置项
```env
# 数据库（必须配置）
DB_HOST=127.0.0.1          # 数据库地址
DB_PORT=3306               # 数据库端口
DB_USER=root               # 数据库用户名
DB_PASSWORD=your_password  # 数据库密码 ← 必须修改
DB_NAME=webook_db          # 数据库名称

# 应用配置
SECRET_KEY=random-secret   # 会话密钥
DEBUG=True                 # 调试模式

# 语义模型（可选调整）
SEMANTIC_MODEL=paraphrase-multilingual-MiniLM-L12-v2  # 默认多语言模型
VECTOR_DIM=384             # 向量维度
```

## 🎯 核心功能 URL

| 功能 | URL | 说明 |
|-----|-----|-----|
| 登录 | http://localhost:5003/ | 首页/登录页 |
| 注册 | http://localhost:5003/register | 用户注册 |
| 首页 | http://localhost:5003/homepage | 商品列表 |
| 搜索 | http://localhost:5003/search | 搜索页面 |
| 上传 | http://localhost:5003/upload | 上传商品 |

## 🔍 语义搜索 API

### 语义搜索
```bash
POST /api/semantic_search
Content-Type: application/json

{
  "query": "我想学习编程",
  "top_k": 10
}

# 响应示例
{
  "results": [
    {
      "id": 1,
      "name": "Python编程从入门到实践",
      "description": "...",
      "price": 35.5,
      "similarity_score": 0.85
    }
  ]
}
```

### 重建索引
```bash
POST /api/rebuild_index

# 响应
{
  "message": "索引重建成功",
  "total_products": 5
}
```

## 📊 目录结构

```
WeBook/
├── app.py                    # Flask 主应用 ⭐
├── config.py                # 配置管理
├── semantic_search.py       # 语义检索服务 ⭐
├── init_db.py              # 数据库初始化工具
├── check_env.py            # 环境检查工具
├── test_semantic.py        # 测试脚本
├── start.ps1               # Windows 启动脚本
├── requirements.txt        # Python 依赖
├── .env                    # 环境配置 ⭐
├── README.md               # 项目文档
├── DEPLOYMENT.md           # 部署指南
├── templates/              # HTML 模板
│   ├── search.html        # 搜索页面（含语义搜索） ⭐
│   └── ...
├── uploads/                # 用户上传文件
└── data/                   # 数据文件
    ├── faiss_index.bin            # Faiss 索引
    └── faiss_index_metadata.pkl   # 索引元数据
```

⭐ = 核心文件

## ⚡ 语义搜索测试用例

### 中文查询
| 输入 | 预期匹配 |
|-----|---------|
| 我想学习人工智能 | 深度学习、机器学习相关书籍 |
| 编程入门教程 | Python、Web 开发等入门书 |
| 数据结构和算法 | 算法、数据结构教材 |

### 英文查询
| 输入 | 预期匹配 |
|-----|---------|
| machine learning | 机器学习、深度学习书籍 |
| web development | Web 开发相关书籍 |
| algorithms | 算法相关书籍 |

## 🐛 故障排查速查表

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| 无法启动应用 | 依赖未安装 | `pip install -r requirements.txt` |
| 数据库连接错误 | MySQL 未启动 | 启动 MySQL 服务 |
| 语义搜索无结果 | 索引未创建 | `python init_db.py` → 选项 3 |
| 图片无法显示 | 路径错误 | 检查 `uploads/` 目录 |
| 模型下载失败 | 网络问题 | 使用镜像源或代理 |

## 🔄 日常维护

### 添加新商品后
```powershell
# 方法一：自动（推荐）
# 上传商品时会自动添加到索引

# 方法二：批量重建
python init_db.py  # 选项 3
```

### 数据库备份
```powershell
# 备份
mysqldump -u root -p webook_db > backup.sql

# 恢复
mysql -u root -p webook_db < backup.sql
```

### 清理缓存
```powershell
# 删除 Python 缓存
Remove-Item -Recurse -Force __pycache__

# 重建虚拟环境（如果依赖有问题）
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📚 扩展阅读

- **Sentence-Transformers**: https://www.sbert.net/
- **Faiss**: https://github.com/facebookresearch/faiss
- **Flask 文档**: https://flask.palletsprojects.com/

## 💡 性能优化提示

1. **索引优化**：定期重建索引以保持性能
2. **模型选择**：小模型速度快，大模型精度高
3. **缓存策略**：Faiss 索引会自动缓存到磁盘
4. **批量操作**：批量添加商品后统一重建索引

## 🎓 下一步学习

1. 自定义前端样式
2. 添加商品分类功能
3. 实现用户个人中心
4. 集成推荐系统
5. 部署到云服务器

---

**需要帮助？** 查看 `DEPLOYMENT.md` 获取详细部署指南
