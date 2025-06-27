from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class PhotoPreviewView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Photo Preview Content", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        self.setStyleSheet("""
            PhotoPreviewView {
                background-color: #3E3E40;
                color: #CCCCCC;
                border: none;
            }
        """)
