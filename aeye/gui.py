from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog,
    QGroupBox, QMessageBox, QStyleFactory, QMenuBar
)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QFont, QAction
from .i18n import I18N


def check_command_available(cmd: str) -> bool:
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


def check_aeye_in_env(python_cmd: list[str], cwd: Optional[pathlib.Path] = None) -> bool:
    try:
        check_cmd = python_cmd + ["-c", "import aeye"]
        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(cwd) if cwd else None
        )
        return result.returncode == 0
    except Exception:
        return False


def install_aeye_to_env(python_cmd: list[str], aeye_path: pathlib.Path, cwd: Optional[pathlib.Path] = None) -> bool:
    try:
        if python_cmd[0] == "poetry":
            install_cmd = ["poetry", "run", "pip", "install", "-e", str(aeye_path)]
        elif python_cmd[0] == "uv":
            install_cmd = ["uv", "pip", "install", "-e", str(aeye_path)]
        else:
            python_exe = python_cmd[0]
            install_cmd = [python_exe, "-m", "pip", "install", "-e", str(aeye_path)]
        
        result = subprocess.run(
            install_cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(cwd) if cwd else None
        )
        return result.returncode == 0
    except Exception:
        return False


def detect_virtual_env(project_path: pathlib.Path) -> Optional[tuple[str, list[str]]]:
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
        self.venv_type: Optional[str] = None
        self.process: Optional[QProcess] = None
        self.aeye_path = pathlib.Path(__file__).parent.parent
        self.i18n = I18N()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(self.i18n.tr("gui_window_title"))
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_label = QLabel(self.i18n.tr("gui_title"))
        self.title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #6366f1; padding: 10px 0;")
        main_layout.addWidget(self.title_label)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        self.project_group = QGroupBox(self.i18n.tr("gui_select_project"))
        project_layout = QHBoxLayout()
        project_layout.setSpacing(10)
        
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText(self.i18n.tr("gui_project_placeholder"))
        self.project_path_edit.setMinimumHeight(40)
        project_layout.addWidget(self.project_path_edit)
        
        self.browse_btn = QPushButton(self.i18n.tr("gui_browse"))
        self.browse_btn.setMinimumHeight(40)
        self.browse_btn.setMinimumWidth(90)
        self.browse_btn.clicked.connect(self.browse_project)
        project_layout.addWidget(self.browse_btn)
        
        self.project_group.setLayout(project_layout)
        grid_layout.addWidget(self.project_group, 0, 0)
        
        self.info_group = QGroupBox(self.i18n.tr("gui_project_info"))
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.venv_label = QLabel(self.i18n.tr("gui_venv_not_detected"))
        self.venv_label.setFont(QFont("Arial", 13))
        info_layout.addWidget(self.venv_label)
        
        self.info_group.setLayout(info_layout)
        self.info_group.setEnabled(False)
        grid_layout.addWidget(self.info_group, 0, 1)
        
        self.file_group = QGroupBox(self.i18n.tr("gui_select_file"))
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)
        
        self.file_label = QLabel(self.i18n.tr("gui_python_file"))
        self.file_label.setFont(QFont("Arial", 11))
        self.file_label.setStyleSheet("color: #1f2937;")
        file_layout.addWidget(self.file_label)
        
        self.file_combo = QComboBox()
        self.file_combo.setMinimumHeight(40)
        self.file_combo.currentTextChanged.connect(self.on_file_changed)
        file_layout.addWidget(self.file_combo, 1)
        
        self.file_group.setLayout(file_layout)
        self.file_group.setEnabled(False)
        grid_layout.addWidget(self.file_group, 1, 0)
        
        self.args_group = QGroupBox(self.i18n.tr("gui_start_args"))
        args_layout = QHBoxLayout()
        
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText(self.i18n.tr("gui_args_placeholder"))
        self.args_edit.setMinimumHeight(40)
        args_layout.addWidget(self.args_edit)
        
        self.args_group.setLayout(args_layout)
        self.args_group.setEnabled(False)
        grid_layout.addWidget(self.args_group, 1, 1)
        
        main_layout.addLayout(grid_layout)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.start_btn = QPushButton(self.i18n.tr("gui_start_debug"))
        self.start_btn.setMinimumHeight(48)
        self.start_btn.clicked.connect(self.start_debug)
        self.start_btn.setEnabled(False)
        self.start_btn.setObjectName("startButton")
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(self.i18n.tr("gui_stop"))
        self.stop_btn.setMinimumHeight(48)
        self.stop_btn.clicked.connect(self.stop_debug)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setObjectName("stopButton")
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        self.log_group = QGroupBox(self.i18n.tr("gui_output_log"))
        log_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Menlo", 11))
        self.log_output.setMinimumHeight(180)
        log_layout.addWidget(self.log_output)
        
        self.log_group.setLayout(log_layout)
        main_layout.addWidget(self.log_group, 1)
        
        self.apply_modern_theme()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        view_menu = menubar.addMenu(self.i18n.tr("gui_menu_view"))
        
        language_menu = view_menu.addMenu(self.i18n.tr("gui_menu_language"))
        
        self.english_action = QAction(self.i18n.tr("gui_menu_english"), self)
        self.english_action.setCheckable(True)
        self.english_action.triggered.connect(lambda: self.set_language("en"))
        language_menu.addAction(self.english_action)
        
        self.chinese_action = QAction(self.i18n.tr("gui_menu_chinese"), self)
        self.chinese_action.setCheckable(True)
        self.chinese_action.triggered.connect(lambda: self.set_language("zh"))
        language_menu.addAction(self.chinese_action)
        
        self.update_language_actions()
        
        help_menu = menubar.addMenu(self.i18n.tr("gui_menu_help"))
        about_action = QAction(self.i18n.tr("gui_menu_about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def update_language_actions(self):
        self.english_action.setChecked(self.i18n.language == "en")
        self.chinese_action.setChecked(self.i18n.language == "zh")
    
    def set_language(self, lang: str):
        if self.i18n.language != lang:
            self.i18n.language = lang
            self.update_language_actions()
            self.retranslate_ui()
    
    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("gui_window_title"))
        self.title_label.setText(self.i18n.tr("gui_title"))
        self.project_group.setTitle(self.i18n.tr("gui_select_project"))
        self.project_path_edit.setPlaceholderText(self.i18n.tr("gui_project_placeholder"))
        self.browse_btn.setText(self.i18n.tr("gui_browse"))
        self.info_group.setTitle(self.i18n.tr("gui_project_info"))
        if self.venv_type:
            self.venv_label.setText(self.i18n.tr("gui_venv", venv_type=self.venv_type.upper()))
        else:
            self.venv_label.setText(self.i18n.tr("gui_venv_not_detected"))
        self.file_group.setTitle(self.i18n.tr("gui_select_file"))
        self.file_label.setText(self.i18n.tr("gui_python_file"))
        self.args_group.setTitle(self.i18n.tr("gui_start_args"))
        self.args_edit.setPlaceholderText(self.i18n.tr("gui_args_placeholder"))
        self.start_btn.setText(self.i18n.tr("gui_start_debug"))
        self.stop_btn.setText(self.i18n.tr("gui_stop"))
        self.log_group.setTitle(self.i18n.tr("gui_output_log"))
        
        menubar = self.menuBar()
        menubar.clear()
        self.create_menu_bar()
    
    def apply_modern_theme(self):
        style_sheet = """
        QMainWindow {
            background-color: #ffffff;
        }
        
        QLabel {
            color: #1f2937;
        }
        
        QGroupBox {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 12px;
            background-color: #fafafa;
            font-weight: 600;
            color: #374151;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            left: 10px;
        }
        
        QLineEdit {
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #ffffff;
            color: #1f2937;
        }
        
        QLineEdit:focus {
            border: 2px solid #6366f1;
        }
        
        QComboBox {
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #ffffff;
            color: #1f2937;
        }
        
        QComboBox QAbstractItemView {
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background-color: #ffffff;
            color: #1f2937;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
            padding: 4px;
        }
        
        QComboBox:focus {
            border: 2px solid #6366f1;
        }
        
        QPushButton {
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 700;
            font-size: 14px;
            color: #ffffff;
            background-color: #6366f1;
        }
        
        QPushButton:hover {
            background-color: #4f46e5;
        }
        
        QPushButton:disabled {
            background-color: #d1d5db;
            color: #6b7280;
        }
        
        QPushButton#startButton {
            background-color: #10b981;
            color: #ffffff;
            font-weight: 700;
        }
        
        QPushButton#startButton:hover {
            background-color: #059669;
        }
        
        QPushButton#startButton:disabled {
            background-color: #d1d5db;
            color: #6b7280;
        }
        
        QPushButton#stopButton {
            background-color: #ef4444;
            color: #ffffff;
            font-weight: 700;
        }
        
        QPushButton#stopButton:hover {
            background-color: #dc2626;
        }
        
        QPushButton#stopButton:disabled {
            background-color: #d1d5db;
            color: #6b7280;
        }
        
        QTextEdit {
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 12px;
            background-color: #1e293b;
            color: #f1f5f9;
        }
        """
        
        self.setStyleSheet(style_sheet)
    
    def browse_project(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("gui_select_directory"),
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
            self.venv_type = venv_type
            self.venv_label.setText(self.i18n.tr("gui_venv", venv_type=venv_type.upper()))
            self.venv_label.setStyleSheet("color: #10b981; font-weight: bold;")
            self.python_cmd = python_cmd
        else:
            self.venv_type = None
            self.venv_label.setText(self.i18n.tr("gui_venv_system"))
            self.venv_label.setStyleSheet("color: #3b82f6;")
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
            QMessageBox.warning(self, self.i18n.tr("gui_warning"), self.i18n.tr("gui_warning_no_python"))
    
    def on_file_changed(self, text: str):
        pass
    
    def append_log(self, message: str, color: str = "#f1f5f9"):
        self.log_output.append(f'<span style="color:{color}">{message}</span>')
    
    def start_debug(self):
        if not self.project_path or self.file_combo.currentData() is None:
            return
        
        target_file = pathlib.Path(self.file_combo.currentData())
        
        if self.venv_type:
            self.append_log(self.i18n.tr("gui_venv_checking", venv_type=self.venv_type.upper()), "#60a5fa")
            
            if not check_aeye_in_env(self.python_cmd, self.project_path):
                self.append_log(self.i18n.tr("gui_aeye_not_found"), "#fbbf24")
                
                install_success = install_aeye_to_env(self.python_cmd, self.aeye_path, self.project_path)
                
                if install_success:
                    self.append_log(self.i18n.tr("gui_aeye_installed", venv_type=self.venv_type.upper()), "#34d399")
                else:
                    self.append_log(self.i18n.tr("gui_aeye_install_failed", aeye_path=self.aeye_path), "#f87171")
                    QMessageBox.critical(
                        self,
                        self.i18n.tr("gui_install_failed"),
                        self.i18n.tr("gui_install_failed_msg", venv_type=self.venv_type.upper(), aeye_path=self.aeye_path)
                    )
                    return
            else:
                self.append_log(self.i18n.tr("gui_aeye_ready"), "#34d399")
        
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
        
        self.append_log(self.i18n.tr("gui_start_cmd", cmd=' '.join(cmd)), "#60a5fa")
        self.append_log(self.i18n.tr("gui_working_dir", path=str(self.project_path)), "#94a3b8")
        
        self.process = QProcess()
        self.process.setProgram(cmd[0])
        self.process.setArguments(cmd[1:])
        self.process.setWorkingDirectory(str(self.project_path))
        
        env = self.process.processEnvironment()
        current_pythonpath = env.value("PYTHONPATH", "")
        aeye_parent_path = str(self.aeye_path)
        if current_pythonpath:
            new_pythonpath = f"{aeye_parent_path}:{current_pythonpath}"
        else:
            new_pythonpath = aeye_parent_path
        env.insert("PYTHONPATH", new_pythonpath)
        self.process.setProcessEnvironment(env)
        
        self.append_log(self.i18n.tr("gui_pythonpath", path=new_pythonpath), "#94a3b8")
        
        self.process.readyReadStandardOutput.connect(self.on_ready_read_stdout)
        self.process.readyReadStandardError.connect(self.on_ready_read_stderr)
        self.process.finished.connect(self.on_process_finished)
        
        self.process.start()
        
        if self.process.waitForStarted(3000):
            self.append_log(self.i18n.tr("gui_started", pid=self.process.processId()), "#34d399")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.append_log(self.i18n.tr("gui_start_failed", error=self.process.errorString()), "#f87171")
    
    def on_ready_read_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            for line in data.strip().split('\n'):
                if line:
                    self.append_log(line, "#f1f5f9")
    
    def on_ready_read_stderr(self):
        if self.process:
            data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
            for line in data.strip().split('\n'):
                if line:
                    self.append_log(line, "#f87171")
    
    def on_process_finished(self, exit_code: int, exit_status: int):
        self.append_log(self.i18n.tr("gui_exited", code=exit_code), "#94a3b8")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.process = None
    
    def stop_debug(self):
        if self.process:
            self.append_log(self.i18n.tr("gui_stopping"), "#fbbf24")
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
    
    def show_about(self):
        QMessageBox.about(
            self,
            self.i18n.tr("gui_menu_about"),
            f"{self.i18n.tr('gui_title')}\n\nA GUI debug helper for AEye"
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = AEyeGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
