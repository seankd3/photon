from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

class GridView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.image_widgets = []

    def add_thumbnail(self, image_data: bytes, image_info: object):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        if pixmap.isNull():
            return
        label = QLabel(self)
        label.setFixedSize(256, 256)
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.layout.addWidget(label, len(self.image_widgets) // 4, len(self.image_widgets) % 4)
        self.image_widgets.append(label)
