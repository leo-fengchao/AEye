from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Optional

from aeye.launcher import launch_target


CONFIG_FILE = pathlib.Path.home() / ".aeye_config.json"


def load_config() -> dict:
    """加载配置文件"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}


def save_config(config: dict) -> None:
    """保存配置文件"""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def check_poetry_available() -> bool:
    """检查 Poetry 是否可用"""
    try:
        result = subprocess.run(
            ["poetry", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def check_poetry_project() -> bool:
    """检查当前目录是否是 Poetry 项目"""
    return (pathlib.Path.cwd() / "pyproject.toml").exists()


def install_in_system() -> None:
    """在系统环境中安装 aeye"""
    print("正在在系统环境中安装 aeye...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
    config = load_config()
    config["env_type"] = "system"
    save_config(config)
    print("✅ 安装完成！")


def install_in_poetry() -> None:
    """在 Poetry 虚拟环境中安装 aeye"""
    print("正在在 Poetry 虚拟环境中安装 aeye...")
    # 使用 poetry install 而不是 poetry add
    subprocess.run(["poetry", "install"], check=True)
    config = load_config()
    config["env_type"] = "poetry"
    save_config(config)
    print("✅ 安装完成！")


def first_run_setup() -> None:
    """首次运行设置"""
    print("=" * 60)
    print("👁️  欢迎使用 AEye！")
    print("=" * 60)
    print()
    
    config = load_config()
    
    # 检查是否已经配置过
    if "env_type" in config:
        return
    
    # 直接设置为系统环境模式，跳过安装步骤
    # 用户可以后续再决定是否安装
    config["env_type"] = "system"
    save_config(config)
    print("已设置为系统环境模式，直接启动 GUI...")
    print()


def run_gui() -> None:
    """运行 GUI"""
    from aeye.gui import main
    main()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aeye",
        description="Launch a PySide6 app with the AEye runtime inspector enabled.",
    )
    
    subparsers = parser.add_subparsers(title="子命令", dest="subcommand")
    
    # gui 子命令
    gui_parser = subparsers.add_parser("gui", help="启动 AEye GUI 调试助手")
    
    # 直接执行文件的命令
    parser.add_argument(
        "--file",
        required=False,
        help="Python entry file to execute.",
    )
    
    return parser


def main(argv: list[str] | None = None) -> int:
    # 如果没有任何参数，直接启动 GUI
    if argv is None:
        argv = sys.argv[1:]
    
    if not argv:
        # 首次运行设置
        first_run_setup()
        print("未指定参数，启动 AEye GUI 调试助手...")
        run_gui()
        return 0
    
    # 否则正常解析参数
    parser = build_parser()
    args, unknown_args = parser.parse_known_args(argv)
    
    # 首次运行设置
    first_run_setup()
    
    # 如果是 gui 子命令
    if args.subcommand == "gui":
        run_gui()
        return 0
    
    # 原有行为
    if args.file:
        target = pathlib.Path(args.file).expanduser().resolve()
        if not target.exists():
            parser.error(f"Target file does not exist: {target}")
        
        # 处理传递给目标文件的参数
        file_args = list(unknown_args)
        if file_args[:1] == ["--"]:
            file_args = file_args[1:]
        
        launch_target(target, file_args)
        return 0
    
    # 默认启动 GUI
    print("未指定参数，启动 AEye GUI 调试助手...")
    run_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
