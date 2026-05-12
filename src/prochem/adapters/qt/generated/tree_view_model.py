"""Custom Tree Model class for control window"""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import sys
from PySide6.QtCore import Qt, QModelIndex, QMimeData, QAbstractItemModel, QByteArray
from PySide6.QtWidgets import QApplication, QTreeView, QAbstractItemView, QMainWindow

__all__ = ["CustomTreeModel"]


class TreeItem:
    """
    Represents a node in a tree structure.
    
    Attributes:
        parent_item: The parent TreeItem instance, or None if this is a root node.
        item_data: The data associated with this tree item.
        child_items: A list of child TreeItem instances.
    """
    def __init__(self, data, parent=None):
        """
        Initializes a new item.
        
        Args:
            data: The data associated with this item.
            parent: The parent item, if any.
        
        Initializes the following object properties:
            self.parent_item: The parent item of this item.
            self.item_data: The data stored in this item.
            self.child_items: A list to store child items.
        
        Returns:
            None
        """
        self.parent_item = parent
        self.item_data = data 
        self.child_items = []

    def append_child(self, item):
        """
        Appends a child item to the internal list of child items.
        
        Args:
            item: The item to append as a child.
        
        Returns:
            None
        
        Initializes:
            self.child_items: A list to store child items.
        """
        self.child_items.append(item)

    def child(self, row):
        """
        Returns the child item at the given row.
        
        Args:
          self: The instance of the class.
          row: The row index of the child item to retrieve.
        
        Returns:
          The child item at the specified row.
        """
        return self.child_items[row]

    def child_count(self):
        """
        Counts the number of child items.
        
        Args:
         self: The instance of the class.
        
        Returns:
         int: The number of child items.
        """
        return len(self.child_items)

    def row(self):
        """
        Returns the row index of the item.
        
        If the item has a parent, it returns the index of the item within
        the parent's child items. Otherwise, it returns 0.
        
        Args:
          self: The instance of the class.
        
        Returns:
          int: The row index of the item.
        """
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def data(self, column):
        """
        Retrieves data from a specific column.
        
        Args:
            column: The index of the column to retrieve data from.
        
        Returns:
            The data at the specified column index, or None if the index is out of bounds.
        """
        try:
            return self.item_data[column]
        except IndexError:
            return None

    def insert_child(self, position, item):
        """
        Inserts a child item at a specified position within the parent's child items.
        
        Args:
            position: The index at which to insert the item.
            item: The item to insert.
        
        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        if position < 0 or position > len(self.child_items):
            return False
        item.parent_item = self # Устанавливаем нового родителя
        self.child_items.insert(position, item)
        return True

    def remove_child(self, item):
        """
        Removes a child item from the parent's list of child items.
        
        Args:
            item: The child item to remove.
        
        Returns:
            bool: True if the item was successfully removed, False otherwise.
        """
        if item in self.child_items:
            self.child_items.remove(item)
            return True
        return False

    def __repr__(self):
        """
        Represents the TreeItem object as a string.
        
        Args:
            self: The TreeItem instance.
        
        Returns:
            str: A string representation of the TreeItem, including its data and parent.
        """
        return f"TreeItem(data={self.item_data}, parent={self.parent_item})"

class CustomTreeModel(QAbstractItemModel):
    """
    Initializes a new instance of the TreeModel.
    
    Args:
        data: The initial data to populate the tree model.
        parent: The parent widget or object.
    
    Initializes the following object properties:
        column_count: An integer representing the fixed number of columns (set to 4).
        root_item: The root TreeItem containing the column headers ("ID", "V", "Name", "Type").
    
    Returns:
        None
    """
    def __init__(self, data=None, parent=None):
        """
        Initializes a new instance of the TreeModel.
        
        Args:
            data: The initial data to populate the tree model.
            parent: The parent widget or object.
        
        Initializes the following object properties:
            column_count: An integer representing the fixed number of columns (set to 4).
            root_item: The root TreeItem containing the column headers ("ID", "V", "Name", "Type").
        
        Returns:
            None
        """
        super().__init__(parent)
        self.column_count = 4 # Фиксируем количество столбцов
        self.root_item = TreeItem(["ID", "V", "Name", "Type"])
        if data is not None:
            self.append_data(data, self.root_item)

    def headerData(self, section, orientation, role=Qt.DisplayRole): # NOTE: overrided method 
        """
        Returns the header data for the given section, orientation, and role.
        
        Args:
         section: The section index.
         orientation: The orientation of the header (Qt.Horizontal or Qt.Vertical).
         role: The role of the header data (defaults to Qt.DisplayRole).
        
        Returns:
         The header data as a string or a list of strings.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["ID", "V", "Name", "Type"][section]
            else:
                return QString(f"Row {section + 1}")
        return super().headerData(section, orientation, role)

    def columnCount(self, parent=QModelIndex()): # NOTE: overrided method
        return self.column_count

    def rowCount(self, parent=QModelIndex()): # NOTE: overrided method
        parent_item = self.get_item(parent)
        return parent_item.child_count()

    def data(self, index, role=Qt.DisplayRole):
        """
        Retrieves the data for a given index and role.
        
        Args:
            index: The index of the item to retrieve data from.
            role: The role of the data to retrieve (defaults to Qt.DisplayRole).
        
        Returns:
            The data associated with the given index and role, or None if the index is invalid or the role is not Qt.DisplayRole.
        """
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        item = self.get_item(index)
        return item.data(index.column())

    def index(self, row, column, parent=QModelIndex()):
        """
        Returns the index for the item at the given row and column.
        
        Args:
            row: The row of the item.
            column: The column of the item.
            parent: The parent index.
        
        Returns:
            QModelIndex: The index for the item, or an invalid QModelIndex if the item does not exist.
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_item = self.get_item(parent)
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        """
        Returns the parent of the item at the given index.
        
        Args:
         index: The index of the item to get the parent of.
        
        Returns:
         A QModelIndex representing the parent of the item, or an invalid QModelIndex
         if the item has no parent or is the root item.
        """
        if not index.isValid():
            return QModelIndex()
        child_item = self.get_item(index)
        parent_item = child_item.parent_item
        if parent_item == self.root_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def get_item(self, index):
        """
        Retrieves an item at a given index.
        
        Args:
            index: The index to retrieve the item from.
        
        Returns:
            The item at the given index, or the root item if the index is invalid or points to nothing.
        """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_item

    def flags(self, index):
        """
        Returns the flags for a given index.
        
        Args:
         self: The object instance.
         index: The index for which to return flags.
        
        Returns:
         int: A bitwise OR of Qt flags representing the item's capabilities.
              Returns Qt.ItemIsEnabled | Qt.ItemIsDropEnabled if the index is invalid,
              otherwise returns Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled.
        """
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def supportedDropActions(self): # NOTE: overrided method
        return Qt.MoveAction

    def mimeData(self, indexes): # NOTE: overrided method 
        """
        Creates a QMimeData object for dragged items.
        
        This method prepares a QMimeData object containing information about the
        items being dragged, specifically those from the first column. It filters
        out the root item and stores the dragged items for later use.
        
        Args:
           indexes: A list of QModelIndex objects representing the selected items.
        
        Returns:
           QMimeData: A QMimeData object containing the drag data.
        
        Class Fields Initialized:
           self._dragged_items: A list to store the items being dragged. It's populated
               with the items from the selected indexes (excluding the root item)
               and used for drag and drop operations.
        """
        self._dragged_items = []
        for index in indexes:
             if index.column() == 0:
                item = self.get_item(index)
                if item is not self.root_item:
                   self._dragged_items.append(item)
        mime_data = QMimeData()
        mime_data.setData('application/x-qabstractitemmodeldatalist', QByteArray(b'marker'))
        return mime_data
    
    def dropMimeData(self, data, action, row, column, parent): # NOTE: overrided method
        """
        Handles the dropping of MIME data onto the model.
        
        This method processes the dropped data, moves items within the model,
        and updates the view accordingly. It handles cases where items are
        dropped onto themselves or their parent, and ensures proper removal
        and insertion of items to maintain model consistency.
        
        Args:
           data: The MIME data being dropped.
           action: The action being performed (e.g., move, copy).
           row: The row where the data is being dropped.
           column: The column where the data is being dropped.
           parent: The parent item where the data is being dropped.
        
        Returns:
           bool: True if the drop was successful, False otherwise.
        """
        old_row, new_row = -1, row
        if action == Qt.IgnoreAction:
            return True
        if not data.hasFormat('application/x-qabstractitemmodeldatalist'):
            return False

        moved_items = self._dragged_items
        if not moved_items:
            return False
       
        target_item = self.get_item(parent)
        first_parent = moved_items[0].parent_item

        if target_item in moved_items:
            self._dragged_items = []
            return False
        if target_item == first_parent.parent_item:
            self._dragged_items = []
            return False
        
        if parent.isValid():
            if target_item == first_parent:
                pass
            else:
                self._dragged_items = []
                return False

        for item in sorted(moved_items, key=lambda x: x.row(), reverse=True):
            old_parent = item.parent_item
            old_row = item.row()
            self.beginRemoveRows(self.createIndex(old_parent.row(), 0, old_parent) if old_parent != self.root_item else QModelIndex(), old_row, old_row)
            old_parent.remove_child(item)
            self.endRemoveRows()
        
        self.beginInsertRows(parent, new_row, new_row + len(moved_items) - 1)
        for item in moved_items:
            target_item.insert_child(new_row - 1 if new_row > old_row else new_row, item)
            new_row += 1
        self.endInsertRows()

        self._dragged_items = []
        return True

    def move_item(self, index, direction):
        """
        Moves an item within its parent based on the given direction.
        
        Args:
            index: The index of the item to move.
            direction: The direction to move the item ('up' or 'down').
        
        Returns:
            bool: True if the item was successfully moved, False otherwise.
        """
        item = self.get_item(index)
        parent = item.parent_item
        # if parent == self.root_item:
        #     return False
        row = item.row()
        new_row = row - 1 if direction == 'up' else row
        if (row == 0 and direction == 'up') or (row == parent.child_count() - 1 and direction == 'down'):
            return False

        self.beginRemoveRows(self.createIndex(parent.row(), 0, parent) if parent != self.root_item else QModelIndex(), row, row)
        parent.remove_child(item)
        self.endRemoveRows()

        self.beginInsertRows(self.createIndex(parent.row(), 0, parent) if parent != self.root_item else QModelIndex(), new_row, new_row)
        parent.insert_child(new_row, item)
        self.endInsertRows()

        #if direction == 'up':
        #    self.beginMoveRows(self.createIndex(parent.row(), 0, parent), row, row, self.createIndex(parent.row() - 1, 0, parent), row - 1)
        #else:
        #    self.beginMoveRows(self.createIndex(parent.row(), 0, parent), row, row, self.createIndex(parent.row() + 1, 0, parent), row + 1)
        #parent.remove_child(item)
        #parent.insert_child(row - 1 if direction == 'up' else row + 1, item)
        #self.endMoveRows()
        return True

    def append_data(self, data_list, parent):
        """
        Appends data to a tree structure recursively.
        
         This method iterates through a list of data items and their children,
         creating TreeItem objects and appending them to the specified parent item.
         It recursively calls itself to handle nested children.
        
         Parameters:
           data_list: A list of tuples, where each tuple contains the data for an item
             and a list of data for its children.
           parent: The parent TreeItem to which the new items will be appended.
        
         Returns:
           None
        """
        for item_data, children_data in data_list:
            parent_item = TreeItem(item_data, parent)
            parent.append_child(parent_item)
            if children_data:
                self.append_data(children_data, parent_item)


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("QAbstractItemModel D&D Example")
            self.setGeometry(100, 100, 400, 300)
            
            # Пример иерархических данных: [([ДанныеРодителя], [ДанныеДетей]), ...]
            # Каждый элемент данных - это кортеж из двух списков/кортежей
            data = [
                ([1, "V","Item 1", "Desc 1"], None),
                ([2, "I", "Item 2 (Parent)", "Desc 2"], [
                    ([1, "I", "Child 2.1", "Desc 2.1"], None),
                    ([2, "I", "Child 2.2", "Desc 2.2"], None),
                    ([3, "I", "Child 2.3", "Desc 2.3"], None),
                    ([4, "I", "Child 2.4", "Desc 2.4"], None)
                ]),
                ([3, "I", "Item 3", "Desc 3"], None),
                ([4, "I", "Item 4", "Desc 4"], None),
                ([5, "I", "Item 5", "Desc 5"], None),
                ([6, "I", "Item 6", "Desc 6"], None),
                ([7, "I", "Item 7", "Desc 7"], None)
            ]

            self.model = CustomTreeModel(data)
            self.tree_view = QTreeView()
            self.tree_view.setModel(self.model)
            
            # Настройка представления для D&D
            self.tree_view.setDragDropMode(QAbstractItemView.InternalMove)
            self.tree_view.setDragEnabled(True)
            self.tree_view.setAcceptDrops(True)
            self.tree_view.setDropIndicatorShown(True)
            self.tree_view.setDefaultDropAction(Qt.MoveAction)

            self.setCentralWidget(self.tree_view)
            print(self.model.move_item(self.model.index(1, 0), direction='up'))


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
