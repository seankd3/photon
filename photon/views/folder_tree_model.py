from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon
from photon.models import FolderNode

class FolderTreeModel(QAbstractItemModel):
    def __init__(self, root_folders: list[FolderNode], parent=None):
        super().__init__(parent)
        self._root_folders = root_folders

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            # Top-level items (root folders)
            if row < len(self._root_folders):
                return self.createIndex(row, column, self._root_folders[row])
            return QModelIndex()

        # Child items
        parent_node = parent.internalPointer()
        if isinstance(parent_node, FolderNode) and row < len(parent_node.children):
            child_node = parent_node.children[row]
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        if not isinstance(child_node, FolderNode):
            return QModelIndex()

        parent_node = child_node.parent
        if parent_node is None:
            return QModelIndex() # Top-level item has no parent in the model

        # Determine the row of the parent within its own parent's children or root folders
        if parent_node.parent is None: # If the parent is a root folder
            row = self._root_folders.index(parent_node)
        else:
            row = parent_node.parent.children.index(parent_node)

        return self.createIndex(row, 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            return len(self._root_folders)

        parent_node = parent.internalPointer()
        if isinstance(parent_node, FolderNode):
            return len(parent_node.children)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1 # Only one column for folder names

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> any:
        if not index.isValid():
            return None

        node = index.internalPointer()
        if not isinstance(node, FolderNode):
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return node.name
        elif role == Qt.ItemDataRole.DecorationRole:
            # You can add folder icons here
            return QIcon(":/icons/folder.png") # Placeholder for an icon
        elif role == Qt.ItemDataRole.UserRole:
            return node # Return the actual FolderNode object
        return None

    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        if not parent.isValid():
            return len(self._root_folders) > 0

        node = parent.internalPointer()
        if isinstance(node, FolderNode):
            return node.has_children
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "Folders"
        return None
