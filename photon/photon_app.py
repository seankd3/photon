import sys
import os

# Redirect stdout and stderr to a log file
log_file_path = os.path.join(os.path.dirname(__file__), "..", "photon_log.txt")
sys.stdout = open(log_file_path, "w", encoding="utf-8")
sys.stderr = open(log_file_path, "a", encoding="utf-8")

from PyQt6.QtWidgets import QMainWindow, QDockWidget, QWidget
from PyQt6.QtCore import Qt, QModelIndex
from photon.views.folder_tree_view import FolderTreeView
from photon.views.thumbnail_grid_view import ThumbnailGridView
from photon.views.photo_preview_view import PhotoPreviewView
from photon.catalog_reader import LightroomCatalogReader
from photon.utils import extract_lrcat_data
from photon.models import FolderNode, LightroomCatalog
import asyncio
from typing import Optional


class PhotonApp(QMainWindow):
    folder_tree_view: FolderTreeView
    lightroom_catalog: Optional[LightroomCatalog]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photon - Photo Culling Application")

        # Central widget placeholder (can be hidden or used for status/welcome)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.catalog_reader = LightroomCatalogReader()
        self.lightroom_catalog = None

        self.create_dock_widgets()
        self.apply_dark_theme()

        # Load the user's Lightroom catalog
        self.load_catalog(
            r"C:\Users\smast\OneDrive\Desktop\Code Projects\Photon\TestCatolog\2025.lrcat"
        )

    def create_dock_widgets(self) -> None:
        # Folder Tree Panel
        self.folder_tree_view = FolderTreeView([])  # Initialize with empty list
        folder_dock = QDockWidget("Folders", self)
        folder_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        folder_dock.setWidget(self.folder_tree_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, folder_dock)

        # Connect signals for lazy loading
        self.folder_tree_view.model.fetch_children_requested.connect(self._on_fetch_children_requested)

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

    def apply_dark_theme(self) -> None:
        self.setStyleSheet(
            """
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
        """
        )

    def load_catalog(self, catalog_path: str) -> None:
        extracted_db_path = os.path.join(
            os.path.dirname(catalog_path),
            f"{os.path.basename(catalog_path)}.extracted.db",
        )

        try:
            # Attempt to extract data if the extracted DB doesn't exist or is older than the lrcat
            if not os.path.exists(extracted_db_path) or os.path.getmtime(
                extracted_db_path
            ) < os.path.getmtime(catalog_path):
                print(f"Extracting data from {catalog_path} to {extracted_db_path}...")
                extract_lrcat_data(catalog_path, extracted_db_path)

            asyncio.run(self._load_catalog(extracted_db_path))
        except Exception as e:
            print(f"Error loading catalog: {e}")

    async def _load_catalog(self, catalog_path: str) -> None:
        try:
            self.lightroom_catalog = await self.catalog_reader.load_catalog_async(
                catalog_path=catalog_path
            )
            self.folder_tree_view.model._root_folders = (
                self.lightroom_catalog.root_folders
            )
            self.folder_tree_view.model.modelReset.emit()
            print("Catalog loaded successfully into UI.")
        except Exception as e:
            print(f"Error loading catalog: {e}")

    def _on_fetch_children_requested(self, folder_node: FolderNode, model_index: QModelIndex) -> None:
        # This slot is called when the model needs to fetch more children
        # It runs in the main thread, so we should offload the actual fetching
        # to avoid blocking the UI.
        # For simplicity, we'll run it directly here for now, but for a real app,
        # consider a QThread or QThreadPool for long-running operations.
        try:
            # Assuming catalog_path is available from the initial load
            if self.lightroom_catalog is None:
                print("Error: Lightroom catalog not loaded.")
                return

            catalog_path = self.lightroom_catalog.file_path
            new_children = self.catalog_reader.get_folder_children(catalog_path, folder_node.id)

            # Update the model with the new children
            self.folder_tree_view.model.update_folder_children(folder_node, new_children, model_index)

            # Add new children to the main catalog's folders_by_id for future lookups
            for child in new_children:
                self.lightroom_catalog.folders_by_id[child.id] = child
                # Also link the parent-child relationship in the catalog's data structure
                folder_node.add_child(child)

        except Exception as e:
            print(f"Error fetching folder children: {e}")
