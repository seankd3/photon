from PyQt6.QtWidgets import QMainWindow, QDockWidget, QTextEdit, QWidget, QVBoxLayout, QMessageBox, QMenu
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
from photon.culling_db import CullingDatabase
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
        
        # Central widget for welcome message or status
        self.central_label = QLabel("Welcome to Photon! Load a Lightroom catalog to begin.")
        self.central_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_label.setStyleSheet("font-size: 24px; color: #AAAAAA;")
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self.central_label)
        self.setCentralWidget(central_widget)

        self.catalog_reader = LightroomCatalogReader()
        self.lightroom_catalog = None
        self.catalog_loader = None # Initialize to None
        self.culling_db = CullingDatabase(os.path.join(os.path.dirname(__file__), "culling.db"))

        self.create_dock_widgets()
        self.apply_dark_theme()
        self._create_actions()
        self._create_menu_bar()

        # Example: Load a catalog (this can be triggered by user action later)
        # For now, we'll keep it commented out to avoid blocking during initial setup
        # self.load_catalog(r"C:\Pictures\Lightroom\Catalogs\2025\2025\2025.lrcat")

    def _create_actions(self):
        self.next_photo_action = QAction("Next Photo", self)
        self.next_photo_action.setShortcut(QKeySequence(Qt.Key.Key_Right))
        self.next_photo_action.triggered.connect(self._next_photo)
        self.addAction(self.next_photo_action)

        self.prev_photo_action = QAction("Previous Photo", self)
        self.prev_photo_action.setShortcut(QKeySequence(Qt.Key.Key_Left))
        self.prev_photo_action.triggered.connect(self._prev_photo)
        self.addAction(self.prev_photo_action)

        self.pick_photo_action = QAction("Pick Photo", self)
        self.pick_photo_action.setShortcut(QKeySequence(Qt.Key.Key_P))
        self.pick_photo_action.triggered.connect(self._pick_photo)
        self.addAction(self.pick_photo_action)

        self.reject_photo_action = QAction("Reject Photo", self)
        self.reject_photo_action.setShortcut(QKeySequence(Qt.Key.Key_X))
        self.reject_photo_action.triggered.connect(self._reject_photo)
        self.addAction(self.reject_photo_action)

        self.rate_1_action = QAction("Rate 1 Star", self)
        self.rate_1_action.setShortcut(QKeySequence(Qt.Key.Key_1))
        self.rate_1_action.triggered.connect(lambda: self._rate_photo(1))
        self.addAction(self.rate_1_action)

        self.rate_2_action = QAction("Rate 2 Stars", self)
        self.rate_2_action.setShortcut(QKeySequence(Qt.Key.Key_2))
        self.rate_2_action.triggered.connect(lambda: self._rate_photo(2))
        self.addAction(self.rate_2_action)

        self.rate_3_action = QAction("Rate 3 Stars", self)
        self.rate_3_action.setShortcut(QKeySequence(Qt.Key.Key_3))
        self.rate_3_action.triggered.connect(lambda: self._rate_photo(3))
        self.addAction(self.rate_3_action)

        self.rate_4_action = QAction("Rate 4 Stars", self)
        self.rate_4_action.setShortcut(QKeySequence(Qt.Key.Key_4))
        self.rate_4_action.triggered.connect(lambda: self._rate_photo(4))
        self.addAction(self.rate_4_action)

        self.rate_5_action = QAction("Rate 5 Stars", self)
        self.rate_5_action.setShortcut(QKeySequence(Qt.Key.Key_5))
        self.rate_5_action.triggered.connect(lambda: self._rate_photo(5))
        self.addAction(self.rate_5_action)

        self.rate_0_action = QAction("Rate 0 Stars", self)
        self.rate_0_action.setShortcut(QKeySequence(Qt.Key.Key_0))
        self.rate_0_action.triggered.connect(lambda: self._rate_photo(0))
        self.addAction(self.rate_0_action)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        # Add actions to file menu later (e.g., Open Catalog)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.folder_tree_view.toggleViewAction())
        view_menu.addAction(self.thumbnail_grid_view.toggleViewAction())
        view_menu.addAction(self.photo_preview_view.toggleViewAction())

        culling_menu = menu_bar.addMenu("&Culling")
        culling_menu.addAction(self.next_photo_action)
        culling_menu.addAction(self.prev_photo_action)
        culling_menu.addSeparator()
        culling_menu.addAction(self.pick_photo_action)
        culling_menu.addAction(self.reject_photo_action)
        culling_menu.addSeparator()
        culling_menu.addAction(self.rate_1_action)
        culling_menu.addAction(self.rate_2_action)
        culling_menu.addAction(self.rate_3_action)
        culling_menu.addAction(self.rate_4_action)
        culling_menu.addAction(self.rate_5_action)
        culling_menu.addAction(self.rate_0_action)

    def _next_photo(self):
        current_index = self.thumbnail_grid_view.list_view.currentIndex()
        if current_index.isValid():
            next_row = current_index.row() + 1
            if next_row < self.thumbnail_grid_view.model.rowCount():
                next_index = self.thumbnail_grid_view.model.index(next_row, 0)
                self.thumbnail_grid_view.list_view.setCurrentIndex(next_index)
                self._on_photo_selected(self.thumbnail_grid_view.model.data(next_index, Qt.ItemDataRole.UserRole))

    def _prev_photo(self):
        current_index = self.thumbnail_grid_view.list_view.currentIndex()
        if current_index.isValid():
            prev_row = current_index.row() - 1
            if prev_row >= 0:
                prev_index = self.thumbnail_grid_view.model.index(prev_row, 0)
                self.thumbnail_grid_view.list_view.setCurrentIndex(prev_index)
                self._on_photo_selected(self.thumbnail_grid_view.model.data(prev_index, Qt.ItemDataRole.UserRole))

    self.central_label.setText("Catalog loaded successfully!")
        self.central_label.hide() # Hide welcome message after loading

        # Apply culling data to photos
        all_photo_ids = [photo.id for photo in self.lightroom_catalog.photos_by_id.values()]
        culling_data = self.culling_db.load_culling_data(all_photo_ids)
        for photo_id, data in culling_data.items():
            if photo_id in self.lightroom_catalog.photos_by_id:
                photo = self.lightroom_catalog.photos_by_id[photo_id]
                photo.rating = data["rating"]
                photo.is_picked = data["is_picked"]
                photo.is_rejected = data["is_rejected"]
                photo.color_label = data["color_label"]

    def _on_catalog_error(self, message: str):
        QMessageBox.critical(self, "Catalog Loading Error", message)
        self.central_label.setText(f"Error loading catalog: {message}")
        self.central_label.show() # Show error message