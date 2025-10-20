# Dependency Installation Fix Script
# Solve setuptools and build tools issues

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Dependency Installation Fix Tool" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upgrade core build tools
Write-Host "[1/3] Upgrading pip, setuptools and wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

if ($LASTEXITCODE -ne 0) {
    Write-Host "X Upgrade failed" -ForegroundColor Red
    exit 1
}
Write-Host "V Core tools upgraded successfully" -ForegroundColor Green

# Step 2: Install dependencies step by step
Write-Host ""
Write-Host "[2/3] Installing basic dependencies..." -ForegroundColor Yellow

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
    Write-Host "  Installing $package" -ForegroundColor Gray
    pip install $package --no-cache-dir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  X $package installation failed" -ForegroundColor Red
    }
}

Write-Host "V Basic dependencies installed" -ForegroundColor Green

# Step 3: Install semantic search dependencies
Write-Host ""
Write-Host "[3/3] Installing semantic search dependencies (may take 5-10 minutes)..." -ForegroundColor Yellow

Write-Host "  Installing numpy..." -ForegroundColor Gray
pip install "numpy>=1.24.0,<2.0.0" --no-cache-dir

Write-Host "  Installing torch (large package, please wait)..." -ForegroundColor Gray
pip install "torch>=2.6.0,<3.0.0" --no-cache-dir

Write-Host "  Installing sentence-transformers..." -ForegroundColor Gray
pip install "sentence-transformers>=2.2.0" --no-cache-dir

Write-Host "  Installing faiss-cpu..." -ForegroundColor Gray
pip install "faiss-cpu>=1.7.0" --no-cache-dir

if ($LASTEXITCODE -ne 0) {
    Write-Host "X Semantic dependencies installation failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "  1. Check network connection"
    Write-Host "  2. Use China mirror:"
    Write-Host "     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
    exit 1
}

Write-Host "V Semantic dependencies installed" -ForegroundColor Green

# Verify installation
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Verifying Installation" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$testPackages = @("flask", "torch", "sentence_transformers", "faiss")

foreach ($pkg in $testPackages) {
    $result = python -c "import $pkg; print('OK')" 2>&1
    if ($result -like "*OK*") {
        Write-Host "  V $pkg" -ForegroundColor Green
    } else {
        Write-Host "  X $pkg import failed" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure database: Edit .env file"
Write-Host "  2. Initialize data: python init_db.py"
Write-Host "  3. Start application: python app.py"
Write-Host ""
