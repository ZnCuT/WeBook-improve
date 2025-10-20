# 依赖安装修复脚本
# 解决 setuptools 和构建工具问题

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  依赖安装修复工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 第一步：升级核心构建工具
Write-Host "[1/3] 升级 pip、setuptools 和 wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 升级失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 核心工具升级成功" -ForegroundColor Green

# 第二步：分步安装依赖（避免一次性解析冲突）
Write-Host ""
Write-Host "[2/3] 安装基础依赖..." -ForegroundColor Yellow

$basicPackages = @(
    "Flask==3.0.0",
    "Flask-SQLAlchemy==3.1.1",
    "Flask-Migrate==4.0.5",
    "Flask-Bcrypt==1.0.1",
    "Werkzeug==3.0.1",
    "PyMySQL==1.1.0",
    "cryptography==41.0.7",
    "python-dotenv==1.0.0",
    "Pillow==10.1.0"
)

foreach ($package in $basicPackages) {
    Write-Host "  安装 $package" -ForegroundColor Gray
    pip install $package --no-cache-dir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ $package 安装失败" -ForegroundColor Red
    }
}

Write-Host "✓ 基础依赖安装完成" -ForegroundColor Green

# 第三步：安装语义检索依赖（可能需要较长时间）
Write-Host ""
Write-Host "[3/3] 安装语义检索依赖（这可能需要 5-10 分钟）..." -ForegroundColor Yellow

Write-Host "  安装 numpy..." -ForegroundColor Gray
pip install "numpy>=1.24.0,<2.0.0" --no-cache-dir

Write-Host "  安装 torch (体积较大，请耐心等待）..." -ForegroundColor Gray
pip install "torch>=2.6.0,<3.0.0" --no-cache-dir

Write-Host "  安装 sentence-transformers..." -ForegroundColor Gray
pip install "sentence-transformers>=2.2.0" --no-cache-dir

Write-Host "  安装 faiss-cpu..." -ForegroundColor Gray
pip install "faiss-cpu>=1.7.0" --no-cache-dir

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 语义检索依赖安装失败" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的解决方案：" -ForegroundColor Yellow
    Write-Host "  1. 检查网络连接"
    Write-Host "  2. 使用国内镜像："
    Write-Host "     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
    exit 1
}

Write-Host "✓ 语义检索依赖安装完成" -ForegroundColor Green

# 验证安装
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  验证安装结果" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$testPackages = @("flask", "torch", "sentence_transformers", "faiss")

foreach ($pkg in $testPackages) {
    $result = python -c "import $pkg; print('✓')" 2>&1
    if ($result -like "*✓*") {
        Write-Host "  ✓ $pkg" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $pkg 导入失败" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 配置数据库：编辑 .env 文件"
Write-Host "  2. 初始化数据： python init_db.py"
Write-Host "  3. 启动应用： python app.py"
Write-Host ""
