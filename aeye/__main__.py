import sys
import subprocess


def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    try:
        import PySide6
        return True
    except ImportError:
        print("⚠️  PySide6 未安装")
        print()
        print("AEye 需要 PySide6 才能运行。")
        print()
        
        # 询问用户是否安装
        try:
            if sys.platform == "win32":
                response = input("是否现在安装 PySide6？(y/n): ")
            else:
                response = input("是否现在安装 PySide6？(y/n): ")
        except (EOFError, KeyboardInterrupt):
            print()
            print("已取消。")
            return False
        
        if response.lower() in ["y", "yes", "是"]:
            print()
            print("正在安装 PySide6...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
                print()
                print("✅ PySide6 安装成功！")
                print()
                return True
            except subprocess.CalledProcessError:
                print()
                print("❌ PySide6 安装失败！")
                print()
                print("请手动运行：pip install PySide6")
                print()
                return False
        else:
            print()
            print("已取消安装，无法启动 AEye。")
            print()
            return False


if __name__ == "__main__":
    # 检查依赖
    if not check_and_install_dependencies():
        sys.exit(1)
    
    # 导入并运行主程序
    from aeye.cli import main
    raise SystemExit(main())
