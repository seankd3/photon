from PyQt6.QtWidgets import QMainWindow, QDockWidget, QTextEdit, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from photon.views.folder_tree_view import FolderTreeView
from photon.views.thumbnail_grid_view import ThumbnailGridView
from photon.views.photo_preview_view import PhotoPreviewView
from photon.catalog_reader import LightroomCatalogReader
from photon.catalog_loader import CatalogLoader
import asyncio
import os

class PhotonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photon - Photo Culling Application")
        
        # Central widget placeholder (can be hidden or used for status/welcome)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.catalog_reader = LightroomCatalogReader()
        self.lightroom_catalog = None
        self.catalog_loader = None # Initialize to None

        self.create_dock_widgets()
        self.apply_dark_theme()

        # Example: Load a catalog (this can be triggered by user action later)
        # For now, we'll keep it commented out to avoid blocking during initial setup
        # self.load_catalog(r"C:\Pictures\Lightroom\Catalogs\2025\2025\2025.lrcat")

    def load_catalog(self, catalog_path: str):
        if not os.path.exists(catalog_path):
            QMessageBox.warning(self, "Catalog Not Found", f"The specified catalog path does not exist:\n{catalog_path}")
            return

        if self.catalog_loader and self.catalog_loader.isRunning():
            QMessageBox.information(self, "Loading in Progress", "A catalog is already being loaded. Please wait.")
            return

        self.catalog_loader = CatalogLoader(catalog_path)
        self.catalog_loader.catalog_loaded.connect(self._on_catalog_loaded)
        self.catalog_loader.error_occurred.connect(self._on_catalog_error)
        self.catalog_loader.start()
        print(f"Started loading catalog from {catalog_path} in a separate thread.")

    def _on_catalog_loaded(self, catalog: LightroomCatalog):
        self.lightroom_catalog = catalog
        self.folder_tree_view.model._root_folders = self.lightroom_catalog.root_folders
        self.folder_tree_view.model.modelReset.emit()
        print("Catalog loaded successfully into UI.")
        # TODO: Pass catalog to ThumbnailGridView and PhotoPreviewView

    def _on_catalog_error(self, message: str):
        QMessageBox.critical(self, "Catalog Loading Error", message)
        print(f"Error loading catalog: {message}")


    def create_dock_widgets(self):
        # Folder Tree Panel
        self.folder_tree_view = FolderTreeView([]) # Initialize with empty list
        folder_dock = QDockWidget("Folders", self)
        folder_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        folder_dock.setWidget(self.folder_tree_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, folder_dock)

        # Thumbnail Grid Panel
        thumbnail_dock = QDockWidget("Thumbnails", self)
        thumbnail_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        thumbnail_grid_view = ThumbnailGridView()
        thumbnail_dock.setWidget(thumbnail_grid_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, thumbnail_dock)

        # Photo Preview Panel
        preview_dock = QDockWidget("Preview", self)
        preview_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        photo_preview_view = PhotoPreviewView()
        preview_dock.setWidget(photo_preview_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, preview_dock)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #CCCCCC;
            }
            QDockWidget {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: 2px solid #555555; /* Increased border thickness and color */
            }
            QDockWidget::title {
                background-color: #3E3E40;
                padding: 5px;
                border-bottom: 1px solid #555555; /* Added bottom border to title */
            }
            QTextEdit {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: none;
            }
            QTreeView {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: none;
            }
            QTreeView::item {
                padding: 3px;
            }
            QTreeView::item:selected {
                background-color: #3E3E40;
            }
        """)

    def load_catalog(self, catalog_path):
        if os.path.exists(catalog_path):
            asyncio.run(self._load_catalog(catalog_path))
        else:
            print(f"Catalog not found at {catalog_path}".encode('utf-8', 'replace').decode('utf-8'))

    async def _load_catalog(self, catalog_path):
        try:
            self.lightroom_catalog = await self.catalog_reader.load_catalog_async(catalog_path)
            self.folder_tree_view.model._root_folders = self.lightroom_catalog.root_folders
            self.folder_tree_view.model.modelReset.emit()
            print("Catalog loaded successfully into UI.")
        except Exception as e:
            print(f"Error loading catalog: {e}")