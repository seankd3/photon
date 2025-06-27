from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from photon.models import LightroomCatalog

class ThumbnailGridView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.catalog = None
        layout = QVBoxLayout(self)
        self.label = QLabel("Thumbnail Grid Content", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setStyleSheet("""
            ThumbnailGridView {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: none;
            }
        """)

    def set_catalog(self, catalog: LightroomCatalog):
        self.catalog = catalog
        if self.catalog:
            self.label.setText(f"Thumbnail Grid: {len(self.catalog.photos_by_id)} photos")
        else:
            self.label.setText("Thumbnail Grid Content")
