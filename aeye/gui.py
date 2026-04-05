from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QFont


def check_command_available(cmd: str) -> bool:
    """检查命令是否可用"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["where", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
        return result.returncode == 0
    except Exception:
        return False


def detect_virtual_env(project_path: pathlib.Path) -> Optional[tuple[str, list[str]]]:
    """检测项目是否使用 Poetry 或 UV 虚拟环境"""
    if (project_path / "pyproject.toml").exists():
        pyproject_content = (project_path / "pyproject.toml").read_text()
        if "poetry" in pyproject_content.lower():
            if check_command_available("poetry"):
                return "poetry", ["poetry", "run", "python"]
    
    if (project_path / "uv.lock").exists():
        if check_command_available("uv"):
            return "uv", ["uv", "run", "python"]
    
    if (project_path / ".venv").exists():
        if sys.platform == "win32":
            python_path = project_path / ".venv" / "Scripts" / "python.exe"
        else:
            python_path = project_path / ".venv" / "bin" / "python"
        if python_path.exists():
            return "venv", [str(python_path)]
    
    return None


def find_python_files(directory: pathlib.Path) -> list[pathlib.Path]:
    """查找目录下所有 Python 文件"""
    python_files = []
    try:
        for item in directory.iterdir():
            if item.is_file() and item.suffix == ".py":
                python_files.append(item)
    except (PermissionError, FileNotFoundError):
        pass
    return sorted(python_files)


class AEyeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_path: Optional[pathlib.Path] = None
        self.python_cmd: list[str] = [sys.executable]
        self.process: Optional[QProcess] = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("AEye GUI 调试助手")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        project_group = QGroupBox("1. 选择项目文件夹")
        project_layout = QHBoxLayout()
        
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText("选择或输入项目文件夹路径...")
        project_layout.addWidget(self.project_path_edit)
        
        browse_btn = QPushButton("📁 浏览...")
        browse_btn.clicked.connect(self.browse_project)
        project_layout.addWidget(browse_btn)
        
        project_group.setLayout(project_layout)
        main_layout.addWidget(project_group)
        
        self.info_group = QGroupBox("2. 项目信息")
        info_layout = QVBoxLayout()
        
        self.venv_label = QLabel("虚拟环境: 未检测")
        self.venv_label.setStyleSheet("color: gray;")
        info_layout.addWidget(self.venv_label)
        
        self.info_group.setLayout(info_layout)
        self.info_group.setEnabled(False)
        main_layout.addWidget(self.info_group)
        
        self.file_group = QGroupBox("3. 选择启动文件")
        file_layout = QHBoxLayout()
        
        file_layout.addWidget(QLabel("Python 文件:"))
        self.file_combo = QComboBox()
        self.file_combo.currentTextChanged.connect(self.on_file_changed)
        file_layout.addWidget(self.file_combo, 1)
        
        self.file_group.setLayout(file_layout)
        self.file_group.setEnabled(False)
        main_layout.addWidget(self.file_group)
        
        self.args_group = QGroupBox("4. 启动参数（可选）")
        args_layout = QHBoxLayout()
        
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("例如: --debug --port 8080")
        args_layout.addWidget(self.args_edit)
        
        self.args_group.setLayout(args_layout)
        self.args_group.setEnabled(False)
        main_layout.addWidget(self.args_group)
        
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 启动 AEye 调试")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_debug)
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_debug)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        log_group = QGroupBox("输出日志")
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Menlo", 10))
        log_layout.addWidget(self.log_output)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group, 1)
    
    def browse_project(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择项目文件夹",
            str(pathlib.Path.home())
        )
        if directory:
            self.project_path_edit.setText(directory)
            self.load_project(pathlib.Path(directory))
    
    def load_project(self, project_path: pathlib.Path):
        self.project_path = project_path
        
        venv_info = detect_virtual_env(project_path)
        if venv_info:
            venv_type, python_cmd = venv_info
            self.venv_label.setText(f"虚拟环境: ✅ {venv_type.upper()}")
            self.venv_label.setStyleSheet("color: green; font-weight: bold;")
            self.python_cmd = python_cmd
        else:
            self.venv_label.setText("虚拟环境: ℹ️ 使用系统 Python")
            self.venv_label.setStyleSheet("color: blue;")
            self.python_cmd = [sys.executable]
        
        python_files = find_python_files(project_path)
        self.file_combo.clear()
        for f in python_files:
            self.file_combo.addItem(f.name, str(f))
        
        self.info_group.setEnabled(True)
        self.file_group.setEnabled(len(python_files) > 0)
        self.args_group.setEnabled(len(python_files) > 0)
        self.start_btn.setEnabled(len(python_files) > 0)
        
        if len(python_files) == 0:
            QMessageBox.warning(self, "警告", "在选中的文件夹中没有找到 Python 文件")
    
    def on_file_changed(self, text: str):
        pass
    
    def append_log(self, message: str, color: str = "black"):
        self.log_output.append(f'<span style="color:{color}">{message}</span>')
    
    def start_debug(self):
        if not self.project_path or self.file_combo.currentData() is None:
            return
        
        target_file = pathlib.Path(self.file_combo.currentData())
        
        cmd = [
            *self.python_cmd,
            "-m",
            "aeye",
            "--file",
            str(target_file)
        ]
        
        args_text = self.args_edit.text().strip()
        if args_text:
            cmd.extend(["--"] + args_text.split())
        
        self.append_log(f"启动命令: {' '.join(cmd)}", "blue")
        self.append_log(f"工作目录: {self.project_path}", "gray")
        
        self.process = QProcess()
        self.process.setProgram(cmd[0])
        self.process.setArguments(cmd[1:])
        self.process.setWorkingDirectory(str(self.project_path))
        
        self.process.readyReadStandardOutput.connect(self.on_ready_read_stdout)
        self.process.readyReadStandardError.connect(self.on_ready_read_stderr)
        self.process.finished.connect(self.on_process_finished)
        
        self.process.start()
        
        if self.process.waitForStarted(3000):
            self.append_log(f"✅ 程序已启动！PID: {self.process.processId()}", "green")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.append_log(f"❌ 启动失败: {self.process.errorString()}", "red")
    
    def on_ready_read_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            for line in data.strip().split('\n'):
                if line:
                    self.append_log(line, "black")
    
    def on_ready_read_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
            for line in data.strip().split('\n'):
                if line:
                    self.append_log(line, "red")
    
    def on_process_finished(self, exit_code: int, exit_status: int):
        self.append_log(f"程序已退出，退出码: {exit_code}", "gray")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.process = None
    
    def stop_debug(self):
        if self.process:
            self.append_log("正在停止程序...", "orange")
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()


def main():
    app = QApplication(sys.argv)
    window = AEyeGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
