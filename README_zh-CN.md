# AEye / 点睛

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)

### 🎯 你是否也在 AI 协作中遇到过这些问题？

- **语言描述太抽象**：用文字告诉 AI"那个按钮的颜色再亮一点"，AI 总是理解错
- **反复沟通效率低**：修改一个 1px 的边框，来来回回说了 10 次，AI 还是改不对
- **截图也不够精准**：多个 UI 元素堆叠在一起，哪怕有截图，AI 也分不清你要改哪个
- **难以达成一致**：你心里想的是"这里"，AI 理解的是"那里"，沟通成本极高

### 💡 AEye 如何解决这些问题？

**AEye（点睛）** 是一个面向 AI 协作的 PySide6 运行时 UI 调试工具。它让你像使用 Chrome DevTools 或 Photoshop 那样，**用鼠标直接选中你想要修改的 UI 元素**，然后添加修改意见，最后一键导出 AI 能精准理解的结构化 Prompt。

- ✅ **精准定位**：像选 PS 图层一样选中 UI 元素，不再用文字猜
- ✅ **处理重叠**：右键查看鼠标位置所有重叠元素，不再错过
- ✅ **AI 友好**：导出包含 Selector、源码位置、几何信息的精确描述
- ✅ **高效协作**：一次沟通就能让 AI 理解你的意图，大幅减少反复调整

[English](README.md) | [简体中文](README_zh-CN.md)

## ✨ 特性

- 🚀 **GUI 启动器** - 直观的图形界面，用于启动和调试 PySide6 应用
- 🔍 **检查模式** - 悬停高亮、左键选择、右键处理重叠元素
- 📝 **修改意见** - 记录和管理 UI 修改建议
- 🎯 **AI Prompt 导出** - 导出结构化 Prompt，随时可与 AI 协作
- 🌐 **双语支持** - 中文/英文界面和导出内容支持
- 🔗 **源码提示** - 轻量级源码位置建议
- 🖥️ **实时预览** - 选中元素的实时高亮
- 💾 **自动保存** - 修改意见自动保存

## 快速开始

### 方式一：快捷启动（推荐）

直接双击对应平台的启动文件即可：

| 平台 | 启动文件 |
|------|---------|
| **macOS** | `AEye.command` |
| **Windows** | `AEye.bat` |

**macOS 首次使用需要授权：**

1. 右键点击 `AEye.command` 文件
2. 选择"打开"
3. 在弹出的安全提示中点击"打开"

或者在终端中添加执行权限：

```bash
chmod +x AEye.command
```

之后您就可以直接双击启动了！您也可以将该文件拖到 Dock 栏、桌面或任务栏上方便随时启动。

### 方式二：命令行模式

1. **进入项目目录并安装依赖**

```bash
cd /path/to/AEye

# 安装依赖
pip install -r requirements.txt
```

2. **运行程序**

```bash
# 启动 GUI
python3 -m aeye

# 或（如果已安装）
aeye
aeye gui

# 直接运行示例应用
python3 -m aeye --file example_app/demo.py
```

3. **使用说明**

GUI 界面会自动打开，您可以：

- 选择项目文件夹
- 自动检测 Poetry/UV/.venv 虚拟环境
- 选择 Python 入口文件
- 一键启动调试

对于 Poetry 项目，建议将 AEye 安装在同一个虚拟环境中。

4. **使用方式**

- 在菜单栏点击 `AEye`
- 从面板切换检查模式
- 悬停以高亮控件
- 左键选择
- 右键查看重叠元素
- 添加修改意见
- 导出 AI Prompt
- 从菜单切换语言

## 环境设置

### Poetry 项目

```bash
cd /path/to/your-project
poetry run python -m pip install -e /path/to/aeye
poetry run python -m aeye --file app.py
```

### 带额外参数

```bash
poetry run python -m aeye --file app.py -- --port 8000
```

## AI Prompt 示例

```text
下面每个元素都包含运行时定位信息、源码候选和对应的修改意见。
请根据这些信息有针对性地修改对应元素，尽量不要影响未提及的界面部分；如果无法唯一定位，优先结合 objectName、源码候选、父级链路、窗口标题和几何信息综合判断。

[元素 1]
定位信息:
- Selector: MainWindow[windowTitle="AEye Example App"] > QWidget:nth(0) > QFrame#sidebar > QLabel#nav_prompt_export
- 类名: QLabel
- objectName: nav_prompt_export
- 窗口标题: AEye Example App
- 文本: Prompt Export
- 几何信息: x=0, y=0, w=120, h=32
- 父级链路: MainWindow[windowTitle="AEye Example App"] > QWidget:nth(0) > QFrame#sidebar
- 定位提示: 优先通过 objectName='nav_prompt_export' 精准定位；再结合类名 QLabel 与几何信息核对。
源码候选:
- example_app/demo.py:73 | objectName 匹配 | label.setObjectName(f"nav_{name.lower().replace(' ', '_')}")
修改意见:
这个导航项和上方项目的垂直间距太小，请增加 6px。
```

## 当前限制

- 目前仅支持 **PySide6**
- 主要面向 `QWidget` / `QMainWindow` 体系
- macOS 上对 `QtWebEngine` 采用兼容模式
- 轻量级源码匹配（非完整静态分析）
- 尚未提供属性面板、样式对比或自动截图
- Selector 是运行时路径表达式（非最终稳定版）

## 路线图

- [ ] 支持 PyQt6 / PySide2 / PyQt5
- [ ] 控件属性快照（styleSheet、字体、调色板、尺寸策略）
- [ ] 批量截图和局部截图
- [ ] 源码文件定位和代码片段导出
- [ ] 增强的 AI Prompt 模板

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

本项目采用 MIT 许可证。

***

