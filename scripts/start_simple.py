#!/usr/bin/env python
"""
简单启动云存储系统
"""
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
    
    def start_services(self):
        """启动后端和前端服务"""
        print("🚀 启动云存储系统")
        print("=" * 40)
        
        # 启动后端
        print("🔧 启动后端服务...")
        backend_dir = Path(__file__).parent.parent  # 项目根目录
        backend_cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
        
        if os.name == 'nt':  # Windows
            # 在Windows上使用subprocess创建新窗口，但保存进程引用
            self.backend_process = subprocess.Popen(
                backend_cmd, 
                cwd=backend_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
            )
        else:
            self.backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)
        
        print("✅ 后端服务启动中: http://localhost:8000")
        
        # 等待后端启动
        time.sleep(3)
        
        # 启动前端
        print("🎨 启动前端服务...")
        frontend_dir = Path(__file__).parent.parent / "frontend"
        
        if os.name == 'nt':  # Windows
            env = os.environ.copy()
            env['NODE_OPTIONS'] = '--openssl-legacy-provider'
            env['BROWSER'] = 'none'
            self.frontend_process = subprocess.Popen(
                ['npm', 'start', '--', '--host', '0.0.0.0'], 
                cwd=frontend_dir,
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
            )
        else:
            env = os.environ.copy()
            env['NODE_OPTIONS'] = '--openssl-legacy-provider'
            env['BROWSER'] = 'none'
            self.frontend_process = subprocess.Popen(['npm', 'start'], cwd=frontend_dir, env=env)
        
        print("✅ 前端服务启动中: http://localhost:3000")
        
        print("\n🎉 服务启动完成！")
        print("=" * 40)
        print("📱 前端: http://localhost:3000")
        print("🔧 后端: http://localhost:8000")
        print("👤 登录: demo/demo123")
        print("\n⚠️  按回车键停止所有服务...")
    
    def stop_services(self):
        """停止所有服务"""
        print("\n🛑 正在停止服务...")
        
        if self.backend_process:
            try:
                print("🔧 停止后端服务...")
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ 后端服务已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  强制停止后端服务...")
                self.backend_process.kill()
            except Exception as e:
                print(f"⚠️  停止后端服务时出错: {e}")
        
        if self.frontend_process:
            try:
                print("🎨 停止前端服务...")
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ 前端服务已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  强制停止前端服务...")
                self.frontend_process.kill()
            except Exception as e:
                print(f"⚠️  停止前端服务时出错: {e}")
        
        # 在Windows上，还需要关闭相关的命令行窗口
        if os.name == 'nt':
            try:
                # 强制关闭可能的node和python进程
                subprocess.run(['taskkill', '/F', '/IM', 'node.exe'], capture_output=True)
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
            except:
                pass
        
        print("🎉 所有服务已停止")
    
    def wait_for_input(self):
        """等待用户输入"""
        try:
            while self.running:
                input()  # 等待回车键
                self.running = False
                self.stop_services()
                break
        except KeyboardInterrupt:
            print("\n检测到Ctrl+C，正在停止服务...")
            self.running = False
            self.stop_services()

def main():
    manager = ServiceManager()
    
    try:
        manager.start_services()
        
        # 在单独的线程中等待输入
        input_thread = threading.Thread(target=manager.wait_for_input)
        input_thread.daemon = True
        input_thread.start()
        
        # 主线程等待
        while manager.running:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n检测到中断信号，正在停止服务...")
        manager.stop_services()
    except Exception as e:
        print(f"\n启动过程中出现错误: {e}")
        manager.stop_services()

if __name__ == "__main__":
    main()