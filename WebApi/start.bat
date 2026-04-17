@echo off
chcp 65001 >nul
echo ========================================
echo PyWeixin Web API 启动脚本
echo ========================================
echo.

echo [1/3] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo [2/3] 检查微信状态...
echo 请确保微信已启动并登录！
echo.

echo [3/3] 启动服务...
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python app.py

pause
