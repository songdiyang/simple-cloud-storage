#!/usr/bin/env python
"""
简单启动云存储系统
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def start_services():
    """启动后端和前端服务"""
    print("🚀 启动云存储系统")
    print("=" * 40)
    
    # 启动后端
    print("🔧 启动后端服务...")
    backend_dir = Path(__file__).parent.parent  # 项目根目录
    backend_cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
    
    if os.name == 'nt':  # Windows
        subprocess.Popen(['start', 'cmd', '/k', f'cd /d {backend_dir} && {" ".join(backend_cmd)}'], shell=True)
    else:
        subprocess.Popen(backend_cmd, cwd=backend_dir)
    
    print("✅ 后端服务启动中: http://localhost:8000")
    
    # 等待后端启动
    time.sleep(3)
    
    # 启动前端
    print("🎨 启动前端服务...")
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    if os.name == 'nt':  # Windows
        frontend_cmd = f'cd /d {frontend_dir} && set NODE_OPTIONS=--openssl-legacy-provider && set BROWSER=none && npm start -- --host 0.0.0.0'
        subprocess.Popen(['start', 'cmd', '/k', frontend_cmd], shell=True)
    else:
        env = os.environ.copy()
        env['NODE_OPTIONS'] = '--openssl-legacy-provider'
        env['BROWSER'] = 'none'
        subprocess.Popen(['npm', 'start'], cwd=frontend_dir, env=env)
    
    print("✅ 前端服务启动中: http://localhost:3000")
    
    print("\n🎉 服务启动完成！")
    print("=" * 40)
    print("📱 前端: http://localhost:3000")
    print("🔧 后端: http://localhost:8000")
    print("👤 登录: demo/demo123")

if __name__ == "__main__":
    start_services()
    input("\n按回车键退出...")