from __future__ import annotations

from dataclasses import dataclass
import pathlib
import re
from typing import Any
import weakref

from aeye.i18n import I18N

_BOOTSTRAPPED = False
_CONTROLLER = None
_PROJECT_ROOT: pathlib.Path | None = None

try:  # pragma: no cover - import is validated at runtime usage
    from PySide6 import QtCore as _BaseQtCore
except ImportError:  # pragma: no cover
    _BaseQtCore = None


def configure_runtime(project_root: pathlib.Path) -> None:
    global _PROJECT_ROOT
    _PROJECT_ROOT = project_root.resolve()


def bootstrap_runtime() -> None:
    global _BOOTSTRAPPED

    if _BOOTSTRAPPED:
        return

    try:
        from PySide6 import QtWidgets
    except ImportError as exc:  # pragma: no cover - runtime dependency guard
        raise RuntimeError(
            "AEye currently requires PySide6 to be installed in the target environment."
        ) from exc

    _BOOTSTRAPPED = True
    original_init = QtWidgets.QApplication.__init__
    def patched_init(app_self: QtWidgets.QApplication, *args: Any, **kwargs: Any) -> None:
        original_init(app_self, *args, **kwargs)
        _BaseQtCore.QTimer.singleShot(1000, lambda: _ensure_controller(app_self))

    QtWidgets.QApplication.__init__ = patched_init

    existing = QtWidgets.QApplication.instance()
    if existing is not None:
        _BaseQtCore.QTimer.singleShot(1000, lambda: _ensure_controller(existing))


def _ensure_controller(app: Any):
    global _CONTROLLER
    if _CONTROLLER is None:
        _CONTROLLER = InspectorController(app)
    return _CONTROLLER


@dataclass
class CommentEntry:
    selector: str
    class_name: str
    object_name: str
    widget_text: str
    geometry: str
    window_title: str
    parent_chain: str
    locator_hint: str
    source_candidates: list[str]
    instruction: str
    pointer: int
    widget_ref: Any | None = None


class HighlightOverlay:
    def __init__(self, color: str):
        from PySide6 import QtCore, QtGui, QtWidgets

        class _Overlay(QtWidgets.QWidget):
            def __init__(self, pen_color: QtGui.QColor):
                super().__init__()
                self._pen_color = pen_color
                self.setProperty("aeye_internal", True)
                self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
                self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
                self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
                self.hide()

            def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: N802
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
                pen = QtGui.QPen(self._pen_color, 2)
                brush = QtGui.QBrush(
                    QtGui.QColor(
                        self._pen_color.red(),
                        self._pen_color.green(),
                        self._pen_color.blue(),
                        28,
                    )
                )
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        self.widget = _Overlay(QtGui.QColor(color))
        self._QtCore = QtCore
        self.target_widget = None
        self.parent_window = None

    def show_for(self, widget: Any) -> None:
        parent_window = widget.window()
        if parent_window is None:
            return
        if self.parent_window is not parent_window:
            self.widget.setParent(parent_window)
            self.parent_window = parent_window

        rect = widget.rect()
        top_left = widget.mapTo(parent_window, self._QtCore.QPoint(0, 0))
        new_geometry = self._QtCore.QRect(
            top_left.x(),
            top_left.y(),
            rect.width(),
            rect.height(),
        )

        self.target_widget = widget
        if self.widget.geometry() != new_geometry:
            self.widget.setGeometry(new_geometry)
        if not self.widget.isVisible():
            self.widget.show()
        self.widget.raise_()

    def hide(self) -> None:
        self.target_widget = None
        self.widget.hide()

    def is_visible(self) -> bool:
        return self.widget.isVisible()


class NotesPanel:
    def __init__(self, controller: "InspectorController"):
        from PySide6 import QtCore, QtWidgets

        self.controller = controller
        self.widget = QtWidgets.QWidget()
        self.widget.resize(440, 720)
        self.widget.setWindowFlag(QtCore.Qt.Tool, True)
        self.widget.setProperty("aeye_internal", True)
        self.widget.setObjectName("aeyeNotesPanel")

        self.current_selector: str | None = None

        self.header_card = QtWidgets.QFrame()
        self.header_card.setObjectName("headerCard")
        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("titleLabel")
        self.subtitle_label = QtWidgets.QLabel()
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setWordWrap(True)
        self.inspect_toggle = QtWidgets.QPushButton()
        self.inspect_toggle.setObjectName("inspectToggle")
        self.inspect_toggle.setCheckable(True)
        header_top_row = QtWidgets.QHBoxLayout()
        header_top_row.setSpacing(10)
        header_top_row.addWidget(self.title_label)
        header_top_row.addStretch(1)
        header_top_row.addWidget(self.inspect_toggle)
        header_layout = QtWidgets.QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(6)
        header_layout.addLayout(header_top_row)
        header_layout.addWidget(self.subtitle_label)

        self.current_label = QtWidgets.QLabel()
        self.current_label.setWordWrap(True)
        self.current_label.setObjectName("currentTargetLabel")
        self.current_card = QtWidgets.QFrame()
        self.current_card.setObjectName("sectionCard")
        current_layout = QtWidgets.QVBoxLayout(self.current_card)
        current_layout.setContentsMargins(16, 14, 16, 14)
        current_layout.setSpacing(8)
        current_layout.addWidget(self.current_label)

        self.notes_label = QtWidgets.QLabel()
        self.notes_label.setObjectName("sectionLabel")
        self.comment_label = QtWidgets.QLabel()
        self.comment_label.setObjectName("sectionLabel")

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setObjectName("notesList")
        self.editor = QtWidgets.QTextEdit()
        self.editor.setObjectName("instructionEditor")

        self.add_button = QtWidgets.QPushButton()
        self.remove_button = QtWidgets.QPushButton()
        self.export_button = QtWidgets.QPushButton()
        self.copy_button = QtWidgets.QPushButton()
        for button, name in (
            (self.add_button, "primaryButton"),
            (self.remove_button, "ghostButton"),
            (self.export_button, "ghostButton"),
            (self.copy_button, "primaryButton"),
        ):
            button.setProperty("variant", name)

        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.remove_button)
        button_row.addWidget(self.export_button)
        button_row.addWidget(self.copy_button)

        self.list_card = QtWidgets.QFrame()
        self.list_card.setObjectName("sectionCard")
        list_layout = QtWidgets.QVBoxLayout(self.list_card)
        list_layout.setContentsMargins(16, 14, 16, 16)
        list_layout.setSpacing(10)
        list_layout.addWidget(self.notes_label)
        list_layout.addWidget(self.list_widget, 1)

        self.editor_card = QtWidgets.QFrame()
        self.editor_card.setObjectName("sectionCard")
        editor_layout = QtWidgets.QVBoxLayout(self.editor_card)
        editor_layout.setContentsMargins(16, 14, 16, 16)
        editor_layout.setSpacing(10)
        editor_layout.addWidget(self.comment_label)
        editor_layout.addWidget(self.editor, 1)
        editor_layout.addLayout(button_row)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.setObjectName("panelSplitter")
        self.splitter.addWidget(self.list_card)
        self.splitter.addWidget(self.editor_card)
        self.splitter.setSizes([280, 320])

        layout = QtWidgets.QVBoxLayout(self.widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        layout.addWidget(self.header_card)
        layout.addWidget(self.current_card)
        layout.addWidget(self.splitter, 1)

        self.add_button.clicked.connect(self.save_current_note)
        self.remove_button.clicked.connect(self.remove_selected_note)
        self.export_button.clicked.connect(self.export_notes)
        self.copy_button.clicked.connect(self.copy_export_text)
        self.list_widget.currentRowChanged.connect(self.load_selected_note)
        self.inspect_toggle.toggled.connect(self.controller.set_inspect_mode)
        self.editor.textChanged.connect(self._on_editor_text_changed)
        
        # 添加快捷键支持: Command/Ctrl + Enter
        from PySide6 import QtGui
        self._add_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self.editor)
        self._add_shortcut.activated.connect(lambda: self.save_current_note())
        self._add_shortcut_mac = QtGui.QShortcut(QtGui.QKeySequence("Meta+Return"), self.editor)
        self._add_shortcut_mac.activated.connect(lambda: self.save_current_note())

        self._suspend_editor_events = False
        self.auto_save_timer = QtCore.QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.setInterval(450)
        self.auto_save_timer.timeout.connect(self._auto_save_current_note)

        self._apply_styles()
        self.update_texts()

    def _apply_styles(self) -> None:
        self.widget.setStyleSheet(
            """
            QWidget#aeyeNotesPanel {
                background: #f5f7fb;
            }
            QFrame#headerCard, QFrame#sectionCard {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            QLabel#titleLabel {
                color: #0f172a;
                font-size: 22px;
                font-weight: 700;
            }
            QLabel#subtitleLabel {
                color: #475569;
                font-size: 12px;
                line-height: 1.4em;
            }
            QLabel#sectionLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.02em;
            }
            QLabel#currentTargetLabel {
                color: #0f172a;
                font-size: 13px;
                font-weight: 600;
            }
            QListWidget#notesList, QTextEdit#instructionEditor {
                background: #fbfdff;
                border: 1px solid #dbe3ef;
                border-radius: 12px;
                padding: 8px;
                color: #0f172a;
                selection-background-color: #dbeafe;
            }
            QListWidget#notesList::item {
                border-radius: 8px;
                padding: 8px 10px;
                margin: 2px 0;
            }
            QListWidget#notesList::item:selected {
                background: #dbeafe;
                color: #0f172a;
            }
            QTextEdit#instructionEditor {
                padding: 10px 12px;
            }
            QPushButton {
                min-height: 38px;
                border-radius: 10px;
                padding: 0 14px;
                font-weight: 600;
            }
            QPushButton#inspectToggle {
                min-width: 120px;
                background: #e2e8f0;
                color: #0f172a;
                border: 1px solid #cbd5e1;
            }
            QPushButton#inspectToggle:checked {
                background: #2563eb;
                color: #ffffff;
                border: 1px solid #1d4ed8;
            }
            QPushButton[variant="primaryButton"] {
                background: #2563eb;
                color: #ffffff;
                border: 1px solid #1d4ed8;
            }
            QPushButton[variant="primaryButton"]:hover {
                background: #1d4ed8;
            }
            QPushButton[variant="ghostButton"] {
                background: #ffffff;
                color: #1e293b;
                border: 1px solid #cbd5e1;
            }
            QPushButton[variant="ghostButton"]:hover {
                background: #f8fafc;
            }
            QSplitter::handle {
                background: transparent;
                height: 8px;
            }
            """
        )

    def update_texts(self) -> None:
        self.widget.setWindowTitle(self.controller.tr("panel_title"))
        self.title_label.setText(self.controller.tr("panel_header_title"))
        self.subtitle_label.setText(self.controller.tr("panel_header_subtitle"))
        self.notes_label.setText(self.controller.tr("recorded_notes"))
        self.comment_label.setText(self.controller.tr("comment_content"))
        self.editor.setPlaceholderText(self.controller.tr("comment_placeholder"))
        self.add_button.setText(self.controller.tr("btn_add_update"))
        self.remove_button.setText(self.controller.tr("btn_remove"))
        self.export_button.setText(self.controller.tr("btn_export"))
        self.copy_button.setText(self.controller.tr("btn_copy"))
        self.update_current_target(self.current_selector)
        self.refresh_note_list()
        self.sync_state()

    def show(self) -> None:
        self.controller.position_notes_panel()
        self.widget.show()
        self.widget.raise_()

    def update_current_target(self, selector: str | None) -> None:
        self.current_selector = selector
        if selector:
            self.current_label.setText(self.controller.tr("current_target", selector=selector))
        else:
            self.current_label.setText(self.controller.tr("current_target_none"))

    def refresh_note_list(self) -> None:
        selected_selector = None
        current_row = self.list_widget.currentRow()
        if 0 <= current_row < len(self.controller.notes):
            selected_selector = self.controller.notes[current_row].selector
        self.list_widget.clear()
        selected_row = -1
        for row, note in enumerate(self.controller.notes):
            title = note.selector
            if note.instruction:
                title = f"{title} | {note.instruction.splitlines()[0][:28]}"
            self.list_widget.addItem(title)
            if note.selector == selected_selector:
                selected_row = row
        if selected_row >= 0:
            self.list_widget.setCurrentRow(selected_row)

    def load_selected_note(self, row: int) -> None:
        if row < 0 or row >= len(self.controller.notes):
            return
        note = self.controller.notes[row]
        self._suspend_editor_events = True
        self.editor.setPlainText(note.instruction)
        self._suspend_editor_events = False
        self.update_current_target(note.selector)
        widget = self.controller.resolve_note_widget(note)
        if widget is not None:
            self.controller.select_widget(widget, show_panel=False)

    def save_current_note(self, silent: bool = False) -> None:
        from PySide6 import QtWidgets

        comment = self.editor.toPlainText().strip()
        if not comment:
            if not silent:
                QtWidgets.QMessageBox.information(
                    self.widget, "AEye", self.controller.tr("msg_enter_comment")
                )
            return
        if self.controller.current_widget is None:
            if not silent:
                QtWidgets.QMessageBox.information(
                    self.widget, "AEye", self.controller.tr("msg_select_widget")
                )
            return

        target_row = self.controller.upsert_note(self.controller.current_widget, comment)
        self.refresh_note_list()
        if target_row >= 0:
            self.list_widget.setCurrentRow(target_row)

    def remove_selected_note(self) -> None:
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.controller.notes):
            return
        del self.controller.notes[row]
        self.editor.clear()
        self.refresh_note_list()
        self.update_current_target(
            self.controller.build_selector(self.controller.current_widget)
            if self.controller.current_widget is not None
            else None
        )

    def export_notes(self) -> None:
        from PySide6 import QtWidgets

        text = self.controller.export_text()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.widget,
            self.controller.tr("dialog_export_title"),
            self.controller.tr("dialog_export_filename"),
            self.controller.tr("file_filter_text"),
        )
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write(text)
        QtWidgets.QMessageBox.information(
            self.widget, "AEye", self.controller.tr("msg_exported", path=file_path)
        )

    def copy_export_text(self) -> None:
        from PySide6 import QtWidgets

        text = self.controller.export_text()
        QtWidgets.QApplication.clipboard().setText(text)
        QtWidgets.QMessageBox.information(
            self.widget, "AEye", self.controller.tr("msg_copied")
        )

    def _on_editor_text_changed(self) -> None:
        if self._suspend_editor_events:
            return
        self.auto_save_timer.start()

    def _auto_save_current_note(self) -> None:
        from PySide6 import QtGui
        
        comment = self.editor.toPlainText().strip()
        if not comment:
            return
        if self.controller.current_widget is None:
            return
            
        selector = self.controller.build_selector(self.controller.current_widget)
        
        # 检查该 selector 是否已存在于已记录修改项中
        found_index = -1
        for index, note in enumerate(self.controller.notes):
            if note.selector == selector:
                found_index = index
                break
        
        if found_index == -1:
            # 新的 UI 元素，不自动保存
            return
            
        # 保存光标位置
        cursor = self.editor.textCursor()
        cursor_position = cursor.position()
        
        # 更新已存在的记录
        self.controller.upsert_note(self.controller.current_widget, comment)
        self.refresh_note_list()
        if found_index >= 0:
            self.list_widget.setCurrentRow(found_index)
        
        # 恢复光标位置
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor_position)
        self.editor.setTextCursor(cursor)

    def sync_state(self) -> None:
        enabled = self.controller.inspect_mode
        self.inspect_toggle.blockSignals(True)
        self.inspect_toggle.setChecked(enabled)
        self.inspect_toggle.blockSignals(False)
        self.inspect_toggle.setText(
            self.controller.tr("inspect_toggle_on") if enabled else self.controller.tr("inspect_toggle_off")
        )


class InspectorController(_BaseQtCore.QObject if _BaseQtCore else object):
    def __init__(self, app: Any):
        from PySide6 import QtCore, QtGui, QtWidgets

        super().__init__()

        self.QtCore = QtCore
        self.QtGui = QtGui
        self.QtWidgets = QtWidgets
        self.app = app
        self.i18n = I18N(language="zh")
        self.inspect_mode = False
        self.current_widget = None
        self.hovered_widget = None
        self.notes: list[CommentEntry] = []
        self._known_windows: set[int] = set()
        self._menu_entries: list[dict[str, Any]] = []
        self._active_candidate_menu = None
        self._anchor_window = None
        self._panel_initialized = False
        self._menu_preview_widget = None
        self._last_mouse_buttons = QtCore.Qt.MouseButton.NoButton

        self.hover_overlay: HighlightOverlay | None = None
        self.selection_overlay: HighlightOverlay | None = None
        self.notes_panel: NotesPanel | None = None

        self.app.aboutToQuit.connect(self._cleanup)

        self.scan_timer = QtCore.QTimer()
        self.scan_timer.setInterval(80)
        self.scan_timer.timeout.connect(self._tick)
        self.scan_timer.start()

        QtCore.QTimer.singleShot(0, self._attach_menus)

    def tr(self, key: str, **kwargs: str) -> str:
        return self.i18n.tr(key, **kwargs)

    def toggle_language(self) -> None:
        self.i18n.toggle()
        self._update_menu_texts()
        if self.notes_panel is not None:
            self.notes_panel.update_texts()

    def _get_hover_overlay(self) -> HighlightOverlay:
        if self.hover_overlay is None:
            self.hover_overlay = HighlightOverlay("#00C2FF")
        return self.hover_overlay

    def _get_selection_overlay(self) -> HighlightOverlay:
        if self.selection_overlay is None:
            self.selection_overlay = HighlightOverlay("#FF9D00")
        return self.selection_overlay

    def _get_notes_panel(self) -> NotesPanel:
        if self.notes_panel is None:
            self.notes_panel = NotesPanel(self)
        return self.notes_panel

    def _cleanup(self) -> None:
        if self.hover_overlay is not None:
            self.hover_overlay.hide()
        if self.selection_overlay is not None:
            self.selection_overlay.hide()

    def _tick(self) -> None:
        self._attach_menus()
        if not self.inspect_mode:
            if self.hover_overlay is not None:
                self.hover_overlay.hide()
            self._last_mouse_buttons = self.QtGui.QGuiApplication.mouseButtons()
            return
        if self._active_candidate_menu is not None:
            if self._menu_preview_widget is not None:
                self._get_hover_overlay().show_for(self._menu_preview_widget)
            self._last_mouse_buttons = self.QtGui.QGuiApplication.mouseButtons()
            return

        cursor_pos = self.QtGui.QCursor.pos()
        widget = self._widget_at_global_pos(cursor_pos)
        if widget is None:
            self.hovered_widget = None
            if self.hover_overlay is not None:
                self.hover_overlay.hide()
        else:
            if widget is not self.hovered_widget:
                self.hovered_widget = widget
                self._get_hover_overlay().show_for(widget)

        buttons = self.QtGui.QGuiApplication.mouseButtons()
        left_pressed = bool(buttons & self.QtCore.Qt.LeftButton)
        left_was_pressed = bool(self._last_mouse_buttons & self.QtCore.Qt.LeftButton)
        right_pressed = bool(buttons & self.QtCore.Qt.RightButton)
        right_was_pressed = bool(self._last_mouse_buttons & self.QtCore.Qt.RightButton)

        if widget is not None and left_pressed and not left_was_pressed:
            self._close_candidate_menu()
            self.select_widget(widget)
        elif widget is not None and right_pressed and not right_was_pressed:
            self._show_candidate_menu(widget, cursor_pos)

        self._last_mouse_buttons = buttons

    def _attach_menus(self) -> None:
        for widget in self.app.topLevelWidgets():
            if not isinstance(widget, self.QtWidgets.QMainWindow):
                continue
            pointer = int(widget.winId())
            if pointer in self._known_windows:
                continue
            self._known_windows.add(pointer)
            self._install_menu(widget)
            widget.installEventFilter(self)
            if self._anchor_window is None:
                self._anchor_window = widget
            if not self._panel_initialized:
                self._panel_initialized = True
                self.QtCore.QTimer.singleShot(180, self._show_notes_panel_initially)

    def _install_menu(self, window: Any) -> None:
        menu = window.menuBar().addMenu("")

        toggle_action = menu.addAction("")
        toggle_action.setCheckable(True)
        toggle_action.triggered.connect(self.set_inspect_mode)

        panel_action = menu.addAction("")
        panel_action.triggered.connect(lambda: self._get_notes_panel().show())

        export_action = menu.addAction("")
        export_action.triggered.connect(lambda: self._get_notes_panel().export_notes())

        language_action = menu.addAction("")
        language_action.triggered.connect(self.toggle_language)

        self._menu_entries.append(
            {
                "menu": menu,
                "toggle": toggle_action,
                "panel": panel_action,
                "export": export_action,
                "language": language_action,
            }
        )
        self._update_menu_texts()

    def _update_menu_texts(self) -> None:
        for entry in self._menu_entries:
            entry["menu"].setTitle(self.tr("menu_root"))
            entry["toggle"].setText(self.tr("menu_toggle_inspect"))
            entry["toggle"].setChecked(self.inspect_mode)
            entry["panel"].setText(self.tr("menu_show_panel"))
            entry["export"].setText(self.tr("menu_export"))
            entry["language"].setText(self.tr("menu_switch_language"))
        if self.notes_panel is not None:
            self.notes_panel.sync_state()

    def _show_notes_panel_initially(self) -> None:
        if self._anchor_window is None or not self._anchor_window.isVisible():
            self.QtCore.QTimer.singleShot(120, self._show_notes_panel_initially)
            return
        self._get_notes_panel()
        self.position_notes_panel()
        if self.notes_panel is not None:
            self.notes_panel.widget.show()

    def position_notes_panel(self) -> None:
        window = self._anchor_window
        if window is None or not window.isVisible() or self.notes_panel is None:
            return
        gap = 18
        frame = window.frameGeometry()
        panel = self.notes_panel.widget
        panel_width = panel.width()
        panel_height = max(frame.height(), 560)
        panel.resize(panel_width, panel_height)

        screen = window.screen() or self.QtGui.QGuiApplication.screenAt(frame.center())
        available = screen.availableGeometry() if screen is not None else frame.adjusted(-1000, -1000, 1000, 1000)

        x = frame.right() + gap
        if x + panel_width > available.right():
            x = max(available.left() + gap, frame.left() - panel_width - gap)
        y = max(available.top() + gap, min(frame.top(), available.bottom() - panel_height - gap))
        panel.move(x, y)

    def set_inspect_mode(self, enabled: bool) -> None:
        self.inspect_mode = enabled
        self._update_menu_texts()
        if not enabled:
            self._close_candidate_menu()
            if self.hover_overlay is not None:
                self.hover_overlay.hide()
            if self.selection_overlay is not None:
                self.selection_overlay.hide()
        elif self.current_widget is not None:
            self._get_selection_overlay().show_for(self.current_widget)

    def eventFilter(self, obj: Any, event: Any) -> bool:  # noqa: N802
        event_type = event.type()
        if event_type == self.QtCore.QEvent.ApplicationDeactivate:
            if self.hover_overlay is not None:
                self.hover_overlay.hide()
            self._close_candidate_menu()
            return False
        if obj is self._anchor_window and event_type in (
            self.QtCore.QEvent.Move,
            self.QtCore.QEvent.Resize,
            self.QtCore.QEvent.Show,
            self.QtCore.QEvent.WindowStateChange,
        ):
            self.QtCore.QTimer.singleShot(0, self.position_notes_panel)
            return False
        if event_type == self.QtCore.QEvent.MouseButtonPress and self.inspect_mode:
            global_pos = self._event_global_pos(event)
            widget = self._widget_at_global_pos(global_pos)
            if widget is None:
                return False
            button = event.button()
            if button == self.QtCore.Qt.LeftButton:
                self._close_candidate_menu()
                self.select_widget(widget)
                return True
            if button == self.QtCore.Qt.RightButton:
                self._show_candidate_menu(widget, global_pos)
                return True
        return False

    def _event_global_pos(self, event: Any):
        if hasattr(event, "globalPosition"):
            return event.globalPosition().toPoint()
        return event.globalPos()

    def _widget_at_global_pos(self, pos: Any) -> Any:
        top_level = self.app.topLevelAt(pos)
        top_level = self._normalize_widget(top_level)
        if top_level is None:
            top_level = self._find_top_level_at(pos)
        if top_level is None:
            return None
        return self._deepest_widget_at(top_level, pos)

    def _find_top_level_at(self, pos: Any) -> Any:
        for widget in reversed(self.app.topLevelWidgets()):
            if not isinstance(widget, self.QtWidgets.QWidget):
                continue
            if self._is_internal_widget(widget) or not widget.isVisible():
                continue
            local_pos = widget.mapFromGlobal(pos)
            if widget.rect().contains(local_pos):
                return widget
        return None

    def _deepest_widget_at(self, widget: Any, global_pos: Any) -> Any:
        local_pos = widget.mapFromGlobal(global_pos)
        children = [
            child
            for child in widget.children()
            if isinstance(child, self.QtWidgets.QWidget)
            and child.isVisible()
            and not self._is_internal_widget(child)
        ]

        for child in reversed(children):
            child_local_pos = child.mapFromGlobal(global_pos)
            if not child.rect().contains(child_local_pos):
                continue
            descendant = self._deepest_widget_at(child, global_pos)
            if descendant is not None:
                return descendant

        return self._normalize_widget(widget)

    def _normalize_widget(self, widget: Any) -> Any:
        while widget is not None:
            if self._is_internal_widget(widget):
                widget = widget.parentWidget()
                continue
            if not widget.isVisible():
                widget = widget.parentWidget()
                continue
            return widget
        return None

    def _is_internal_widget(self, widget: Any) -> bool:
        current = widget
        while current is not None:
            if current.property("aeye_internal"):
                return True
            current = current.parentWidget()
        return False

    def _show_candidate_menu(self, widget: Any, global_pos: Any) -> None:
        self._close_candidate_menu()
        menu = self.QtWidgets.QMenu()
        menu.setProperty("aeye_internal", True)

        for candidate in self._widget_candidates(widget):
            action = menu.addAction(self.describe_widget(candidate))
            action.triggered.connect(lambda checked=False, w=candidate: self.select_widget(w))
            action.hovered.connect(lambda w=candidate: self.preview_widget(w))

        menu.aboutToHide.connect(self._on_candidate_menu_hidden)
        self._active_candidate_menu = menu
        self._menu_preview_widget = widget
        self.preview_widget(widget)
        menu.popup(global_pos)

    def _close_candidate_menu(self) -> None:
        menu = self._active_candidate_menu
        if menu is None:
            return
        self._active_candidate_menu = None
        self._menu_preview_widget = None
        menu.close()
        menu.deleteLater()

    def _on_candidate_menu_hidden(self) -> None:
        menu = self.sender()
        if menu is self._active_candidate_menu:
            self._active_candidate_menu.deleteLater()
            self._active_candidate_menu = None
        self._menu_preview_widget = None

    def _widget_candidates(self, widget: Any) -> list[Any]:
        candidates = []
        current = widget
        seen: set[int] = set()
        while current is not None:
            pointer = id(current)
            if pointer not in seen and not self._is_internal_widget(current):
                candidates.append(current)
                seen.add(pointer)
            current = current.parentWidget()
        return candidates

    def select_widget(self, widget: Any, show_panel: bool = True) -> None:
        widget = self._normalize_widget(widget)
        if widget is None:
            return
        if isinstance(widget.window(), self.QtWidgets.QMainWindow):
            self._anchor_window = widget.window()
        self.current_widget = widget
        self._get_selection_overlay().show_for(widget)
        selector = self.build_selector(widget)
        panel = self.notes_panel if not show_panel else self._get_notes_panel()
        if panel is not None:
            panel.update_current_target(selector)
        
        # 检查该组件是否已在已记录修改项中，如果是则自动加载，否则清空编辑器
        found = False
        if panel is not None:
            for index, note in enumerate(self.notes):
                if note.selector == selector:
                    panel.list_widget.setCurrentRow(index)
                    found = True
                    break
        
        if panel is not None and not found:
            # 新的 UI 元素，清空编辑器和列表选中状态
            panel._suspend_editor_events = True
            panel.editor.clear()
            panel._suspend_editor_events = False
            panel.list_widget.setCurrentRow(-1)
        
        if show_panel and panel is not None:
            panel.show()
            self.position_notes_panel()

    def preview_widget(self, widget: Any) -> None:
        widget = self._normalize_widget(widget)
        if widget is None:
            return
        self._menu_preview_widget = widget
        if self.inspect_mode:
            self._get_hover_overlay().show_for(widget)

    def upsert_note(self, widget: Any, instruction: str) -> int:
        selector = self.build_selector(widget)
        entry = CommentEntry(
            selector=selector,
            class_name=widget.metaObject().className(),
            object_name=widget.objectName() or "",
            widget_text=self.extract_widget_text(widget),
            geometry=self.geometry_to_string(widget),
            window_title=widget.window().windowTitle() if widget.window() else "",
            parent_chain=self.build_parent_chain(widget),
            locator_hint=self.build_locator_hint(widget),
            source_candidates=self.find_source_candidates(widget),
            instruction=instruction,
            pointer=id(widget),
            widget_ref=weakref.ref(widget),
        )

        for index, note in enumerate(self.notes):
            if note.selector == selector:
                self.notes[index] = entry
                return index
        self.notes.append(entry)
        return len(self.notes) - 1

    def resolve_note_widget(self, note: CommentEntry) -> Any:
        widget = note.widget_ref() if callable(note.widget_ref) else None
        widget = self._normalize_widget(widget)
        if widget is not None:
            return widget

        if note.object_name:
            for candidate in self.app.allWidgets():
                if not isinstance(candidate, self.QtWidgets.QWidget):
                    continue
                if candidate.objectName() != note.object_name:
                    continue
                if note.window_title and candidate.window().windowTitle() != note.window_title:
                    continue
                return candidate

        return self._find_widget_by_selector(note.selector, note.window_title)

    def _find_widget_by_selector(self, selector: str, window_title: str) -> Any:
        for candidate in self.app.allWidgets():
            if not isinstance(candidate, self.QtWidgets.QWidget):
                continue
            if window_title and candidate.window().windowTitle() != window_title:
                continue
            if self.build_selector(candidate) == selector:
                return candidate
        return None

    def export_text(self) -> str:
        if not self.notes:
            return (
                f"{self.tr('export_empty_1')}\n"
                f"{self.tr('export_empty_2')}\n"
            )

        none_text = self.tr("none")
        lines = [
            self.tr("export_intro_1"),
            self.tr("export_intro_2"),
            "",
        ]

        for index, note in enumerate(self.notes, start=1):
            lines.extend(
                [
                    self.tr("export_element", index=str(index)),
                    f"{self.tr('export_locator_block')}:",
                    f"- {self.tr('export_selector')}: {note.selector}",
                    f"- {self.tr('export_class')}: {note.class_name}",
                    f"- {self.tr('export_object_name')}: {note.object_name or none_text}",
                    f"- {self.tr('export_window_title')}: {note.window_title or none_text}",
                    f"- {self.tr('export_text')}: {note.widget_text or none_text}",
                    f"- {self.tr('export_geometry')}: {note.geometry}",
                    f"- {self.tr('export_parent_chain')}: {note.parent_chain}",
                    f"- {self.tr('export_locator_hint')}: {note.locator_hint}",
                    f"{self.tr('export_source_candidates')}:",
                    *(
                        [f"- {candidate}" for candidate in note.source_candidates]
                        if note.source_candidates
                        else [f"- {none_text}"]
                    ),
                    f"{self.tr('export_comment')}:",
                    note.instruction,
                    "",
                ]
            )
        return "\n".join(lines).strip() + "\n"

    def describe_widget(self, widget: Any) -> str:
        class_name = widget.metaObject().className()
        object_name = widget.objectName()
        text = self.extract_widget_text(widget)
        parts = [class_name]
        if object_name:
            parts.append(f"#{object_name}")
        if text:
            parts.append(f'"{self._quote(text[:24])}"')
        return " ".join(parts)

    def extract_widget_text(self, widget: Any) -> str:
        for attr_name in ("text", "title", "windowTitle", "placeholderText", "toolTip"):
            attr = getattr(widget, attr_name, None)
            if callable(attr):
                try:
                    value = attr()
                except TypeError:
                    continue
                if isinstance(value, str) and value.strip():
                    return value.strip().replace("\n", " ")
        return ""

    def geometry_to_string(self, widget: Any) -> str:
        rect = widget.geometry()
        return f"x={rect.x()}, y={rect.y()}, w={rect.width()}, h={rect.height()}"

    def build_parent_chain(self, widget: Any) -> str:
        parts = []
        current = widget.parentWidget()
        while current is not None:
            parts.append(self._widget_label(current))
            current = current.parentWidget()
        return " > ".join(reversed(parts)) if parts else self.tr("none")

    def build_locator_hint(self, widget: Any) -> str:
        object_name = widget.objectName()
        text = self.extract_widget_text(widget)
        class_name = widget.metaObject().className()
        if self.i18n.language == "zh":
            if object_name:
                return f"优先通过 objectName='{object_name}' 精准定位；再结合类名 {class_name} 与几何信息核对。"
            if text:
                return f"该控件没有 objectName，可结合文本 '{text[:24]}'、类名 {class_name}、父级链路与几何信息定位。"
            return f"该控件没有稳定文本或 objectName，建议结合类名 {class_name}、父级链路和几何信息定位。"
        if object_name:
            return f"Prefer objectName='{object_name}' for precise lookup, then verify with class {class_name} and geometry."
        if text:
            return f"No objectName is available. Use text '{text[:24]}', class {class_name}, parent chain, and geometry together."
        return f"No stable objectName or text is available. Use class {class_name}, parent chain, and geometry together."

    def build_selector(self, widget: Any) -> str:
        parts = []
        current = widget
        while current is not None:
            parts.append(self._selector_segment(current))
            current = current.parentWidget()
        return " > ".join(reversed(parts))

    def _selector_segment(self, widget: Any) -> str:
        class_name = widget.metaObject().className()
        object_name = widget.objectName()
        text = self.extract_widget_text(widget)
        sibling_index = self._sibling_index(widget)

        segment = class_name
        if widget.parentWidget() is None:
            window_title = widget.windowTitle() if hasattr(widget, "windowTitle") else ""
            if object_name:
                return f"{segment}#{object_name}"
            if window_title:
                return f'{segment}[windowTitle="{self._quote(window_title[:36])}"]'
            return f"{segment}:nth({sibling_index})"

        if object_name:
            segment += f"#{object_name}"
        elif text:
            segment += f'[text="{self._quote(text[:24])}"]:nth({sibling_index})'
        else:
            segment += f":nth({sibling_index})"
        return segment

    def _widget_label(self, widget: Any) -> str:
        class_name = widget.metaObject().className()
        object_name = widget.objectName()
        if object_name:
            return f"{class_name}#{object_name}"
        text = self.extract_widget_text(widget)
        if text:
            return f'{class_name}[text="{self._quote(text[:24])}"]'
        return f"{class_name}:nth({self._sibling_index(widget)})"

    def _quote(self, text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"')

    def find_source_candidates(self, widget: Any) -> list[str]:
        if _PROJECT_ROOT is None or not _PROJECT_ROOT.exists():
            return []

        object_name = widget.objectName().strip()
        widget_text = self.extract_widget_text(widget).strip()
        class_name = widget.metaObject().className().strip()
        if not any((object_name, widget_text, class_name)):
            return []

        candidates: dict[tuple[str, int, str], tuple[int, str]] = {}
        py_files = sorted(_PROJECT_ROOT.rglob("*.py"))
        for file_path in py_files:
            if "__pycache__" in file_path.parts:
                continue
            try:
                lines = file_path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            relative = str(file_path.relative_to(_PROJECT_ROOT))
            for index, line in enumerate(lines):
                line_number = index + 1
                stripped = line.strip()
                if not stripped:
                    continue

                if object_name:
                    if re.search(rf"setObjectName\(\s*[\"']{re.escape(object_name)}[\"']\s*\)", line):
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            140,
                            "setObjectName 精确匹配",
                            self._candidate_snippet(lines, index),
                        )
                    if f"#{object_name}" in line:
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            120,
                            "样式选择器匹配",
                            self._candidate_snippet(lines, index),
                        )
                    elif object_name in line:
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            85,
                            "objectName 文本匹配",
                            self._candidate_snippet(lines, index),
                        )

                if widget_text:
                    escaped_text = re.escape(widget_text)
                    if re.search(
                        rf"set(Text|Title|WindowTitle|PlaceholderText)\(\s*[\"']{escaped_text}[\"']\s*\)",
                        line,
                    ):
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            125,
                            "文本设置精确匹配",
                            self._candidate_snippet(lines, index),
                        )
                    elif re.search(rf"\(\s*[\"']{escaped_text}[\"']\s*\)", line):
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            100,
                            "构造文本匹配",
                            self._candidate_snippet(lines, index),
                        )
                    elif widget_text in line:
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            70,
                            "文本包含匹配",
                            self._candidate_snippet(lines, index),
                        )

                if class_name:
                    if not class_name.startswith("Q") and re.search(
                        rf"^class\s+{re.escape(class_name)}\b", stripped
                    ):
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            130,
                            "自定义类定义匹配",
                            self._candidate_snippet(lines, index),
                        )
                    if re.search(rf"\b{re.escape(class_name)}\s*\(", line):
                        score = 110 if not class_name.startswith("Q") else 78
                        reason = "控件实例化匹配" if not class_name.startswith("Q") else "Qt 控件类型匹配"
                        self._add_source_candidate(
                            candidates,
                            relative,
                            line_number,
                            score,
                            reason,
                            self._candidate_snippet(lines, index),
                        )

        ranked = sorted(
            candidates.values(),
            key=lambda item: (-item[0], item[1]),
        )
        return [text for _, text in ranked[:8]]

    def _add_source_candidate(
        self,
        candidates: dict[tuple[str, int, str], tuple[int, str]],
        relative_path: str,
        line_number: int,
        score: int,
        reason: str,
        snippet: str,
    ) -> None:
        key = (relative_path, line_number, reason)
        text = f"{relative_path}:{line_number} | {reason} | {snippet[:180]}"
        current = candidates.get(key)
        if current is None or score > current[0]:
            candidates[key] = (score, text)

    def _candidate_snippet(self, lines: list[str], index: int) -> str:
        current = lines[index].strip()
        if "setObjectName" in current:
            for offset in range(1, 4):
                prev_index = index - offset
                if prev_index < 0:
                    break
                previous = lines[prev_index].strip()
                if previous and "(" in previous:
                    return f"{previous} || {current}"
        return current

    def _sibling_index(self, widget: Any) -> int:
        parent = widget.parentWidget()
        if parent is None:
            return 0
        siblings = [
            child
            for child in parent.children()
            if isinstance(child, self.QtWidgets.QWidget) and not self._is_internal_widget(child)
        ]
        matches = [
            child for child in siblings if child.metaObject().className() == widget.metaObject().className()
        ]
        for index, sibling in enumerate(matches):
            if sibling is widget:
                return index
        return 0
