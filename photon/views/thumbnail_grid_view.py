from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class ThumbnailGridView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Thumbnail Grid Content", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        self.setStyleSheet("""
            ThumbnailGridView {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: none;
            }
        """)
