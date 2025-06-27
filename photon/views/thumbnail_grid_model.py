from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize, QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
from photon.models import PhotoMetadata
from photon.image_processor import ImageProcessor
from typing import List
import os

class ThumbnailLoader(QRunnable):
    def __init__(self, image_processor: ImageProcessor, photo_path: str, size: QSize, index: QModelIndex, callback):
        super().__init__()
        self.image_processor = image_processor
        self.photo_path = photo_path
        self.size = size
        self.index = index
        self.callback = callback

    def run(self):
        thumbnail_path = self.image_processor._generate_thumbnail_sync(self.photo_path, (self.size.width(), self.size.height()))
        if thumbnail_path and os.path.exists(thumbnail_path):
            self.callback(self.index, QPixmap(thumbnail_path))
        else:
            self.callback(self.index, None) # Indicate failure to load thumbnail

class ThumbnailGridModel(QAbstractListModel):
    thumbnail_loaded = pyqtSignal(QModelIndex, QPixmap)

    def __init__(self, photos: List[PhotoMetadata], image_processor: ImageProcessor, parent=None):
        super().__init__(parent)
        self._photos = photos
        self._image_processor = image_processor
        self.thumbnail_size = QSize(160, 120) # Default thumbnail size
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(os.cpu_count() or 1)
        self.thumbnail_loaded.connect(self._on_thumbnail_loaded)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._photos)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> any:
        if not index.isValid() or not (0 <= index.row() < len(self._photos)):
            return None

        photo = self._photos[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return photo.file_name # Display file name
        elif role == Qt.ItemDataRole.DecorationRole:
            # Check if thumbnail is already cached in PhotoMetadata object
            if photo.thumbnail_path and os.path.exists(photo.thumbnail_path):
                return QPixmap(photo.thumbnail_path)
            else:
                # Request thumbnail generation asynchronously
                worker = ThumbnailLoader(self._image_processor, photo.file_path, self.thumbnail_size, index, self.thumbnail_loaded.emit)
                self.thread_pool.start(worker)
                return None # Return None for now, thumbnail will be loaded later
        elif role == Qt.ItemDataRole.SizeHintRole:
            return self.thumbnail_size
        elif role == Qt.ItemDataRole.UserRole:
            return photo # Return the PhotoMetadata object
        return None

    def _on_thumbnail_loaded(self, index: QModelIndex, pixmap: QPixmap):
        photo = self._photos[index.row()]
        if pixmap:
            photo.thumbnail_path = self._image_processor._generate_thumbnail_sync(photo.file_path, (self.thumbnail_size.width(), self.thumbnail_size.height()))
        else:
            # Use a placeholder for failed thumbnails
            photo.thumbnail_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cache", "thumbnails", "error_thumbnail.png")

        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])

    def set_photos(self, photos: List[PhotoMetadata]):
        self.beginResetModel()
        self._photos = photos
        self.endResetModel()

    def set_thumbnail_size(self, width: int, height: int):
        self.thumbnail_size = QSize(width, height)
        # Emit dataChanged for all items to update their size hints and decorations
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, 0), [Qt.ItemDataRole.SizeHintRole, Qt.ItemDataRole.DecorationRole])
