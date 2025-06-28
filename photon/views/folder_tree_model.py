from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from photon.catalog_reader import LightroomCatalogReader # Import the reader

class FolderTreeModel(QAbstractItemModel):
    def __init__(self, catalog, parent=None):
        super().__init__(parent)
        self._catalog = catalog
        self._root_node = FolderTreeNode(name="Catalog Root", path="", is_root=True)
        self._setup_model_data()

    def _setup_model_data(self):
        # Populate the root node with initial root folders from the catalog
        for folder_node in self._catalog.root_folders:
            self._root_node.add_child(FolderTreeNode(
                name=folder_node.name,
                path=folder_node.full_path,
                folder_id=folder_node.id,
                parent=self._root_node,
                has_unloaded_children=folder_node._has_unloaded_children # Pass this flag
            ))

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if role == Qt.DisplayRole:
            return node.name
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        child_node = parent_node.child(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        node = index.internalPointer()
        parent_node = node.parent()

        if parent_node == self._root_node:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        # Lazy loading: if children haven't been loaded, load them now
        if not parent_node.children_loaded and parent_node.has_unloaded_children:
            self._load_children(parent_node)

        return parent_node.child_count()

    def hasChildren(self, parent=QModelIndex()):
        if not parent.isValid():
            return self._root_node.child_count() > 0
        
        node = parent.internalPointer()
        return node.has_unloaded_children or node.child_count() > 0

    def _load_children(self, parent_node):
        # This method will be responsible for querying the catalog for children
        # and populating parent_node._children
        print(f"Loading children for: {parent_node.path} (ID: {parent_node.folder_id})")
        
        # Use LightroomCatalogReader to get children
        reader = LightroomCatalogReader()
        # Assuming the catalog_path is available in self._catalog
        # This might need to be passed down or accessed differently if not directly on catalog
        catalog_path = self._catalog.file_path 
        
        if catalog_path:
            children_nodes = reader.get_folder_children(catalog_path, parent_node.folder_id)
            
            self.beginInsertRows(self.index(parent_node.row(), 0, self.parent(self.createIndex(parent_node.row(), 0, parent_node))), 
                                 parent_node.child_count(), 
                                 parent_node.child_count() + len(children_nodes) - 1)
            
            for child_data in children_nodes:
                parent_node.add_child(FolderTreeNode(
                    name=child_data.name,
                    path=child_data.full_path,
                    folder_id=child_data.id,
                    parent=parent_node,
                    has_unloaded_children=child_data._has_unloaded_children
                ))
            self.endInsertRows()
        
        parent_node.children_loaded = True
        parent_node.has_unloaded_children = False # All children are now loaded


class FolderTreeNode:
    def __init__(self, name, path, folder_id=None, parent=None, is_root=False, has_unloaded_children=False):
        self.name = name
        self.path = path
        self.folder_id = folder_id
        self._parent = parent
        self._children = []
        self.is_root = is_root
        self.children_loaded = False # For lazy loading
        self.has_unloaded_children = has_unloaded_children # Indicates if there are more children in DB

        if parent and not is_root: # Only add to parent if not root and has a parent
            parent.add_child(self)

    def add_child(self, child):
        self._children.append(child)

    def child(self, row):
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def child_count(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent._children.index(self)
        return 0 # Root node or orphaned node