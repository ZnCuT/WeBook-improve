# Simple Installation Script - Lightweight Semantic Search
# Install only essential packages for quick startup

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Lightweight Semantic Search Setup" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  V No large AI models needed" 
Write-Host "  V Download size under 50MB"
Write-Host "  V Fast installation"
Write-Host "  V Smart search still works"
Write-Host ""

# Upgrade pip
Write-Host "[1/2] Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install lightweight dependencies
Write-Host "[2/2] Installing packages..." -ForegroundColor Cyan
pip install -r requirements_simple.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "V Installation successful!" -ForegroundColor Green
    Write-Host ""
    
    # Verify core packages
    Write-Host "Verifying installation:" -ForegroundColor White
    $packages = @("flask", "pymysql", "jieba")
    
    foreach ($pkg in $packages) {
        python -c "import $pkg; print('OK')" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  V $pkg" -ForegroundColor Green
        } else {
            if ($pkg -eq "jieba") {
                Write-Host "  ! $pkg (optional, will fallback)" -ForegroundColor Yellow
            } else {
                Write-Host "  X $pkg" -ForegroundColor Red
            }
        }
    }
    
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "  Ready to use!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Edit .env file, set database password"
    Write-Host "  2. Run: python app.py"
    Write-Host "  3. Visit: http://localhost:5003"
    Write-Host ""
    Write-Host "Semantic search features:" -ForegroundColor Cyan
    Write-Host "  - Synonym matching"
    Write-Host "  - Chinese word segmentation"
    Write-Host "  - Understands programming = coding etc."
    Write-Host ""

} else {
    Write-Host ""
    Write-Host "X Installation failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manual installation:" -ForegroundColor Yellow
    Write-Host "  pip install flask flask-sqlalchemy pymysql python-dotenv"
}