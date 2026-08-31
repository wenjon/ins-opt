@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Crystal IG Insights Fetcher
echo ============================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查 .env 文件
if not exist ".env" (
    echo [提示] 未找到 .env 文件
    echo 正在从 .env.example 复制...
    copy .env.example .env
    echo.
    echo [重要] 请编辑 .env 文件，填入你的 IG_BUSINESS_ID 和 IG_ACCESS_TOKEN
    echo 然后重新运行此脚本
    pause
    exit /b 1
)

REM 运行主脚本
echo [开始] 抓取 IG 数据...
echo.
python fetch_insights.py
echo.
echo [完成] 数据已保存到 data 目录
echo.
pause
