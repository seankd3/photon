from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListView
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from photon.models import LightroomCatalog, PhotoMetadata, FolderNode
from photon.image_processor import ImageProcessor
from photon.views.thumbnail_grid_model import ThumbnailGridModel


class ThumbnailGridView(QWidget):
    photo_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.catalog = None
        self.image_processor = ImageProcessor()  # Initialize ImageProcessor

        layout = QVBoxLayout(self)
        self.list_view = QListView(self)
        self.list_view.setFlow(QListView.Flow.LeftToRight)
        self.list_view.setWrapping(True)
        self.list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.list_view.setViewMode(QListView.ViewMode.IconMode)
        self.list_view.setUniformItemSizes(True)

        self.model = ThumbnailGridModel([], self.image_processor)
        self.list_view.setModel(self.model)
        self.list_view.setGridSize(self.model.thumbnail_size)
        self.list_view.setSpacing(5)

        self.list_view.clicked.connect(self._on_thumbnail_clicked)

        layout.addWidget(self.list_view)
        self.setLayout(layout)

        self.setStyleSheet(
            """
            ThumbnailGridView {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: none;
            }
            QListView {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: none;
            }
            QListView::item {
                border: 1px solid #444444;
                padding: 5px;
            }
            QListView::item:selected {
                background-color: #3E3E40;
            }
        """
        )

    def set_catalog(self, catalog: LightroomCatalog):
        self.catalog = catalog
        if self.catalog:
            self.model.set_photos(list(self.catalog.photos_by_id.values()))
        else:
            self.model.set_photos([])

    def set_folder(self, folder: FolderNode):
        if self.catalog and folder:
            photos_in_folder = [
                photo
                for photo in self.catalog.photos_by_id.values()
                if photo.folder_id == folder.id
            ]
            self.model.set_photos(photos_in_folder)
        else:
            self.model.set_photos([])

    def _on_thumbnail_clicked(self, index: QModelIndex) -> None:
        if index.isValid():
            photo = self.model.data(index, Qt.ItemDataRole.UserRole)
            if isinstance(photo, PhotoMetadata):
                self.photo_selected.emit(photo.id)
