from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import pyqtSignal, QModelIndex
from .folder_tree_model import FolderTreeModel

class FolderTreeView(QTreeView):
    folder_selected = pyqtSignal(str)

    def __init__(self, catalog, parent=None):
        super().__init__(parent)
        self._catalog = catalog
        self._model = FolderTreeModel(self._catalog)
        self.setModel(self._model)
        self.setHeaderHidden(True)
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self, index: QModelIndex):
        if index.isValid():
            node = index.internalPointer()
            if node and not node.is_root:
                self.folder_selected.emit(node.path)

    def set_catalog(self, catalog):
        self._catalog = catalog
        self._model = FolderTreeModel(self._catalog)
        self.setModel(self._model)
        # Expand the root node to show initial folders
        self.expandToDepth(0)
