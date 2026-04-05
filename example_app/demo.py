from PySide6 import QtCore, QtWidgets


class OverlayCard(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overlayCard")
        self.setStyleSheet(
            """
            QFrame#overlayCard {
                background: rgba(255, 255, 255, 220);
                border: 1px solid #d7dce4;
                border-radius: 14px;
            }
            """
        )

        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("AEye Demo Panel")
        title.setObjectName("panelTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        subtitle = QtWidgets.QLabel("用于测试悬停高亮、重叠组件选择和评论导出。")
        subtitle.setWordWrap(True)
        action = QtWidgets.QPushButton("立即同步")
        action.setObjectName("syncButton")
        action.setStyleSheet(
            """
            QPushButton#syncButton {
                padding: 8px 14px;
                background: #276ef1;
                color: white;
                border: 1px solid #1956c8;
                border-radius: 8px;
            }
            """
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        layout.addWidget(action, alignment=QtCore.Qt.AlignLeft)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AEye Example App")
        self.resize(980, 680)

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)

        grid = QtWidgets.QGridLayout(root)
        grid.setContentsMargins(24, 24, 24, 24)
        grid.setSpacing(18)

        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(
            """
            QFrame#sidebar {
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
            }
            QLabel {
                color: white;
            }
            """
        )
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_title = QtWidgets.QLabel("Project")
        sidebar_title.setObjectName("sidebarTitle")
        sidebar_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        sidebar_layout.addWidget(sidebar_title)
        for name in ["Dashboard", "Inspect", "Prompt Export", "Settings"]:
            label = QtWidgets.QLabel(name)
            label.setObjectName(f"nav_{name.lower().replace(' ', '_')}")
            label.setStyleSheet("padding: 8px 10px; border: 1px solid rgba(255,255,255,0.06);")
            sidebar_layout.addWidget(label)
        sidebar_layout.addStretch(1)

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        header = QtWidgets.QFrame()
        header.setObjectName("header")
        header.setStyleSheet(
            """
            QFrame#header {
                background: #ffffff;
                border: 1px solid #d8dde6;
                border-radius: 12px;
            }
            """
        )
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_title = QtWidgets.QLabel("Prompt-ready UI review")
        header_title.setObjectName("headerTitle")
        header_title.setStyleSheet("font-size: 20px; font-weight: 700;")
        search = QtWidgets.QLineEdit()
        search.setObjectName("searchBox")
        search.setPlaceholderText("Search widgets...")
        search.setStyleSheet(
            """
            QLineEdit#searchBox {
                padding: 8px 12px;
                border: 1px solid #ced4de;
                border-radius: 8px;
            }
            """
        )
        header_layout.addWidget(header_title)
        header_layout.addStretch(1)
        header_layout.addWidget(search, 0)

        canvas = QtWidgets.QFrame()
        canvas.setObjectName("canvas")
        canvas.setStyleSheet(
            """
            QFrame#canvas {
                background: #f4f7fb;
                border: 1px solid #d6dce7;
                border-radius: 16px;
            }
            """
        )
        canvas_layout = QtWidgets.QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(18, 18, 18, 18)
        canvas_layout.setSpacing(12)

        stats_row = QtWidgets.QHBoxLayout()
        for title, value in [("Comments", "12"), ("Open Issues", "4"), ("Reviewers", "3")]:
            card = QtWidgets.QFrame()
            card.setObjectName(f"stat_{title.lower().replace(' ', '_')}")
            card.setStyleSheet(
                """
                QFrame {
                    background: white;
                    border: 1px solid #dde3ec;
                    border-radius: 12px;
                }
                """
            )
            card_layout = QtWidgets.QVBoxLayout(card)
            top = QtWidgets.QLabel(title)
            number = QtWidgets.QLabel(value)
            number.setStyleSheet("font-size: 28px; font-weight: 700;")
            card_layout.addWidget(top)
            card_layout.addWidget(number)
            stats_row.addWidget(card)

        stack_zone = QtWidgets.QFrame()
        stack_zone.setObjectName("stackZone")
        stack_zone.setMinimumHeight(280)
        stack_zone.setStyleSheet(
            """
            QFrame#stackZone {
                background: #ecf2fc;
                border: 1px solid #cfd7e7;
                border-radius: 16px;
            }
            """
        )
        stack_zone.setLayout(QtWidgets.QVBoxLayout())
        stack_zone.layout().setContentsMargins(0, 0, 0, 0)

        base_panel = QtWidgets.QFrame(stack_zone)
        base_panel.setObjectName("basePanel")
        base_panel.setGeometry(30, 34, 360, 190)
        base_panel.setStyleSheet(
            """
            QFrame#basePanel {
                background: white;
                border: 1px solid #ccd4e0;
                border-radius: 14px;
            }
            """
        )
        base_layout = QtWidgets.QVBoxLayout(base_panel)
        base_label = QtWidgets.QLabel("Base panel")
        base_label.setObjectName("basePanelLabel")
        base_layout.addWidget(base_label)
        base_layout.addWidget(QtWidgets.QLabel("这里有 1px 边框，适合测试细节定位。"))

        overlay_card = OverlayCard(stack_zone)
        overlay_card.setGeometry(210, 88, 330, 170)

        list_table = QtWidgets.QTableWidget(4, 3)
        list_table.setObjectName("reviewTable")
        list_table.setHorizontalHeaderLabels(["Selector", "Status", "Owner"])
        list_table.horizontalHeader().setStretchLastSection(True)
        list_table.verticalHeader().setVisible(False)
        list_table.setStyleSheet(
            """
            QTableWidget#reviewTable {
                background: white;
                border: 1px solid #d8deea;
                border-radius: 12px;
                gridline-color: #edf1f7;
            }
            """
        )
        rows = [
            ("#sidebar", "Ready", "Alex"),
            ("#searchBox", "Review", "Mina"),
            ("#overlayCard", "Draft", "Chen"),
            ("#syncButton", "Todo", "You"),
        ]
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                list_table.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(value))

        canvas_layout.addLayout(stats_row)
        canvas_layout.addWidget(stack_zone)
        canvas_layout.addWidget(list_table, 1)

        content_layout.addWidget(header)
        content_layout.addWidget(canvas, 1)

        grid.addWidget(sidebar, 0, 0)
        grid.addWidget(content, 0, 1)
        grid.setColumnStretch(1, 1)


def main() -> None:
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
