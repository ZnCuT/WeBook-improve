# WeBook 快速启动脚本

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  WeBook 二手书交易平台启动工具" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[✓] 发现虚拟环境" -ForegroundColor Green
    Write-Host "正在激活虚拟环境..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "[!] 未发现虚拟环境，将使用系统 Python" -ForegroundColor Yellow
    $createVenv = Read-Host "是否创建虚拟环境? (y/n)"
    if ($createVenv -eq 'y') {
        Write-Host "正在创建虚拟环境..." -ForegroundColor Yellow
        python -m venv venv
        & "venv\Scripts\Activate.ps1"
        Write-Host "[✓] 虚拟环境创建成功" -ForegroundColor Green
    }
}

# 检查依赖
Write-Host ""
Write-Host "正在检查依赖..." -ForegroundColor Yellow

$flaskInstalled = python -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Flask 未安装" -ForegroundColor Red
    $installDeps = Read-Host "是否安装所有依赖? (y/n)"
    if ($installDeps -eq 'y') {
        Write-Host "正在安装依赖，这可能需要几分钟..." -ForegroundColor Yellow
        pip install -r requirements.txt
        Write-Host "[✓] 依赖安装完成" -ForegroundColor Green
    } else {
        Write-Host "[!] 缺少必要依赖，程序可能无法运行" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[✓] 依赖检查通过" -ForegroundColor Green
}

# 检查数据库
Write-Host ""
Write-Host "正在检查数据库配置..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "[✓] 发现配置文件 .env" -ForegroundColor Green
} else {
    Write-Host "[!] 未找到 .env 配置文件" -ForegroundColor Red
    Write-Host "请先配置数据库信息" -ForegroundColor Yellow
    exit 1
}

# 询问是否初始化数据库
Write-Host ""
$initDb = Read-Host "是否需要初始化数据库? (首次运行请选择 y) (y/n)"
if ($initDb -eq 'y') {
    Write-Host "启动数据库初始化工具..." -ForegroundColor Yellow
    python init_db.py
}

# 启动应用
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  准备启动 WeBook 应用" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址: http://localhost:5003" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2

python app.py
