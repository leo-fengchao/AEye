from __future__ import annotations

import sys
import locale
from dataclasses import dataclass


def _get_system_language() -> str:
    """Get system language, returns 'zh' if simplified Chinese, otherwise 'en'"""
    try:
        # Try getting from locale
        lang, _ = locale.getdefaultlocale()
        if lang and 'zh_CN' in lang:
            return 'zh'
    except (AttributeError, ValueError):
        pass
    
    # Try getting from sys
    try:
        if hasattr(sys, 'getdefaultencoding'):
            pass
        # Check platform-specific methods
        if sys.platform.startswith('win'):
            try:
                import ctypes
                lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                # 2052 is zh-CN
                if lang_id == 2052:
                    return 'zh'
            except:
                pass
        elif sys.platform == 'darwin':  # macOS
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', 'NSGlobalDomain', 'AppleLanguages'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    if 'zh-Hans' in result.stdout or 'zh_CN' in result.stdout:
                        return 'zh'
            except:
                pass
    except:
        pass
    
    return 'en'


TRANSLATIONS = {
    "zh": {
        "menu_root": "AEye",
        "menu_toggle_inspect": "切换检查模式",
        "menu_show_panel": "显示调试面板",
        "menu_export": "导出 AI Prompt",
        "menu_switch_language": "Switch To English",
        "panel_title": "AEye 调试面板",
        "panel_header_title": "AEye",
        "panel_header_subtitle": "记录修改意见，并生成可直接发给 AI 的任务内容。",
        "inspect_toggle": "检查模式",
        "inspect_toggle_on": "检查模式: 开启",
        "inspect_toggle_off": "检查模式: 关闭",
        "current_target_none": "当前目标：未选择",
        "current_target": "当前目标：{selector}",
        "recorded_notes": "已记录修改项",
        "comment_content": "修改意见",
        "comment_placeholder": "输入当前选中 UI 元素的修改建议或功能建议...",
        "btn_add_update": "添加修改意见 ({modifier}+Enter)",
        "btn_remove": "删除选中修改意见",
        "btn_export": "导出 AI Prompt",
        "btn_copy": "复制 AI Prompt",
        "msg_enter_comment": "请先输入修改意见。",
        "msg_select_widget": "请先在界面上选中一个 UI 元素。",
        "msg_exported": "已导出到:\n{path}",
        "msg_copied": "AI Prompt 已复制到剪贴板。",
        "dialog_export_title": "导出 AEye AI Prompt",
        "dialog_export_filename": "aeye_导出.txt",
        "file_filter_text": "文本文件 (*.txt)",
        "none": "（无）",
        "export_intro_1": "下面每个元素都包含运行时定位信息、源码候选和对应的修改意见。",
        "export_intro_2": "请根据这些信息有针对性地修改对应元素，尽量不要影响未提及的界面部分；如果无法唯一定位，优先结合 objectName、源码候选、父级链路、窗口标题和几何信息综合判断。",
        "export_empty_1": "当前还没有可执行的修改任务。",
        "export_empty_2": "请先在检查模式下选中控件，并至少添加一条修改意见。",
        "export_element": "[元素 {index}]",
        "export_locator_block": "定位信息",
        "export_selector": "Selector",
        "export_class": "类名",
        "export_object_name": "objectName",
        "export_window_title": "窗口标题",
        "export_text": "文本",
        "export_geometry": "几何信息",
        "export_parent_chain": "父级链路",
        "export_locator_hint": "定位提示",
        "export_source_candidates": "源码候选",
        "export_comment": "修改意见",
        "gui_window_title": "AEye GUI 调试助手",
        "gui_title": "AEye GUI 调试助手",
        "gui_select_project": "📁 选择项目文件夹",
        "gui_project_placeholder": "选择或输入项目文件夹路径...",
        "gui_browse": "浏览",
        "gui_select_directory": "选择项目文件夹",
        "gui_project_info": "ℹ️ 项目信息",
        "gui_venv_not_detected": "虚拟环境: 未检测",
        "gui_venv": "虚拟环境: {venv_type}",
        "gui_venv_system": "虚拟环境: 使用系统 Python",
        "gui_select_file": "📄 选择启动文件",
        "gui_python_file": "Python 文件:",
        "gui_start_args": "⚙️ 启动参数（可选）",
        "gui_args_placeholder": "例如: --debug --port 8080",
        "gui_start_debug": "🚀 启动调试",
        "gui_stop": "🚫 停止",
        "gui_output_log": "📝 输出日志",
        "gui_warning": "警告",
        "gui_warning_no_python": "在选中的文件夹中没有找到 Python 文件",
        "gui_install_failed": "安装失败",
        "gui_install_failed_msg": "无法将 AEye 自动安装到 {venv_type} 虚拟环境中。\n\n请手动在项目目录中运行：\npip install -e {aeye_path}",
        "gui_venv_checking": "检测到 {venv_type} 虚拟环境，正在检查 AEye...",
        "gui_aeye_not_found": "AEye 未在虚拟环境中检测到，正在自动安装...",
        "gui_aeye_installed": "AEye 已成功安装到 {venv_type} 虚拟环境！",
        "gui_aeye_install_failed": "AEye 安装失败！请手动在该虚拟环境中运行：pip install -e {aeye_path}",
        "gui_aeye_ready": "AEye 已在虚拟环境中就绪",
        "gui_start_cmd": "启动命令: {cmd}",
        "gui_working_dir": "工作目录: {path}",
        "gui_pythonpath": "PYTHONPATH: {path}",
        "gui_started": "程序已启动！PID: {pid}",
        "gui_start_failed": "启动失败: {error}",
        "gui_exited": "程序已退出，退出码: {code}",
        "gui_stopping": "正在停止程序...",
        "gui_menu_view": "视图",
        "gui_menu_language": "语言",
        "gui_menu_english": "English",
        "gui_menu_chinese": "简体中文",
        "gui_menu_help": "帮助",
        "gui_menu_about": "关于",
    },
    "en": {
        "menu_root": "AEye",
        "menu_toggle_inspect": "Toggle Inspect Mode",
        "menu_show_panel": "Show Edit Panel",
        "menu_export": "Export AI Prompt",
        "menu_switch_language": "切换到中文",
        "panel_title": "AEye Edit Panel",
        "panel_header_title": "AEye",
        "panel_header_subtitle": "Collect modification requests and generate AI-ready task content.",
        "inspect_toggle": "Inspect Mode",
        "inspect_toggle_on": "Inspect: On",
        "inspect_toggle_off": "Inspect: Off",
        "current_target_none": "Current target: none",
        "current_target": "Current target: {selector}",
        "recorded_notes": "Recorded Edit Items",
        "comment_content": "Modification Request",
        "comment_placeholder": "Describe the UI or functional change you want for the selected widget...",
        "btn_add_update": "Add Request ({modifier}+Enter)",
        "btn_remove": "Remove Selected Request",
        "btn_export": "Export AI Prompt",
        "btn_copy": "Copy AI Prompt",
        "msg_enter_comment": "Please enter a modification request first.",
        "msg_select_widget": "Please select a UI widget first.",
        "msg_exported": "Exported to:\n{path}",
        "msg_copied": "The AI prompt has been copied to the clipboard.",
        "dialog_export_title": "Export AEye AI Prompt",
        "dialog_export_filename": "aeye_export.txt",
        "file_filter_text": "Text Files (*.txt)",
        "none": "(none)",
        "export_intro_1": "Each element below includes runtime locator information, source candidates, and the requested modification.",
        "export_intro_2": "Use these details to update the corresponding element precisely and avoid changing unrelated UI. If mapping is ambiguous, prioritize objectName, source candidates, parent chain, window title, and geometry together.",
        "export_empty_1": "There is no actionable modification task yet.",
        "export_empty_2": "Select a widget in inspect mode and add at least one modification request.",
        "export_element": "[Element {index}]",
        "export_locator_block": "Locator Information",
        "export_selector": "Selector",
        "export_class": "Class",
        "export_object_name": "Object Name",
        "export_window_title": "Window Title",
        "export_text": "Text",
        "export_geometry": "Geometry",
        "export_parent_chain": "Parent Chain",
        "export_locator_hint": "Locator Hint",
        "export_source_candidates": "Source Candidates",
        "export_comment": "Modification Request",
        "gui_window_title": "AEye GUI Debug Helper",
        "gui_title": "AEye GUI Debug Helper",
        "gui_select_project": "📁 Select Project Folder",
        "gui_project_placeholder": "Select or enter project folder path...",
        "gui_browse": "Browse",
        "gui_select_directory": "Select Project Folder",
        "gui_project_info": "ℹ️ Project Info",
        "gui_venv_not_detected": "Virtual Env: Not Detected",
        "gui_venv": "Virtual Env: {venv_type}",
        "gui_venv_system": "Virtual Env: Using System Python",
        "gui_select_file": "📄 Select Startup File",
        "gui_python_file": "Python File:",
        "gui_start_args": "⚙️ Startup Args (Optional)",
        "gui_args_placeholder": "e.g., --debug --port 8080",
        "gui_start_debug": "🚀 Start Debug",
        "gui_stop": "🚫 Stop",
        "gui_output_log": "📝 Output Log",
        "gui_warning": "Warning",
        "gui_warning_no_python": "No Python files found in the selected folder",
        "gui_install_failed": "Installation Failed",
        "gui_install_failed_msg": "Failed to automatically install AEye into {venv_type} virtual environment.\n\nPlease run manually in project directory:\npip install -e {aeye_path}",
        "gui_venv_checking": "{venv_type} virtual env detected, checking AEye...",
        "gui_aeye_not_found": "AEye not found in virtual env, installing automatically...",
        "gui_aeye_installed": "AEye successfully installed into {venv_type} virtual env!",
        "gui_aeye_install_failed": "AEye installation failed! Please run manually in this virtual env: pip install -e {aeye_path}",
        "gui_aeye_ready": "AEye is ready in virtual env",
        "gui_start_cmd": "Start command: {cmd}",
        "gui_working_dir": "Working dir: {path}",
        "gui_pythonpath": "PYTHONPATH: {path}",
        "gui_started": "Program started! PID: {pid}",
        "gui_start_failed": "Start failed: {error}",
        "gui_exited": "Program exited, code: {code}",
        "gui_stopping": "Stopping program...",
        "gui_menu_view": "View",
        "gui_menu_language": "Language",
        "gui_menu_english": "English",
        "gui_menu_chinese": "简体中文",
        "gui_menu_help": "Help",
        "gui_menu_about": "About",
    },
}


@dataclass
class I18N:
    language: str = None
    
    def __post_init__(self):
        if self.language is None:
            self.language = _get_system_language()

    def tr(self, key: str, **kwargs: str) -> str:
        template = TRANSLATIONS[self.language][key]
        # 根据系统平台设置快捷键符号
        if sys.platform == 'darwin':
            modifier = '⌘'
        else:
            modifier = 'Ctrl'
        # 合并用户传入的 kwargs 和 modifier
        all_kwargs = {'modifier': modifier, **kwargs}
        return template.format(**all_kwargs)

    def toggle(self) -> None:
        self.language = "en" if self.language == "zh" else "zh"
