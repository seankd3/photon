from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QSize
from PyQt6.QtGui import QImage, QPixmap
from photon.models import PhotoMetadata
from photon.image_processor import ImageProcessor
from typing import List

class ThumbnailGridModel(QAbstractListModel):
    def __init__(self, photos: List[PhotoMetadata], image_processor: ImageProcessor, parent=None):
        super().__init__(parent)
        self._photos = photos
        self._image_processor = image_processor
        self.thumbnail_size = QSize(160, 120) # Default thumbnail size

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
            # Load thumbnail asynchronously or from cache
            thumbnail_path = self._image_processor.generate_thumbnail(photo.file_path, self.thumbnail_size.width(), self.thumbnail_size.height())
            if thumbnail_path and os.path.exists(thumbnail_path):
                return QPixmap(thumbnail_path)
            return None # Placeholder for no thumbnail
        elif role == Qt.ItemDataRole.SizeHintRole:
            return self.thumbnail_size
        elif role == Qt.ItemDataRole.UserRole:
            return photo # Return the PhotoMetadata object
        return None

    def set_photos(self, photos: List[PhotoMetadata]):
        self.beginResetModel()
        self._photos = photos
        self.endResetModel()

    def set_thumbnail_size(self, width: int, height: int):
        self.thumbnail_size = QSize(width, height)
        # Emit dataChanged for all items to update their size hints and decorations
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, 0), [Qt.ItemDataRole.SizeHintRole, Qt.ItemDataRole.DecorationRole])
