import logging
from prochem.adapters.qt.generated.oszicar import Ui_VROszicar, QMainWindow
from prochem.adapters.qt.graph.graph import VRGraph
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, QAbstractTableModel, QItemSelectionModel
import os
import traceback
import pandas as pd
logger = logging.getLogger(__name__)


class VRPdModel(QAbstractTableModel):
    """
    A model for displaying and managing data in a table format.
    
    Attributes:
        _data: The internal data storage for the model (DataFrame).
    """
    def __init__(self, data):
        """
        Initializes the model with the given data.
        
        Args:
            data: The data to be used by the model.
        
        Initializes the following fields:
            _data: The internal data storage for the model.
        
        Returns:
            None
        """
        QAbstractTableModel.__init__(self)
        self._data = data

    def refreshTable(self, df):
        """
        Refreshes the table model with a new DataFrame.
        
        Args:
          self: The object instance.
          df: The new DataFrame to populate the table model with.
        
        Initializes:
          _data: The DataFrame used as the data source for the table.
        
        Returns:
          None
        """
        self.beginResetModel()
        self._data = df
        self.endResetModel()

    def rowCount(self, parent=None):
        """
        Returns the number of rows in the data.
        
        Args:
           parent: Not used. Included for compatibility with certain frameworks.
        
        Returns:
           int: The number of rows in the underlying data structure.
        """
        return len(self._data.values)

    def columnCount(self, parent=None):
        """
        Returns the number of columns in the underlying data.
        
        Args:
          self: The instance of the class.
          parent: Not used. Included for compatibility with other methods.
        
        Returns:
          int: The number of columns in the data.
        """
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        """
        Retrieves the data at a given index for a specific role.
        
        Args:
            index: The index of the data to retrieve.
            role: The role of the data to retrieve (defaults to Qt.DisplayRole).
        
        Returns:
            str: The formatted data as a string if the index is valid and the role is Qt.DisplayRole, otherwise None.
        """
        if index.isValid():
            if role == Qt.DisplayRole:
                return f'{self._data.values[index.row()][index.column()]:f}'
        return None

    def headerData(self, col, orientation, role):
        """
        Returns the header data for a given column, orientation, and role.
        
        Args:
            col: The column index.
            orientation: The orientation of the header.
            role: The role of the header data.
        
        Returns:
            The header data as a string, or None if no data is available.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def insertColumn(self, column, place, parent=None):
        """
        Inserts a column into the model.
        
        Args:
            column: The column to insert.
            place: The index where the column should be inserted.
            parent: The parent item to which the column belongs. Defaults to None.
        
        Returns:
            None
        """
        self.beginInsertColumns(parent, place, place)
        self.endInsertColumns()

    def insertRow(self, row, place, parent=None):
        """
        Inserts a row into the model.
        
        Args:
            row: The row to insert.
            place: The index where the row should be inserted.
            parent: The parent item for the row (optional).
        
        Returns:
            None
        """
        self.beginInsertRows(parent, place, place)
        self.endInsertRows()

    def removeColumn(self, column, place, parent=None):
        """
        Removes a column from the model.
        
        Args:
            column: The column to remove.
            place: The index where the column is located.
            parent: The parent item (optional).
        
        Returns:
            None
        """
        self.beginRemoveColumns(parent, place, place)
        self.endRemoveColumns()

    def removeRow(self, column, place, parent=None):
        """
        Removes a row from the model.
        
        Args:
            column: The column the row belongs to.
            place: The index of the row to remove.
            parent: The parent item (if any).
        
        Returns:
            None
        """
        self.beginRemoveRows(parent, place, place)
        self.endRemoveRows()


class VROszicarProcessing:
    """
    Initializes the OszicarProcessor object.
    
    This constructor sets up the object by storing the directory path,
    steps, and POTIM value, listing files in the directory,
    and initializing data structures to hold OSZICAR file information.
    It then searches for OSZICAR files and, if found,
    forms a Pandas DataFrame from their data. If no OSZICAR files
    are found, it adds a message indicating this.
    
    Args:
     directory: The path to the directory containing OSZICAR files.
     printWindowObject: An object used for displaying messages.
     steps: The number of steps to process.
     POTIM: The POTIM value used in calculations.
    
    Attributes:
     __printWindow: An object used for displaying messages.
     directory: The path to the directory containing OSZICAR files.
     steps: The number of steps to process.
     directoryFiles: A list of files in the specified directory.
     oszicarFiles: A list of OSZICAR files found in the directory.
     data: A list to store data extracted from OSZICAR files.
     POTIM: The POTIM value used in calculations.
     oszicarDf: A Pandas DataFrame to store the processed OSZICAR data.
    
    Returns:
     None
    """
    def __init__(self, directory, printWindowObject, steps, POTIM):
        """
        Initializes the OszicarProcessor object.
        
        This constructor sets up the object by storing the directory path,
        steps, and POTIM value, listing files in the directory,
        and initializing data structures to hold OSZICAR file information.
        It then searches for OSZICAR files and, if found,
        forms a Pandas DataFrame from their data. If no OSZICAR files
        are found, it adds a message indicating this.
        
        Args:
         directory: The path to the directory containing OSZICAR files.
         printWindowObject: An object used for displaying messages.
         steps: The number of steps to process.
         POTIM: The POTIM value used in calculations.
        
        Attributes:
         __printWindow: An object used for displaying messages.
         directory: The path to the directory containing OSZICAR files.
         steps: The number of steps to process.
         directoryFiles: A list of files in the specified directory.
         oszicarFiles: A list of OSZICAR files found in the directory.
         data: A list to store data extracted from OSZICAR files.
         POTIM: The POTIM value used in calculations.
         oszicarDf: A Pandas DataFrame to store the processed OSZICAR data.
        
        Returns:
         None
        """
        self.__printWindow = printWindowObject
        self.directory, self.steps = directory, steps
        self.directoryFiles = os.listdir(directory)
        self.oszicarFiles, self.data, self.POTIM, self.oszicarDf = [], [], POTIM, pd.DataFrame()
        self.oszicarSearch()
        if self.oszicarFiles:
            self.formOszicarDataframe()
        else:
            self.addMessage('No OSZICAR files in directory.')

    def addMessage(self, message):
        """
        Adds a message to the print window.
        
        Args:
            message: The message to be added.
        
        Returns:
            None
        """
        self.__printWindow.addMessage(message)

    def oszicarSearch(self):
        """
        Searches for OSZICAR files within the directory files and sorts them.
        
        This method iterates through the directory files, identifies files containing 'OSZICAR',
        appends them to the oszicarFiles list, sorts the list, and then moves the first
        OSZICAR file to the end of the list.
        
        Args:
         self: The instance of the class.
        
        Attributes Initialized:
         oszicarFiles: A list to store the names of OSZICAR files found in the directory.
         
        Returns:
         None
        """
        for file in self.directoryFiles:
            if 'OSZICAR' in file:
                self.oszicarFiles.append(file)
        if self.oszicarFiles:
            self.oszicarFiles.sort()
        if 'OSZICAR' in self.oszicarFiles:
            self.oszicarFiles.append(self.oszicarFiles[0])
            self.oszicarFiles.pop(0)

    def oszicarParse(self, index):
        """
        Parses an OSZICAR file and appends the extracted data to the data list.
        
        Args:
            self:  The instance of the class.
            index: The index of the OSZICAR file to parse.
        
        Initializes the following class fields:
            self.data: A list to store the parsed data. Each element represents a row of data extracted from the OSZICAR file.
            self.directory: The directory containing the OSZICAR files.
            self.oszicarFiles: A list of OSZICAR filenames.
            self.POTIM: A list of potential time multipliers.
            self.steps: A list of step boundaries for applying time multipliers.
        
        Returns:
            None
        """
        if index > 0:
            startCount = self.data[-1][0]
        else:
            startCount = 0
        with open(f'{self.directory}/{self.oszicarFiles[index]}', 'r') as osz:
            while True:
                line = osz.readline()
                if not line:
                    break
                else:
                    if 'T' in line and 'mag' in line:
                        startCount += 1
                        addToData = [startCount]
                        addToData.extend(list(map(float, line.split()[2::2])))
                        self.data.append(list(addToData))
                        del addToData
        if self.POTIM:
            prevIndex = 0
            for index, POTIM in enumerate(self.POTIM):
                for dataIndex in range(prevIndex, self.steps[index]):
                    self.data[dataIndex][0] = self.data[dataIndex][0] * POTIM
                prevIndex = self.steps[index]
        self.data.pop(-1)
        self.data.pop(-1)

    def formOszicarDataframe(self):
        """
        Forms the Oszicar DataFrame.
        
        This method processes Oszicar files, parses their data, normalizes the data length,
        and constructs a Pandas DataFrame with specified columns.
        
        Args:
            self:  The instance of the class.
        
        Initializes the following class fields:
            oszicarFiles: A list of Oszicar file paths.
            data: A list of lists containing the parsed Oszicar data.
            oszicarDf: The Pandas DataFrame containing the processed Oszicar data.
        
        Returns:
            None. The method modifies the object's state by creating and assigning
            the DataFrame to the 'oszicarDf' attribute.
        """
        for index in range(len(self.oszicarFiles)):
            self.oszicarParse(index)
        self.oszicarFillToNormalLen()
        self.oszicarDf = pd.DataFrame(self.data, columns=['Time, fs', 'T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'])

    def oszicarFillToNormalLen(self):
        """
        Fills the data list to match the expected length based on the steps.
        
         This method adjusts the length of the `data` list to be equal to the last element
         of the `steps` list minus 2. It either removes elements from the end if the
         list is too long or appends placeholder elements if it's too short.
        
         Parameters:
          self: The instance of the class.
        
         Returns:
          None
        """
        if self.steps:
            while len(self.data) != self.steps[-1] - 2:
                if len(self.data) > self.steps[-1] - 2:
                    self.data.pop(-1)
                else:
                    self.data.append([None for _ in range(9)])


class VROszicar(Ui_VROszicar, QMainWindow):
    """
    A class for processing and visualizing OSZICAR data.
    
    This class handles loading, processing, and displaying data from OSZICAR files,
    allowing users to select columns, plot graphs, and save table data.
    """
    def __init__(self, directory, app, settings, visualWindowObject, openGLWindow, printWindowObject):
        """
        Initializes the VROszicar object.
        
        Args:
            directory: The directory containing the Oszicar data.
            app: The application object.
            settings: The settings object.
            visualWindowObject: The visual window object.
            openGLWindow: The OpenGL window object.
            printWindowObject: The print window object.
        
        Initializes the following object properties:
            self.__app: The application object.
            self.__settings: The settings object.
            self.__printWindow: The print window object.
            self.directory: The directory containing the Oszicar data.
            self.__parent: The visual window object.
            self.__openGLWindow: The OpenGL window object.
            self._selected_columns: A list to store selected columns. Initialized as an empty list.
            self.oszicarDf: The Oszicar DataFrame processed from the directory.
            self._model: The data model for the Oszicar table view.
            self._selectionModel: The selection model for the Oszicar table view.
        
        Returns:
            None
        """
        super(VROszicar, self).__init__()
        self.__app = app
        self.__settings = settings
        self.__printWindow = printWindowObject
        self.directory = directory
        location = self.__settings.oszicarWindowLocation
        self.__parent = visualWindowObject
        self.__openGLWindow = openGLWindow
        self.setupUi(self)
        self._selected_columns = []
        self.OszicarBuildGraphButton.setDisabled(True)
        if location is not None:
            self.move(location[0], location[1])
        self.oszicarDf = VROszicarProcessing(directory, printWindowObject, [], []).oszicarDf
        self._model = VRPdModel(self.oszicarDf)
        self.OszicarTableView.setModel(self._model)
        self._selectionModel = QItemSelectionModel(self._model)
        self.OszicarTableView.setSelectionModel(self._selectionModel)
        self.linkElementsWithFunctions()
        self.__parent.hide()
        self.__openGLWindow.hide()

    def addMessage(self, message):
        """
        Adds a message to the print window.
        
        Args:
            message: The message to be added.
        
        Returns:
            None
        """
        self.__printWindow.addMessage(message)

    def closeAll(self, event):
        """
        Closes the parent window and accepts the close event.
        
        Args:
         self: The instance of the class.
         event: The close event.
        
        Returns:
         None
        """
        self.__parent.close()
        event.accept()

    def closeEvent(self, event=QCloseEvent()):
        """
        Shows the parent and OpenGL window when the window is closed.
        
        Args:
         self: The instance of the class.
         event: The close event.
        
        Returns:
         None
        """
        self.__parent.show()
        self.__openGLWindow.show()
        event.accept()

    def linkElementsWithFunctions(self):
        """
        Connects UI elements to their corresponding functions.
        
        This method establishes connections between various UI elements (buttons, menu items, selection models)
        and the functions that should be executed when those elements are interacted with.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        self.OszicarCreateExcelButton.clicked.connect(self.saveTable)
        self.OszicarBack.clicked.connect(self.window().close)
        self.ABack.triggered.connect(self.window().close)
        self.AExit.triggered.connect(lambda: self.closeAll(QCloseEvent()))
        self._selectionModel.selectionChanged.connect(self.columnSelected)
        self.OszicarBuildGraphButton.clicked.connect(self.plotGraph)

    def columnSelected(self, selected, deselected):
        """
        Updates the list of selected columns based on user selection.
        
        This method handles column selection and deselection events, updating an internal
        list of selected column indices and enabling/disabling a button based on
        whether any columns are selected.
        
        Args:
         selected: The currently selected columns.
         deselected: The currently deselected columns.
        
        Attributes Initialized:
         _selected_columns: A list of integers representing the indices of the
          selected columns. This list is maintained in sorted order.
         OszicarBuildGraphButton: A button that is enabled when at least one column
          is selected and disabled otherwise.
        
        Returns:
         None
        """
        selected_list = selected.toList()
        deselected_list = deselected.toList()
        if selected_list and not selected_list[0].top() and selected_list[0].bottom() == len(self.oszicarDf) - 1 and selected_list[0].left() == selected_list[0].right():
            self._selected_columns.append(selected_list[0].left())
            self._selected_columns.sort()
        if deselected_list and self._selected_columns and not deselected_list[0].top():
            for column in deselected_list:
                self._selected_columns.remove(column.left())
        if self._selected_columns:
            self.OszicarBuildGraphButton.setEnabled(True)
        else:
            self.OszicarBuildGraphButton.setDisabled(True)

    def plotGraph(self):
        """
        Plots a graph based on the selected columns from the OSZICAR data.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            __graph (VRGraph): The VRGraph object containing the plotted graph.
            OszicarBuildGraphButton (QPushButton): Disables the button after graph construction.
        
        Returns:
            None
        """
        columns_indexes = [column.column() for column in self._selectionModel.selectedColumns()]
        df = pd.DataFrame(self.oszicarDf[self.oszicarDf.columns[0]])
        for index in columns_indexes:
            df[self.oszicarDf.columns[index]] = self.oszicarDf[self.oszicarDf.columns[index]]
        self.__graph = VRGraph(df)
        self.OszicarBuildGraphButton.setDisabled(True)
        self._selectionModel.clearSelection()

    def saveTable(self):
        """
        Saves the current table data to a file.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        
        Class Fields Initialized:
         None
        """
        tableDir = QFileDialog.getSaveFileName(None, caption='Save Table', filter="Excel (*.xlsx *.xls);;Csv (*.csv);;HTML (*.html)", selectedFilter="Excel (*.xlsx *.xls)")[0]
        if tableDir.endswith('.xlsx'):
            try:
                writer = pd.ExcelWriter(tableDir)
                self.oszicarDf.to_excel(writer, sheet_name='my_analysis', index=False)
                # Auto-adjust columns' width
                for column in self.oszicarDf:
                    columnWidth = max(self.oszicarDf[column].astype(str).map(len).max(), len(column))
                    colIdx = self.oszicarDf.columns.get_loc(column)
                    writer.sheets['my_analysis'].set_column(colIdx, colIdx, columnWidth)
                writer.close()
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except PermissionError:
                self.addMessage('Close Excel table before writing.') # title='OpenXslError')
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        elif tableDir.endswith('.csv'):
            try:
                self.oszicarDf.to_csv(tableDir, index=False)
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        elif tableDir.endswith('.html'):
            try:
                self.oszicarDf.to_html(tableDir, index=False, na_rep='')
                self.addMessage(f"File {tableDir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.addMessage('Caught exception: ' + traceback.format_exc())
