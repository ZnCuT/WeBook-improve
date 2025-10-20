# Enhanced Installation Script with Error Handling
# Handles SSL issues and package compatibility

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Enhanced Dependency Installer" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 0: Configure pip for China users (solve SSL issues)
Write-Host "[0/4] Configuring pip for better connectivity..." -ForegroundColor Yellow

# Create pip config directory if not exists
$pipConfigDir = "$env:APPDATA\pip"
if (!(Test-Path $pipConfigDir)) {
    New-Item -ItemType Directory -Path $pipConfigDir -Force | Out-Null
}

# Create pip config file with China mirrors
$pipConfig = @"
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
"@

$pipConfigPath = Join-Path $pipConfigDir "pip.conf"
$pipConfig | Out-File -FilePath $pipConfigPath -Encoding UTF8
Write-Host "V Configured pip to use China mirrors" -ForegroundColor Green

# Step 1: Upgrade core build tools
Write-Host ""
Write-Host "[1/4] Upgrading pip, setuptools and wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

if ($LASTEXITCODE -ne 0) {
    Write-Host "X Core upgrade failed, trying with --user flag..." -ForegroundColor Yellow
    python -m pip install --upgrade --user pip setuptools wheel
}
Write-Host "V Core tools upgraded" -ForegroundColor Green

# Step 2: Install essential dependencies with fallbacks
Write-Host ""
Write-Host "[2/4] Installing essential Flask dependencies..." -ForegroundColor Yellow

$essentialPackages = @(
    "Flask",
    "Flask-SQLAlchemy", 
    "Flask-Migrate",
    "Flask-Bcrypt",
    "Werkzeug",
    "PyMySQL",
    "python-dotenv"
)

foreach ($package in $essentialPackages) {
    Write-Host "  Installing $package..." -ForegroundColor Gray
    pip install $package --no-cache-dir
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  V $package installed" -ForegroundColor Green
    } else {
        Write-Host "  ! $package failed, trying latest version..." -ForegroundColor Yellow
        pip install $package --no-cache-dir --upgrade
    }
}

# Step 3: Install problematic packages with special handling
Write-Host ""
Write-Host "[3/4] Installing packages that need special handling..." -ForegroundColor Yellow

# Pillow - try multiple versions
Write-Host "  Installing Pillow..." -ForegroundColor Gray
$pillowVersions = @("Pillow", "Pillow==10.0.1", "Pillow==9.5.0")
$pillowInstalled = $false

foreach ($version in $pillowVersions) {
    if (!$pillowInstalled) {
        pip install $version --no-cache-dir 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  V Pillow installed ($version)" -ForegroundColor Green
            $pillowInstalled = $true
        }
    }
}

if (!$pillowInstalled) {
    Write-Host "  ! Pillow installation failed - will skip for now" -ForegroundColor Yellow
}

# Cryptography - often causes issues
Write-Host "  Installing cryptography..." -ForegroundColor Gray
pip install cryptography --no-cache-dir
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! Cryptography failed, trying pre-built wheel..." -ForegroundColor Yellow
    pip install --only-binary=cryptography cryptography
}

# Step 4: Install AI/ML dependencies
Write-Host ""
Write-Host "[4/4] Installing AI/ML dependencies (this may take 10+ minutes)..." -ForegroundColor Yellow

# NumPy first
Write-Host "  Installing numpy..." -ForegroundColor Gray
pip install numpy --no-cache-dir
if ($LASTEXITCODE -ne 0) {
    pip install "numpy>=1.21.0" --no-cache-dir
}

# PyTorch - use CPU-only version for faster install
Write-Host "  Installing PyTorch CPU version..." -ForegroundColor Gray
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! PyTorch failed, trying fallback method..." -ForegroundColor Yellow
    pip install torch --no-cache-dir
}

# Sentence Transformers
Write-Host "  Installing sentence-transformers..." -ForegroundColor Gray
pip install sentence-transformers --no-cache-dir
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! sentence-transformers failed, will try minimal version..." -ForegroundColor Yellow
    pip install "sentence-transformers>=2.0.0" --no-cache-dir
}

# Faiss CPU
Write-Host "  Installing faiss-cpu..." -ForegroundColor Gray
pip install faiss-cpu --no-cache-dir
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! faiss-cpu failed, trying alternative..." -ForegroundColor Yellow
    pip install "faiss-cpu>=1.7.0" --no-cache-dir
}

# Final verification
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Installation Verification" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$criticalPackages = @("flask", "pymysql", "dotenv")
$aiPackages = @("numpy", "torch", "sentence_transformers", "faiss")

Write-Host "Critical packages:" -ForegroundColor White
foreach ($pkg in $criticalPackages) {
    $result = python -c "import $pkg; print('OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  V $pkg" -ForegroundColor Green
    } else {
        Write-Host "  X $pkg - REQUIRED" -ForegroundColor Red
    }
}

Write-Host "AI/ML packages:" -ForegroundColor White
foreach ($pkg in $aiPackages) {
    $result = python -c "import $pkg; print('OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  V $pkg" -ForegroundColor Green
    } else {
        Write-Host "  X $pkg - semantic search will not work" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Installation Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if basic Flask app can run
$flaskTest = python -c "import flask, pymysql; print('BASIC_OK')" 2>$null
$aiTest = python -c "import torch, sentence_transformers, faiss; print('AI_OK')" 2>$null

if ($LASTEXITCODE -eq 0 -and $flaskTest -like "*BASIC_OK*") {
    Write-Host "V Basic Flask application ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now:" -ForegroundColor Yellow
    Write-Host "  1. Configure database: Edit .env file" 
    Write-Host "  2. Test basic app: python app.py"
    
    if ($aiTest -like "*AI_OK*") {
        Write-Host "  3. Full setup: python init_db.py" -ForegroundColor Green
        Write-Host ""
        Write-Host "V Semantic search fully supported!" -ForegroundColor Green
    } else {
        Write-Host "  3. Basic mode only (no semantic search)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "! AI packages failed - semantic search disabled" -ForegroundColor Yellow
        Write-Host "  You can still use keyword search functionality"
    }
} else {
    Write-Host "X Critical dependencies missing" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try manual installation:" -ForegroundColor Yellow
    Write-Host "  pip install flask flask-sqlalchemy pymysql python-dotenv"
}

Write-Host ""