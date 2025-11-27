#!/usr/bin/env python
"""
快速启动云存储系统
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def start_backend():
    """启动后端Django服务"""
    print("🔧 启动后端服务 (Django)")
    print("=" * 40)
    
    backend_dir = Path(__file__).parent
    
    try:
        # 切换到项目根目录
        os.chdir(backend_dir)
        
        # 启动Django开发服务器
        cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
        print(f"执行命令: {' '.join(cmd)}")
        print("后端服务将在 http://localhost:8000 启动")
        print("按 Ctrl+C 停止服务")
        print()
        
        # 在新的命令行窗口中启动后端
        if os.name == 'nt':  # Windows
            subprocess.Popen(['start', 'cmd', '/k', f'cd /d {backend_dir} && {" ".join(cmd)}'], shell=True)
        else:
            subprocess.Popen(cmd)
        
        return True
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return False

def start_frontend():
    """启动前端React服务"""
    print("🎨 启动前端服务 (React)")
    print("=" * 40)
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        # 在新的命令行窗口中启动前端
        if os.name == 'nt':  # Windows
            cmd = f'cd /d {frontend_dir} && set NODE_OPTIONS=--openssl-legacy-provider && set BROWSER=none && npm start'
            subprocess.Popen(['start', 'cmd', '/k', cmd], shell=True)
        else:
            os.chdir(frontend_dir)
            env = os.environ.copy()
            env['NODE_OPTIONS'] = '--openssl-legacy-provider'
            env['BROWSER'] = 'none'
            subprocess.Popen(['npm', 'start'], env=env)
        
        print("前端服务将在 http://localhost:3000 启动")
        print("按 Ctrl+C 停止服务")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 启动前端服务失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 云存储系统快速启动器")
    print("=" * 50)
    print()
    
    print("📋 启动服务...")
    print()
    
    # 启动后端服务
    if not start_backend():
        print("\n❌ 后端服务启动失败")
        input("按回车键退出...")
        return
    
    # 等待后端启动
    print("⏳ 等待后端服务启动...")
    time.sleep(3)
    
    # 启动前端服务
    if not start_frontend():
        print("\n❌ 前端服务启动失败")
        input("按回车键退出...")
        return
    
    print("\n🎉 服务启动完成！")
    print("=" * 40)
    print("📱 前端地址: http://localhost:3000")
    print("🔧 后端地址: http://localhost:8000")
    print("📋 API文档: http://localhost:8000/api/")
    print()
    print("👤 演示账号:")
    print("   用户名: demo")
    print("   密码: demo123")
    print()
    print("💡 提示:")
    print("   - 后端和前端服务会在新的命令行窗口中运行")
    print("   - 要停止服务，请关闭对应的命令行窗口")
    print("   - 确保MySQL和OpenStack服务正在运行")
    print()
    
    input("按回车键退出启动器...")

if __name__ == "__main__":
    main()