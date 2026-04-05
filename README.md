# AEye

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)

### 🎯 Have You Faced These Issues in AI Collaboration?

- **Too abstract with words**: Telling AI "make that button color brighter" and it always misinterprets
- **Inefficient back-and-forth**: Modifying a 1px border takes 10 tries, and AI still gets it wrong
- **Screenshots aren't precise enough**: Multiple UI elements stacked together—even with screenshots, AI can't tell which one you want
- **Hard to align**: You mean "this", AI understands "that"—communication costs are sky-high

### 💡 How AEye Solves These Problems

**AEye** is an AI-oriented runtime UI inspector and debugger for PySide6 applications. It lets you **directly select UI elements with your mouse**—just like using Chrome DevTools or Photoshop—then add modification notes, and finally export structured prompts that AI can understand with pinpoint accuracy.

- ✅ **Precise targeting**: Select UI elements like Photoshop layers, no more guessing with words
- ✅ **Overlap handling**: Right-click to see all overlapping elements at mouse position, never miss anything
- ✅ **AI-friendly**: Export precise descriptions including Selectors, source code locations, and geometry info
- ✅ **Efficient collaboration**: Get AI to understand your intent in one conversation, drastically reducing back-and-forth

[English](README.md) | [简体中文](README_zh-CN.md)

## ✨ Features

- 🚀 **GUI Launcher** - Intuitive graphical interface to launch and debug PySide6 apps
- 🔍 **Inspector Mode** - Hover to highlight, left-click to select, right-click for overlapping elements
- 📝 **Modification Notes** - Record and manage UI modification suggestions
- 🎯 **AI Prompt Export** - Export structured prompts ready for AI collaboration
- 🌐 **Dual Language** - Chinese/English UI and export support
- 🔗 **Source Code Hints** - Lightweight source code location suggestions
- 🖥️ **Live Preview** - Real-time highlighting of selected elements
- 💾 **Auto-save** - Automatic saving of modification notes

## Quick Start

### Option 1: Quick Launch (Recommended)

Simply double-click the appropriate launcher file for your platform:

| Platform | Launcher File |
|----------|---------------|
| **macOS** | `AEye.command` |
| **Windows** | `AEye.bat` |

**macOS first-time authorization:**

1. Right-click the `AEye.command` file
2. Select "Open"
3. Click "Open" in the security prompt

Or add execute permissions via terminal:

```bash
chmod +x AEye.command
```

After that, you can simply double-click to launch! You can also drag the file to your Dock, desktop, or taskbar for convenient access.

### Option 2: Command Line Mode

If you prefer using the command line:

1. **Navigate to project directory**

```bash
cd /path/to/AEye
```

2. **Run the program**

```bash
# First-time or daily use (launch GUI)
python3 -m aeye

# or (if installed)
aeye
aeye gui

# Run example app directly
python3 -m aeye --file example_app/demo.py
```

The GUI interface will open automatically, allowing you to:

- Select your project folder
- Auto-detect Poetry/UV/.venv virtual environments
- Choose your Python entry file
- Launch debugging with one click

3. **Install Dependencies (Optional)**

For full installation:

```bash
pip install -e .
```

For Poetry projects, install AEye in the same virtual environment.

4. **Usage**

- Click `AEye` in the menu bar
- Toggle inspector mode from the panel
- Hover to highlight widgets
- Left-click to select
- Right-click for overlapping elements
- Add modification notes
- Export AI Prompt
- Switch language from menu

## Environment Setup

### Poetry Projects

```bash
cd /path/to/your-project
poetry run python -m pip install -e /path/to/aeye
poetry run python -m aeye --file app.py
```

### With Additional Arguments

```bash
poetry run python -m aeye --file app.py -- --port 8000
```

## AI Prompt Example

```text
Each element includes runtime location info, source code hints, and modification suggestions.
Please modify the corresponding elements based on this information; try not to affect unmentioned parts of the interface. If unable to uniquely locate, prioritize combining objectName, source code candidates, parent chain, window title, and geometry information for comprehensive judgment.

[Element 1]
Location Info:
- Selector: MainWindow[windowTitle="AEye Example App"] > QWidget:nth(0) > QFrame#sidebar > QLabel#nav_prompt_export
- Class: QLabel
- objectName: nav_prompt_export
- Window Title: AEye Example App
- Text: Prompt Export
- Geometry: x=0, y=0, w=120, h=32
- Parent Chain: MainWindow[windowTitle="AEye Example App"] > QWidget:nth(0) > QFrame#sidebar
- Location Hint: Prioritize precise location via objectName='nav_prompt_export'; then verify with class name QLabel and geometry information.
Source Code Candidates:
- example_app/demo.py:73 | objectName match | label.setObjectName(f"nav_{name.lower().replace(' ', '_')}")
Modification Suggestion:
The vertical spacing between this navigation item and the one above is too small, please increase by 6px.
```

## Current Limitations

- Currently only supports **PySide6**
- Focused on `QWidget` / `QMainWindow` system
- macOS compatibility mode for `QtWebEngine` on macOS
- Lightweight source code matching (not full static analysis)
- No property panel, style diff, or auto-screenshot yet
- Selector is runtime path expression (not final stable version)

## Roadmap

- [ ] Support PyQt6 / PySide2 / PyQt5
- [ ] Widget property snapshots (styleSheet, fonts, palette, size policy)
- [ ] Batch and partial screenshots
- [ ] Source file location and code snippet export
- [ ] Enhanced AI Prompt templates

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.

***

