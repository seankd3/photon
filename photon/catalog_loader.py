from PyQt6.QtCore import QThread, pyqtSignal
from photon.catalog_reader import LightroomCatalogReader
from photon.models import LightroomCatalog

class CatalogLoader(QThread):
    catalog_loaded = pyqtSignal(LightroomCatalog)
    error_occurred = pyqtSignal(str)

    def __init__(self, catalog_path: str):
        super().__init__()
        self.catalog_path = catalog_path
        self.catalog_reader = LightroomCatalogReader()

    def run(self):
        try:
            catalog = self.catalog_reader.load_catalog_async(self.catalog_path)
            self.catalog_loaded.emit(catalog)
        except Exception as e:
            self.error_occurred.emit(f"Error loading catalog: {e}")
