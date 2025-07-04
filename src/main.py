import sys
import json
import os
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDockWidget, QShortcut, QScrollArea
)
from src.worker import Worker
from src.grid_view import GridView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photon")
        self.setGeometry(100, 100, 1200, 800)

        self.grid_view = GridView()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.grid_view)
        self.setCentralWidget(self.scroll_area)

        # Create dockable panels
        self.left_panel = QDockWidget("Left Panel", self)
        self.left_panel.setObjectName("LeftPanel")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_panel)
        self.left_panel.setWidget(QLabel("Navigator, Folder Tree, Collections"))

        self.right_panel = QDockWidget("Right Panel", self)
        self.right_panel.setObjectName("RightPanel")
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_panel)
        self.right_panel.setWidget(QLabel("Histogram, Quick Info, EXIF"))

        self.filmstrip_panel = QDockWidget("Filmstrip", self)
        self.filmstrip_panel.setObjectName("FilmstripPanel")
        self.addDockWidget(Qt.BottomDockWidgetArea, self.filmstrip_panel)
        self.filmstrip_panel.setWidget(QLabel("Filmstrip Thumbnails"))

        self.load_catalog()
        self.setup_shortcuts()
        self.load_layout()

    def load_catalog(self):
        catalog_path = "C:/Users/smast/OneDrive/Desktop/CodeProjects/Photon/TestCatolog/2025.lrcat"

        self.thread = QThread()
        self.worker = Worker(catalog_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.image_ready.connect(self.grid_view.add_thumbnail)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        

        self.thread.start()

    

    

    def setup_shortcuts(self):
        # Tab to toggle side panels
        self.tab_shortcut = QShortcut(Qt.Key_Tab, self)
        self.tab_shortcut.activated.connect(self.toggle_side_panels)

        # Shift+Tab to toggle all UI chrome
        self.shift_tab_shortcut = QShortcut(Qt.ShiftModifier | Qt.Key_Tab, self)
        self.shift_tab_shortcut.activated.connect(self.toggle_all_chrome)

    def toggle_side_panels(self):
        self.left_panel.setVisible(not self.left_panel.isVisible())
        self.right_panel.setVisible(not self.right_panel.isVisible())

    def toggle_all_chrome(self):
        is_visible = self.menuBar().isVisible()
        self.menuBar().setVisible(not is_visible)
        self.left_panel.setVisible(not is_visible)
        self.right_panel.setVisible(not is_visible)
        self.filmstrip_panel.setVisible(not is_visible)

    def load_layout(self):
        layout_file = "layout.json"
        if os.path.exists(layout_file):
            with open(layout_file, "r") as f:
                layout_data = json.load(f)
                self.restoreGeometry(bytes.fromhex(layout_data["geometry"]))
                self.restoreState(bytes.fromhex(layout_data["state"]))

    def closeEvent(self, event):
        self.save_layout()
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)

    def save_layout(self):
        layout_file = "layout.json"
        layout_data = {
            "geometry": self.saveGeometry().toHex().data().decode("utf-8"),
            "state": self.saveState().toHex().data().decode("utf-8")
        }
        with open(layout_file, "w") as f:
            json.dump(layout_data, f, indent=4)


import qdarkstyle


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
