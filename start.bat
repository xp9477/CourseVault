@echo off

REM 创建虚拟环境（如果不存在）
if not exist venv (
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate

REM 安装依赖
pip install -r requirements.txt

REM 设置环境变量
set FLASK_ENV=development
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin123

REM 运行应用
python run.py 