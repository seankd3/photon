from PyQt5.QtCore import QObject, pyqtSignal

class Worker(QObject):
    image_ready = pyqtSignal(bytes, object)
    finished = pyqtSignal()

    def __init__(self, catalog_path):
        super().__init__()
        self.catalog_path = catalog_path

    def run(self):
        from src.catalog import get_images
        from src.thumbnail_loader import generate_thumbnail_data

        images = get_images(self.catalog_path)
        for image_data in images:
            absolute_path = image_data[3]
            thumbnail_data = generate_thumbnail_data(absolute_path)
            if thumbnail_data:
                self.image_ready.emit(thumbnail_data, image_data)
        self.finished.emit()
