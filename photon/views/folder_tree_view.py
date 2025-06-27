from PyQt6.QtWidgets import QTreeView
from PyQt6.QtCore import Qt
from photon.views.folder_tree_model import FolderTreeModel

class FolderTreeView(QTreeView):
    def __init__(self, root_folders, parent=None):
        super().__init__(parent)
        self.model = FolderTreeModel(root_folders)
        self.setModel(self.model)
        self.setHeaderHidden(True)

        self.setStyleSheet("""
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