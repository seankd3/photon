from PyQt6.QtWidgets import QTreeView
from PyQt6.QtCore import Qt, pyqtSignal
from photon.views.folder_tree_model import FolderTreeModel
from photon.models import FolderNode

class FolderTreeView(QTreeView):
    folder_selected = pyqtSignal(FolderNode)

    def __init__(self, root_folders, parent=None):
        super().__init__(parent)
        self.model = FolderTreeModel(root_folders)
        self.setModel(self.model)
        self.setHeaderHidden(True)

        self.clicked.connect(self._on_folder_clicked)

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

    def _on_folder_clicked(self, index):
        if index.isValid():
            folder_node = self.model.data(index, Qt.ItemDataRole.UserRole)
            if isinstance(folder_node, FolderNode):
                self.folder_selected.emit(folder_node)