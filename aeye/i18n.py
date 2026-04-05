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
