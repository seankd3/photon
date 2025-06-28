import os

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QLabel,
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt

from photon.culling_db import CullingDatabase
from photon.views.folder_tree_view import FolderTreeView
from photon.views.thumbnail_grid_view import ThumbnailGridView
from photon.views.photo_preview_view import PhotoPreviewView
from photon.catalog_reader import LightroomCatalogReader
from photon.catalog_loader import CatalogLoader
from photon.models import LightroomCatalog


class PhotonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photon - Photo Culling Application")

        

        self.catalog_reader = LightroomCatalogReader()
        self.lightroom_catalog = None
        self.catalog_loader = None  # Initialize to None
        self.culling_db = CullingDatabase(
            os.path.join(os.path.dirname(__file__), "culling.db")
        )

        self.folder_tree_view = None
        self.thumbnail_grid_view = None
        self.photo_preview_view = None

        self.apply_dark_theme()
        self._create_actions()
        self._create_menu_bar()

    def create_dock_widgets(self):
        # Navigator Panel (formerly Folder Tree View)
        self.navigator_dock = QDockWidget("Navigator", self)
        self.navigator_dock.setWidget(self.folder_tree_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.navigator_dock)

        # Grid Panel (formerly Thumbnail Grid View)
        self.grid_dock = QDockWidget("Grid", self)
        self.grid_dock.setWidget(self.thumbnail_grid_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.grid_dock)

        # Loupe Panel (formerly Photo Preview View)
        self.loupe_dock = QDockWidget("Loupe", self)
        self.loupe_dock.setWidget(self.photo_preview_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.loupe_dock)

        # Set the Loupe panel as the central widget area, effectively making it the main view
        self.setCentralWidget(self.loupe_dock.widget())
        self.loupe_dock.setTitleBarWidget(QWidget()) # Hide title bar if it's the central widget
        self.loupe_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures) # Disable docking features for central widget
        self.loupe_dock.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea) # Prevent undocking
        self.loupe_dock.setFloating(False) # Ensure it's not floating

    def apply_dark_theme(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #25282C;
                color: #E0E0E0;
            }
            QDockWidget {
                background-color: #2E3136;
                color: #E0E0E0;
                border: 1px solid #45494E;
            }
            QDockWidget::title {
                background-color: #2E3136;
                padding: 8px;
                border-bottom: 1px solid #45494E;
                font-weight: bold;
            }
            QTextEdit, QTreeView, QListView {
                background-color: #25282C;
                color: #E0E0E0;
                border: 1px solid #45494E;
                font-size: 14px;
            }
            QTreeView::item, QListView::item {
                padding: 5px;
            }
            QTreeView::item:selected, QListView::item:selected {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QTreeView::item:hover, QListView::item:hover {
                background-color: #3A3D42;
            }
            QHeaderView::section {
                background-color: #2E3136;
                color: #E0E0E0;
                padding: 6px;
                border: 1px solid #45494E;
                font-weight: bold;
            }
            QMenuBar {
                background-color: #2E3136;
                color: #E0E0E0;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QMenu {
                background-color: #2E3136;
                color: #E0E0E0;
                border: 1px solid #45494E;
            }
            QMenu::item {
                padding: 8px 25px;
            }
            QMenu::item:selected {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: 1px solid #45494E;
                background: #25282C;
                width: 15px;
                margin: 15px 0 15px 0;
            }
            QScrollBar::handle:vertical {
                background: #3A3D42;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: 1px solid #45494E;
                background: #25282C;
                height: 15px;
                margin: 0 15px 0 15px;
            }
            QScrollBar::handle:horizontal {
                background: #3A3D42;
                min-width: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
            QMessageBox {
                background-color: #2E3136;
            }
            QMessageBox QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #007ACC;
                color: #FFFFFF;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #005F99;
            }
            QSplitter::handle {
                background-color: #45494E;
                border: 1px solid #2E3136;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
        """
        )

    def _on_photo_selected(self, photo_id: str):
        if self.lightroom_catalog and photo_id in self.lightroom_catalog.photos_by_id:
            photo = self.lightroom_catalog.photos_by_id[photo_id]
            self.photo_preview_view.set_photo(photo)

    def _pick_photo(self):
        current_photo_id = self.photo_preview_view.current_photo_id
        if (
            current_photo_id
            and self.lightroom_catalog
            and current_photo_id in self.lightroom_catalog.photos_by_id
        ):
            photo = self.lightroom_catalog.photos_by_id[current_photo_id]
            photo.is_picked = not photo.is_picked
            photo.is_rejected = False  # Cannot be both picked and rejected
            self.culling_db.save_culling_data(
                photo.id,
                photo.rating,
                photo.is_picked,
                photo.is_rejected,
                photo.color_label,
            )
            self.photo_preview_view.update_culling_status(photo)
            self.thumbnail_grid_view.model.dataChanged.emit(
                self.thumbnail_grid_view.list_view.currentIndex(),
                self.thumbnail_grid_view.list_view.currentIndex(),
            )

    def _reject_photo(self):
        current_photo_id = self.photo_preview_view.current_photo_id
        if (
            current_photo_id
            and self.lightroom_catalog
            and current_photo_id in self.lightroom_catalog.photos_by_id
        ):
            photo = self.lightroom_catalog.photos_by_id[current_photo_id]
            photo.is_rejected = not photo.is_rejected
            photo.is_picked = False  # Cannot be both picked and rejected
            self.culling_db.save_culling_data(
                photo.id,
                photo.rating,
                photo.is_picked,
                photo.is_rejected,
                photo.color_label,
            )
            self.photo_preview_view.update_culling_status(photo)
            self.thumbnail_grid_view.model.dataChanged.emit(
                self.thumbnail_grid_view.list_view.currentIndex(),
                self.thumbnail_grid_view.list_view.currentIndex(),
            )

    def _rate_photo(self, rating: int):
        current_photo_id = self.photo_preview_view.current_photo_id
        if (
            current_photo_id
            and self.lightroom_catalog
            and current_photo_id in self.lightroom_catalog.photos_by_id
        ):
            photo = self.lightroom_catalog.photos_by_id[current_photo_id]
            photo.rating = rating
            self.culling_db.save_culling_data(
                photo.id,
                photo.rating,
                photo.is_picked,
                photo.is_rejected,
                photo.color_label,
            )
            self.photo_preview_view.update_culling_status(photo)
            self.thumbnail_grid_view.model.dataChanged.emit(
                self.thumbnail_grid_view.list_view.currentIndex(),
                self.thumbnail_grid_view.list_view.currentIndex(),
            )

    def _set_color_label(self, color: str):
        current_photo_id = self.photo_preview_view.current_photo_id
        if (
            current_photo_id
            and self.lightroom_catalog
            and current_photo_id in self.lightroom_catalog.photos_by_id
        ):
            photo = self.lightroom_catalog.photos_by_id[current_photo_id]
            photo.color_label = color
            self.culling_db.save_culling_data(
                photo.id,
                photo.rating,
                photo.is_picked,
                photo.is_rejected,
                photo.color_label,
            )
            self.photo_preview_view.update_culling_status(photo)
            self.thumbnail_grid_view.model.dataChanged.emit(
                self.thumbnail_grid_view.list_view.currentIndex(),
                self.thumbnail_grid_view.list_view.currentIndex(),
            )

    def load_catalog(self, catalog_path: str):
        if not os.path.exists(catalog_path):
            QMessageBox.critical(
                self,
                "File Not Found",
                f"The specified catalog file does not exist:\n{catalog_path}",
            )
            return

        QApplication.processEvents()  # Update UI immediately

        self.catalog_loader = CatalogLoader(catalog_path)
        self.catalog_loader.catalog_loaded.connect(self._on_catalog_loaded)
        self.catalog_loader.error_occurred.connect(self._on_catalog_error)
        self.catalog_loader.start()

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

        self._create_color_label_actions()

    def _create_color_label_actions(self):
        self.color_red_action = QAction("Red", self)
        self.color_red_action.setShortcut(QKeySequence(Qt.Key.Key_6))
        self.color_red_action.triggered.connect(lambda: self._set_color_label("Red"))
        self.addAction(self.color_red_action)

        self.color_yellow_action = QAction("Yellow", self)
        self.color_yellow_action.setShortcut(QKeySequence(Qt.Key.Key_7))
        self.color_yellow_action.triggered.connect(lambda: self._set_color_label("Yellow"))
        self.addAction(self.color_yellow_action)

        self.color_green_action = QAction("Green", self)
        self.color_green_action.setShortcut(QKeySequence(Qt.Key.Key_8))
        self.color_green_action.triggered.connect(lambda: self._set_color_label("Green"))
        self.addAction(self.color_green_action)

        self.color_blue_action = QAction("Blue", self)
        self.color_blue_action.setShortcut(QKeySequence(Qt.Key.Key_9))
        self.color_blue_action.triggered.connect(lambda: self._set_color_label("Blue"))
        self.addAction(self.color_blue_action)

        self.color_purple_action = QAction("Purple", self)
        self.color_purple_action.setShortcut(QKeySequence(Qt.Key.Key_QuoteLeft))
        self.color_purple_action.triggered.connect(lambda: self._set_color_label("Purple"))
        self.addAction(self.color_purple_action)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        menu_bar.addMenu("&File")
        # Add actions to file menu later (e.g., Open Catalog)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.navigator_dock.toggleViewAction())
        view_menu.addAction(self.grid_dock.toggleViewAction())
        view_menu.addAction(self.loupe_dock.toggleViewAction())

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
        culling_menu.addSeparator()
        culling_menu.addAction(self.color_red_action)
        culling_menu.addAction(self.color_yellow_action)
        culling_menu.addAction(self.color_green_action)
        culling_menu.addAction(self.color_blue_action)
        culling_menu.addAction(self.color_purple_action)

    def _next_photo(self):
        current_index = self.thumbnail_grid_view.list_view.currentIndex()
        if current_index.isValid():
            next_row = current_index.row() + 1
            if next_row < self.thumbnail_grid_view.model.rowCount():
                next_index = self.thumbnail_grid_view.model.index(next_row, 0)
                self.thumbnail_grid_view.list_view.setCurrentIndex(next_index)
                self._on_photo_selected(
                    self.thumbnail_grid_view.model.data(
                        next_index, Qt.ItemDataRole.UserRole
                    )
                )

    def _prev_photo(self):
        current_index = self.thumbnail_grid_view.list_view.currentIndex()
        if current_index.isValid():
            prev_row = current_index.row() - 1
            if prev_row >= 0:
                prev_index = self.thumbnail_grid_view.model.index(prev_row, 0)
                self.thumbnail_grid_view.list_view.setCurrentIndex(prev_index)
                self._on_photo_selected(
                    self.thumbnail_grid_view.model.data(
                        prev_index, Qt.ItemDataRole.UserRole
                    )
                )

    def _on_catalog_loaded(self, catalog: LightroomCatalog):
        self.lightroom_catalog = catalog

        self.folder_tree_view = None
        self.thumbnail_grid_view = None
        self.photo_preview_view = None

        self.create_dock_widgets()

        self.folder_tree_view.folder_selected.connect(
            self.thumbnail_grid_view.set_folder
        )
        self.thumbnail_grid_view.photo_selected.connect(self._on_photo_selected)

        self.thumbnail_grid_view.set_catalog(self.lightroom_catalog)
        self.photo_preview_view.set_catalog(self.lightroom_catalog)
        self.loupe_dock.show() # Show the loupe panel

        # Apply culling data to photos
        all_photo_ids = [
            photo.id for photo in self.lightroom_catalog.photos_by_id.values()
        ]
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
        # self.central_label.setText(f"Error loading catalog: {message}") # Removed central label
        # self.central_label.show()  # Removed central label
