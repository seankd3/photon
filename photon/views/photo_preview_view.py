from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from photon.models import LightroomCatalog

class PhotoPreviewView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.catalog = None
        layout = QVBoxLayout(self)
        self.label = QLabel("Photo Preview Content", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setStyleSheet("""
            PhotoPreviewView {
                background-color: #3E3E40;
                color: #CCCCCC;
                border: none;
            }
        """)

    def set_catalog(self, catalog: LightroomCatalog):
        self.catalog = catalog
        if self.catalog:
            self.label.setText(f"Photo Preview: {len(self.catalog.photos_by_id)} photos in catalog")
        else:
            self.label.setText("Photo Preview Content")
