# WeBook 部署流程详解

本文档提供详细的步骤指导，帮助你从零开始部署 WeBook 二手书交易平台。

## 📝 部署前准备清单

- [ ] 安装 Python 3.8 或更高版本
- [ ] 安装 MySQL 5.7 或更高版本
- [ ] 确保有稳定的网络连接（首次会下载模型）
- [ ] 至少 2GB 可用内存
- [ ] 至少 500MB 可用磁盘空间

## 第一步：环境准备

### 1.1 检查 Python 版本

```powershell
python --version
```

应该显示 Python 3.8.x 或更高版本。

### 1.2 检查 MySQL 服务

```powershell
# 检查 MySQL 服务状态
Get-Service MySQL*

# 如果未运行，启动服务
Start-Service MySQL80  # 服务名可能不同
```

或在服务管理器（services.msc）中启动 MySQL 服务。

## 第二步：创建 Python 虚拟环境（推荐）

```powershell
# 进入项目目录
cd c:\Users\12641\Desktop\WeBook

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

**注意**：如果出现执行策略错误，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

激活成功后，命令行前会显示 `(venv)`。

## 第三步：安装依赖包

```powershell
# 升级 pip（可选但推荐）
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**预计耗时**：5-15 分钟（取决于网络速度）

这一步会安装：
- Flask 及相关扩展
- PyMySQL 数据库驱动
- Sentence-Transformers（语义模型库）
- Faiss（向量检索库）
- PyTorch（深度学习框架）

## 第四步：配置数据库

### 4.1 创建数据库

**方法一：使用命令行**

```powershell
# 登录 MySQL
mysql -u root -p
# 输入密码
```

```sql
-- 创建数据库
CREATE DATABASE webook_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 验证数据库
SHOW DATABASES;

-- 退出
EXIT;
```

**方法二：使用图形化工具（如 MySQL Workbench、Navicat）**

1. 连接到 MySQL 服务器
2. 右键 → 创建数据库
3. 数据库名：`webook_db`
4. 字符集：`utf8mb4`
5. 排序规则：`utf8mb4_unicode_ci`

### 4.2 配置连接信息

编辑 `.env` 文件：

```env
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码  # ← 修改这里
DB_NAME=webook_db

# Flask 配置
SECRET_KEY=your-secret-key-change-this-in-production  # ← 生产环境应改为随机字符串
FLASK_ENV=development
DEBUG=True

# 上传文件配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# 语义检索配置
SEMANTIC_MODEL=paraphrase-multilingual-MiniLM-L12-v2
FAISS_INDEX_PATH=data/faiss_index.bin
VECTOR_DIM=384
```

**重要**：将 `DB_PASSWORD` 替换为你的实际 MySQL 密码。

## 第五步：环境检查

运行环境检查脚本，确保所有配置正确：

```powershell
python check_env.py
```

如果所有检查项都显示 ✓，则可以继续。

如果有 ✗ 标记，根据提示解决问题：
- **依赖包未安装**：重新运行 `pip install -r requirements.txt`
- **数据库连接失败**：检查 MySQL 是否启动、密码是否正确
- **配置文件缺失**：确保 `.env` 文件存在且配置正确

## 第六步：初始化数据库

运行初始化脚本：

```powershell
python init_db.py
```

在菜单中选择 **4**（全部执行），这将：

1. ✓ 创建数据库表（users, products）
2. ✓ 添加 5 个示例商品数据
3. ✓ 下载并加载语义模型（首次约 100MB）
4. ✓ 为示例数据构建向量索引

**注意**：首次运行第 3 步会下载模型，需要几分钟，请耐心等待。

## 第七步：启动应用

### 方式一：直接运行

```powershell
python app.py
```

### 方式二：使用快速启动脚本

```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

启动成功后，会看到类似输出：

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5003
Press CTRL+C to quit
```

## 第八步：访问应用

打开浏览器，访问：

```
http://localhost:5003
```

### 功能测试清单

- [ ] 注册新用户
- [ ] 登录系统
- [ ] 浏览首页商品列表
- [ ] **关键词搜索**：输入"Python"，点击搜索
- [ ] **语义搜索**：选择"智能语义搜索"，输入"我想学习编程"
- [ ] 查看商品详情
- [ ] 上传新商品

## 🎯 语义搜索测试用例

测试语义搜索是否工作正常：

| 搜索模式 | 输入查询 | 预期结果 |
|---------|---------|---------|
| 关键词搜索 | `Python` | 仅返回书名或描述包含"Python"的书 |
| 语义搜索 | `Python` | 返回所有编程相关的书 |
| 语义搜索 | `我想学习人工智能` | 返回《深度学习入门》《机器学习实战》等 |
| 语义搜索 | `编程入门教程` | 返回《Python编程从入门到实践》等 |
| 语义搜索 | `算法和数据结构` | 返回《数据结构与算法分析》等 |

## ⚠️ 常见问题排查

### 问题 1：pip install 失败

**症状**：安装依赖时出现网络错误或超时

**解决方案**：
```powershell
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2：数据库连接错误

**症状**：`Can't connect to MySQL server`

**排查步骤**：
1. 确认 MySQL 服务正在运行
2. 检查 `.env` 中的密码是否正确
3. 尝试用同样的凭据登录 MySQL 命令行
4. 检查防火墙是否阻止 3306 端口

### 问题 3：模型下载失败

**症状**：`ConnectionError` 或下载卡住

**解决方案**：
```powershell
# 方法一：使用国内镜像（需手动设置）
$env:HF_ENDPOINT = "https://hf-mirror.com"
python init_db.py

# 方法二：使用代理
# 在 .env 中添加：
# HTTP_PROXY=http://your-proxy:port
# HTTPS_PROXY=http://your-proxy:port
```

### 问题 4：语义搜索无结果

**排查步骤**：
1. 检查索引是否创建：运行 `python init_db.py`，选择选项 3
2. 查看 `data/` 目录是否有 `faiss_index.bin` 文件
3. 检查控制台日志是否有错误信息

### 问题 5：图片无法显示

**症状**：商品图片显示为损坏图标

**解决方案**：
1. 确保 `uploads/images/` 目录存在
2. 检查图片文件权限
3. 查看浏览器控制台的 404 错误
4. 验证 `Product.image` 路径是否正确

## 🔄 后续维护

### 添加新商品后更新索引

```powershell
# 方法一：使用脚本
python init_db.py
# 选择选项 3（重建索引）

# 方法二：使用 API
curl -X POST http://localhost:5003/api/rebuild_index
```

### 备份数据库

```powershell
mysqldump -u root -p webook_db > backup_$(Get-Date -Format 'yyyyMMdd').sql
```

### 停止应用

在运行 `python app.py` 的终端按 `Ctrl+C`

## 🚀 生产环境部署（可选）

如果要部署到生产环境：

1. **修改配置**
   ```env
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=使用随机生成的长字符串
   ```

2. **使用生产级服务器**
   ```powershell
   pip install gunicorn  # Linux/Mac
   pip install waitress  # Windows
   
   # 启动（Windows）
   waitress-serve --port=5003 app:app
   ```

3. **配置反向代理**（Nginx/Apache）

4. **启用 HTTPS**

---

## ✅ 部署完成！

如果所有步骤都成功，你现在已经拥有一个功能完整的二手书交易平台，并支持智能语义搜索功能！

**下一步建议**：
- 📚 阅读 `README.md` 了解更多功能
- 🔧 自定义前端样式和布局
- 🤖 调整语义模型以获得更好的中文效果
- 📊 添加数据分析和统计功能

有问题？查看 `README.md` 的常见问题部分或提交 Issue。
