import traceback
import numpy as np
import pandas as pd
from analysis import (
    add_kinetic_energy_columns,
    add_velocity_columns,
    atom_labels,
    center_of_mass,
    coordinate_dataframe,
    distance_series,
    export_dataframe,
    time_axis,
    valence_angle,
)
from core.models import Calculation
from gui.processing_dev import Ui_VRProcessing, QMainWindow
from vasp.oszicar import VRPdModel
from graph.graph import VRGraph
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QFileDialog, QAbstractItemView
from PySide6.QtGui import QCloseEvent


class VRProcessing(Ui_VRProcessing, QMainWindow):
    """VaspReader processing class. Initialising of this class create a window for processing molecular dynamic results
       from VASP program. Use this with mainloop function, which work with events sent by window."""
    calc_const = 2 * 9.65 * 1000
    coordProjection = ('_x', '_y', '_z')
    directProjection = ('_dir_1', '_dir_2', '_dir_3')

    def __init__(self, app, settings, visualWindowObject, printWindowObject, openGlWindowObject, calculation, name, deleteAfterLeave):
        """
        Initializes the VRProcessing object.
        
        This constructor sets up the VRProcessing window, initializes data structures,
        and links UI elements to their corresponding functions. It handles data loading,
        DataFrame creation, and model setup for displaying and processing data.
        
        Args:
         app: The application object.
         settings: The settings object containing configuration parameters.
         visualWindowObject: The visual window object.
         printWindowObject: The print window object.
         openGlWindowObject: The OpenGL window object.
         calculation: Unified Calculation object.
         name: The name of the processing instance.
         deleteAfterLeave: A boolean indicating whether to delete the instance after leaving.
        
        Class Fields Initialized:
         self.__app: The application object.
         self.__settings: The settings object.
         self.__parent: The visual window object.
         self.__printWindow: The print window object.
         self.__openGl: The OpenGL window object.
         self.__calculation: Unified Calculation object.
         self._deleteAfterLeave: A boolean indicating whether to delete the instance after leaving.
         self._name: The name of the processing instance.
         self._selected_atoms: A list of selected atom names from the calculation data.
         self.__graph:  Initialized to None, likely intended for graph-related functionality.
         self._selected_columns: An empty list to store selected columns.
         self._masses:  Masses data obtained from the calculation data using the 'MASSES' key.
         self._selectedNames: Selected names obtained from the calculation data using the 'ID' key.
         self.columnsNames: A list of column names derived from self._selectedNames.
         self.coordColumns: A list of coordinate column names.
         self.directColumns: A list of direct column names.
         self.baseDf: A Pandas DataFrame representing the base data.
         self.vColumns: A list of velocity columns.
         self.eColumns: A list of energy columns.
         self.distanceCols: An empty list for distance columns.
         self.angleCols: An empty list for angle columns.
         self.weightmassCols: An empty list for weight/mass columns.
         self.sumCols: An empty list for sum columns.
         self.differenceCols: An empty list for difference columns.
         self.divideCols: An empty list for division columns.
         self.mainDf: A Pandas DataFrame representing the main data, initialized based on the presence of selected names.
         self._model: An instance of VRPdModel, initialized with self.mainDf.
         self._selectionModel: A QItemSelectionModel associated with the model.
        
        Returns:
         None
        """
        super(VRProcessing, self).__init__()
        self.__app = app
        self.__settings = settings
        location = self.__settings.processingWindowLocation
        self.__parent = visualWindowObject
        self.__printWindow = printWindowObject
        self.__openGl = openGlWindowObject
        self.setupUi(self)
        if location is not None:
            self.move(location[0], location[1])
        if not isinstance(calculation, Calculation):
            raise TypeError("VRProcessing expects core.models.Calculation.")
        if calculation.trajectory is None:
            raise ValueError("Calculation does not contain a trajectory.")
        self.__calculation = calculation
        self.__trajectory = calculation.trajectory
        self._deleteAfterLeave = deleteAfterLeave
        self._name = name
        self._selected_atom_ids = self._resolve_selected_atom_ids()

        self.__graph = None
        self._selected_columns = []
        self.columnsNames = atom_labels(self.__trajectory, self._selected_atom_ids)
        self._label_to_atom_id = dict(zip(self.columnsNames, self._selected_atom_ids, strict=True))
        self._masses = [
            self.__trajectory.atom_record(atom_id).mass
            for atom_id in self._selected_atom_ids
        ]
        self._selectedNames = self.columnsNames.copy()

        if self._selected_atom_ids:
            self.coordColumns = [name + self.coordProjection[j] for name in self.columnsNames for j in range(3)]
            self.directColumns = [name + self.directProjection[j] for name in self.columnsNames for j in range(3)]
            self.baseDf = self.formBasePandasDf()
            self.vColumns, self.eColumns = self.velocitiesAndEnergiesCalc()
            self.distanceCols, self.angleCols, self.weightmassCols, self.sumCols, self.differenceCols, self.divideCols = [], [], [], [], [], []
            self.mainDf = pd.DataFrame(self.baseDf)
            for v in self.vColumns:
                if v in self.mainDf:
                    del self.mainDf[v]
            for d in self.directColumns:
                if d in self.mainDf:
                    del self.mainDf[d]
            self.coordinatesDelete()
            self.refreshLists()
            self.oszicarCheckboxUnlock()
        else:
            self.coordColumns = []
            self.directColumns = []
            self.vColumns = []
            self.eColumns = []
            self.distanceCols, self.angleCols, self.weightmassCols, self.sumCols, self.differenceCols, self.divideCols = [], [], [], [], [], []
            self.baseDf = pd.DataFrame({"Time, fs": time_axis(self.__trajectory)})
            self.mainDf = pd.DataFrame(self.baseDf)
        self._model = VRPdModel(self.mainDf)
        self.ViewTable.setModel(self._model)
        self._selectionModel = QItemSelectionModel(self._model)
        self.ViewTable.setSelectionModel(self._selectionModel)
        self.linkElementsWithFunctions()
        self.__parent.hide()
        self.__openGl.hide()

    def _resolve_selected_atom_ids(self):
        selected = self.__calculation.properties.get("selected_atom_ids")
        if selected is None:
            return [record.atom_id for record in self.__trajectory.atom_registry]
        return [int(atom_id) for atom_id in selected]

    def addMessage(self, message, *args, **kwargs):
        """
        Adds a message to the print window.
        
        Args:
            message: The message to be added.
        
        Returns:
            None
        """
        self.__printWindow.addMessage(message)

    def linkElementsWithFunctions(self):
        """
        Connects UI elements to their corresponding functions.
        
        This method establishes connections between various UI elements (e.g., list items,
        radio buttons, buttons) and the functions that should be executed when those
        elements are interacted with. It effectively wires up the user interface to
        the application's logic.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        self.DCList.itemClicked.connect(self.DCListAction)
        self.DistanceRadio.toggled.connect(self.DCListClear)
        self.DCAddCol.clicked.connect(self.DCButtonClicked)
        self.DCAdded.activated.connect(self.DCChooseToRemove)
        self.DCRemoveCol.clicked.connect(lambda: self.removeColumns(self.DCAdded, self.DCRemoveCol))
        self.PMList.itemClicked.connect(self.PMListAction)
        self.MinusRadio.toggled.connect(self.PMListClear)
        self.PMAddCol.clicked.connect(self.PMButtonClicked)
        self.PMAdded.activated.connect(self.PMChooseToRemove)
        self.PMRemoveCol.clicked.connect(lambda: self.removeColumns(self.PMAdded, self.PMRemoveCol))
        self.AngleList.itemClicked.connect(self.AngleListAction)
        self.AngleAddCol.clicked.connect(self.AngleButtonClicked)
        self.AngleAdded.activated.connect(self.AngleChooseToRemove)
        self.AngleRemoveCol.clicked.connect(lambda: self.removeColumns(self.AngleAdded, self.AngleRemoveCol))
        self.DivideList.itemClicked.connect(self.DivideListAction)
        self.DivideAddCol.clicked.connect(self.DivideButtonClicked)
        self.DivideAdded.activated.connect(self.DivideChooseToRemove)
        self.DivideRemoveCol.clicked.connect(lambda: self.removeColumns(self.DivideAdded, self.DivideRemoveCol))
        self.AInclude_OSZICAR.toggled.connect(self.oszicarAction)
        self.ADel_coords_of_sel_atoms.toggled.connect(self.delCoordsAction)
        self.ADel_energy_of_sel_atoms.toggled.connect(self.delEnergyAction)
        self.CreateExcel.clicked.connect(self.saveTable)
        self.Back.clicked.connect(self.window().close)
        self.ABack.triggered.connect(self.window().close)
        self.AExit.triggered.connect(lambda: self.closeAll(QCloseEvent()))
        self._selectionModel.selectionChanged.connect(self.columnSelected)
        self.PlotGraphButton.clicked.connect(self.plotGraph)

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
        Shows the parent and OpenGL windows, destroys the processing window, and accepts the close event.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        self.__parent.show()
        self.__openGl.show()
        self.__parent.destroyProcessingWindow()
        event.accept()

    def refreshLists(self):
        """
        Clears and repopulates several lists used for displaying column names and data manipulation options.
        
        Args:
            self:  The instance of the class.
        
        Initializes the following object properties:
            DCList: A list widget displaying column names for a specific operation.
            PMList: A list widget displaying column names for primary manipulation.
            AngleList: A list widget displaying column names related to angles.
            DivideList: A list widget displaying column names for division operations.
            RenameSelect: A list widget displaying column names for renaming purposes.
        
        Returns:
            None
        """
        self.DCList.clear()
        self.PMList.clear()
        self.AngleList.clear()
        self.DivideList.clear()
        self.RenameSelect.clear()
        self.DCList.addItems(self.columnsNames)
        self.PMList.addItems(self.mainDf.columns[1:].tolist())
        self.AngleList.addItems(self.columnsNames)
        self.DivideList.addItems(self.columnsNames)
        self.RenameSelect.addItems(self.mainDf.columns[1:].tolist())

    def selectedDataForm(self, dict_name):
        """
        Returns a list of selected data based on the provided dictionary name.
        
        This method iterates through a range determined by 'ATOMNUMBER' in the internal
        calculation data and filters based on whether the corresponding atom is
        selected (indicated by 'Sel' in the _selected_atoms list).
        
        Args:
         dict_name: The name of the dictionary within the __calculation data to
           retrieve values from.
        
        Returns:
         list: A list of selected data values.
        """
        if dict_name == "MASSES":
            return self._masses.copy()
        if dict_name == "ID":
            return self._selectedNames.copy()
        return []

    @staticmethod
    def removeSubscriptInNames(names):
        """
        Removes underscores from names in a list.
        
        This method takes a list of strings and returns a new list where each string
        has all underscores removed.
        
        Args:
         names: A list of strings potentially containing underscores.
        
        Returns:
         A new list of strings with underscores removed from each element.
        """
        names = names.copy()
        renamed = []
        for name in names:
            renamed.append(''.join(name.split('_')))
        return renamed

    def formBasePandasDf(self):
        """
        Forms a base Pandas DataFrame from calculation data.
        
        Args:
            self: The instance of the class.
        
        Returns:
            pd.DataFrame: A Pandas DataFrame containing the processed calculation data.
        
        Class Fields Initialized:
            _selected_atoms: A list of selected atoms.
            directColumns: A list of column names for the direct coordinates.
            columnsNames: A list of names for the coordinate components.
            coordProjection: A list of coordinate projection values.
        """
        baseDf = coordinate_dataframe(
            self.__trajectory,
            self._selected_atom_ids,
            include_direct=True,
            include_cartesian=True,
            unwrap_direct=True,
        )
        if self._deleteAfterLeave:
            for column in self.directColumns:
                if column in baseDf:
                    baseDf[column] = baseDf[column].mask((baseDf[column] >= 1) | (baseDf[column] <= 0))
        return baseDf

    @staticmethod
    def atomAwayProcessing(direct, data):
        """
        Processes data relative to a direct input, adjusting a column based on differences.
        
        Args:
         direct: The original data column.
         data: The data to compare against the direct column.
        
        Returns:
         list: A new list representing the adjusted column.
        """
        column = direct.copy()
        for num, _ in enumerate(direct):
            exprFactor = round(data[num] - direct[num])
            if exprFactor:
                column[num] = column[num] + exprFactor
        return column

    def velocitiesAndEnergiesCalc(self):
        """
        Calculates velocities and energies for each column in the base DataFrame.
        
        This method computes the velocity and energy for each column based on the differences in x, y, and z coordinates, and then stores these values in new columns of the DataFrame. It also drops the first row and resets the index.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            baseDf: The DataFrame containing the calculated velocities and energies. New columns 'V_' + column and 'E_' + column are added for each column in columnsNames.
            vColumns: A list of column names for velocities.
            eColumns: A list of column names for energies.
        
        Returns:
            A tuple containing two lists:
                - vColumns: The list of velocity column names.
                - eColumns: The list of energy column names.
        """
        self.baseDf = add_velocity_columns(
            self.baseDf,
            self.__trajectory,
            self._selected_atom_ids,
            prefix="V",
        )
        vColumns = ['V_' + column for column in self.columnsNames]
        eColumns = []
        try:
            self.baseDf = add_kinetic_energy_columns(
                self.baseDf,
                self.__trajectory,
                self._selected_atom_ids,
                prefix="E",
            )
            eColumns = ['E_' + column for column in self.columnsNames]
        except ValueError as err:
            self.addMessage(str(err))
        return vColumns, eColumns

    def coordinatesDelete(self):
        """
        Deletes coordinate columns from the main DataFrame.
        
        Args:
            self: The instance of the class.
        
        The following class fields are initialized:
            - mainDf: The main DataFrame used for data manipulation.
            - coordColumns: A list of column names representing coordinates to be deleted.
        
        Returns:
            None
        """
        for coord in self.coordColumns:
            if coord in self.mainDf:
                del self.mainDf[coord]

    def directCurveChoose(self, first, second):
        """
        Calculates a weighted sum of differences between directional coefficients.
        
        This method computes the difference between directional coefficients for two
        input strings ('first' and 'second') across three directions ('_dir_1',
        '_dir_2', '_dir_3'). It then calculates a weighted sum of these differences
        using a predefined basis.
        
        Args:
         first: The first string identifier.
         second: The second string identifier.
        
        Returns:
         float: The weighted sum of the differences, representing the calculated
         value.
        """
        return np.zeros(3, dtype=np.float64)

    def divineOnPOTIM(self, column, isCOM=False):
        """
        Divines values in the base DataFrame based on POTIM values and a specified column.
        
        Args:
            column: The name of the column in the base DataFrame to modify.
            isCOM: A boolean flag indicating whether to apply a specific calculation for COM scenarios.
        
        Initializes:
            self.baseDf: The DataFrame being modified. This method updates values within this DataFrame based on the provided calculations.
            self.__calculation: A dictionary containing calculation parameters, including 'POTIM' and 'STEPS_LIST', used to determine the ranges and divisors for the calculation.
        
        Returns:
            None
        """
        if column not in self.baseDf:
            return None
        dt = np.concatenate([[np.nan], np.diff(time_axis(self.__trajectory))])
        dt[dt == 0] = np.nan
        self.baseDf[column] = self.baseDf[column] / dt

    def removeColumns(self, addedColsElement, removeElement):
        """
        Removes specified columns from the DataFrames and updates the lists and UI.
        
        Args:
         addedColsElement: The combo box element representing the added columns.
         removeElement: The button element used to remove columns.
        
        This method removes columns from both the base DataFrame (self.baseDf) and the main DataFrame (self.mainDf),
        depending on the selected column and the state of certain checkboxes. It also updates the corresponding lists
        (distanceCols, weightmassCols, sumCols, differenceCols, angleCols, divideCols, vColumns, eColumns, columnsNames)
        and refreshes the UI elements (combo boxes, table).
        """
        toDelete = addedColsElement.currentText()
        colsList = []
        if addedColsElement == self.DCAdded:
            colsList = self.distanceCols if toDelete in self.distanceCols else self.weightmassCols
        elif addedColsElement == self.PMAdded:
            colsList = self.sumCols if toDelete in self.sumCols else self.differenceCols
        elif addedColsElement == self.AngleAdded:
            colsList = self.angleCols
        elif addedColsElement == self.DivideAdded:
            colsList = self.divideCols

        if colsList == self.distanceCols or colsList == self.angleCols:
            self.baseDf.drop(columns=toDelete, inplace=True)
            self.mainDf.drop(columns=toDelete, inplace=True)
            colsList.remove(toDelete)
            self.addMessage(f'Column {toDelete} has been removed.')
        elif colsList == self.sumCols or colsList == self.differenceCols:
            self.baseDf.drop(columns=toDelete, inplace=True)
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDelete, inplace=True)
            colsList.remove(toDelete)
            self.eColumns.remove(toDelete)
            self.addMessage(f'Column {toDelete} has been removed.')
        elif colsList == self.divideCols:
            elements = toDelete.split('_')
            atoms = []
            for num, element in enumerate(elements):
                if num % 2 == 0:
                    atoms.append(element)
                else:
                    atoms[-1] = atoms[-1] + '_' + element
            toDeleteCols = [f'Evib_{toDelete}', f'Erot_{toDelete}']
            for atom in atoms:
                toDeleteCols.extend([f'Evib_{toDelete}({atom})', f'Erot_{toDelete}({atom})'])
            self.baseDf.drop(columns=toDeleteCols, inplace=True)
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDeleteCols, inplace=True)
            colsList.remove(toDelete)
            [self.eColumns.remove(value) for value in toDeleteCols]
            self.addMessage(f'Columns divided to vibrational and rotational energy {toDelete} have been removed.')
        else:
            toDeleteList = [f'{toDelete}_x', f'{toDelete}_y', f'{toDelete}_z', f'V{toDelete}', f'E{toDelete}']
            self.baseDf.drop(columns=toDeleteList, inplace=True)
            toDeleteList.remove(f'V{toDelete}')
            if not self.ADel_coords_of_sel_atoms.isChecked():
                self.mainDf.drop(columns=toDeleteList, inplace=True) if not self.ADel_energy_of_sel_atoms.isChecked() else self.mainDf.drop(columns=toDeleteList[:3], inplace=True)
            else:
                if not self.ADel_energy_of_sel_atoms.isChecked():
                    self.mainDf.drop(columns=toDeleteList[-1], inplace=True)
            self.vColumns.remove(f'V{toDelete}')
            self.addMessage(f'Column {self.eColumns[-1]} and linked columns have been removed.')
            self.eColumns.remove(f'E{toDelete}')
            self.columnsNames.remove(toDelete)
            self.weightmassCols.remove(toDelete)
        addedColsElement.removeItem(addedColsElement.currentIndex())
        if not addedColsElement.count():
            addedColsElement.setDisabled(True)
            removeElement.setDisabled(True)
        self.refreshLists()
        self._model.refreshTable(self.mainDf)

    def DCListAction(self, element):
        """
        Updates the UI based on the selected items in the DCList.
        
        Args:
           self: The instance of the class.
           element: The currently selected item in the list.
        
        Initializes the following object properties:
           DCAddCol: A button enabling/disabling based on the number of selected columns.
           DCSelected: A text field displaying the comma-separated text of selected columns.
        
        Returns:
           None
        """
        selectedColumns = self.DCList.selectedItems()
        listSize = len(selectedColumns)

        if listSize == 2:
            self.DCAddCol.setEnabled(True)
        elif listSize < 2:
            self.DCAddCol.setDisabled(True)

        if self.DistanceRadio.isChecked():
            if listSize > 2:
                self.DCList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.DCSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    def DCListClear(self, *args):
        """
        Clears the selected data in the DCList and DCSelected lists, and disables the Add Column button.
        
        Args:
            self: The instance of the class.
        
        Initializes the following object properties:
            DCSelected: A list to store selected data. Cleared in this method.
            DCList: An object representing the list. Selection is cleared in this method.
            DCAddCol: A button for adding columns. Disabled in this method.
        
        Returns:
            None
        """
        self.DCSelected.clear()
        self.DCList.clearSelection()
        self.DCAddCol.setDisabled(True)

    def DCButtonClicked(self):
        """
        Calculates distance or COM based on the selected radio button.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None.
        
        
        Class Fields Initialized:
         - DistanceRadio: A radio button that determines the calculation type.
         - COMCalculate: A method to calculate the Center of Mass.
         - DistanceCalculate: A method to calculate the distance.
        """
        if self.DistanceRadio.isChecked():
            self.DistanceCalculate()
        else:
            self.COMCalculate()

    def DistanceCalculate(self):
        """
        Calculates the distance between two selected columns and adds it as a new column to the DataFrames.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        
        Fields Initialized:
            baseDf: DataFrame to store the calculated distance.
            mainDf: DataFrame to store the calculated distance.
            distanceCols: List to store the names of the added distance columns.
        """
        first, second = sorted([item.text() for item in self.DCList.selectedItems()])
        if f'{first}--{second}' in self.baseDf:
            self.addMessage('Column has already been added!', result='FAILED', cause='Column has already been added')
            self.DCListClear()
        else:
            first_id = self._label_to_atom_id[first]
            second_id = self._label_to_atom_id[second]
            self.baseDf[f'{first}--{second}'] = distance_series(
                self.__trajectory,
                first_id,
                second_id,
                use_pbc=True,
            )
            self.mainDf[f'{first}--{second}'] = self.baseDf[f'{first}--{second}']

            self.distanceCols.append(f'{first}--{second}')
            if not self.DCAdded.isEnabled():
                self.DCAdded.setEnabled(True)
            self.DCAdded.addItem(f'{first}--{second}')
            if not self.DCRemoveCol.isEnabled():
                self.DCRemoveCol.setEnabled(True)
            self.refreshLists()
            self.DCListClear()
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Column {first}--{second} has been added.')

    def COMCalculate(self, atomsList=None):
        """
        Calculates the center of mass (COM) for selected atoms and adds the resulting data to the DataFrame.
        
        Args:
            atomsList: An optional list of atom names. If None, the method uses the selected items from the DCList.
        
        Initializes the following class fields:
            baseDf: The base DataFrame used for calculations.
            vColumns: A list of velocity column names.
            eColumns: A list of energy column names.
            columnsNames: A list of column names.
            weightmassCols: A list of weight/mass column names.
            DCAdded: A combo box for added columns.
        
        Returns:
            None. The method modifies the class's DataFrames and lists in place.
        """
        if atomsList is None:
            weightmasses = sorted([item.text() for item in self.DCList.selectedItems()])
        else:
            weightmasses = atomsList
        columnName = 'cm_' + '_'.join(weightmasses)
        if f'E{columnName}' not in self.eColumns:
            atom_ids = [self._label_to_atom_id[name] for name in weightmasses]
            try:
                cm_values = center_of_mass(self.__trajectory, atom_ids)
            except ValueError as err:
                self.addMessage(str(err))
                self.DCListClear()
                return
            masses = np.asarray([self.__trajectory.atom_record(atom_id).mass for atom_id in atom_ids], dtype=np.float64)
            summaryMass = float(np.sum(masses))
            for index, proj in enumerate(['_x', '_y', '_z']):
                self.baseDf[f"{columnName}{proj}"] = cm_values[:, index]
            self.vColumns.append(f'V{columnName}')
            self.eColumns.append(f'E{columnName}')
            times = time_axis(self.__trajectory)
            dt = np.diff(times)
            dt[dt == 0] = np.nan
            speeds = np.linalg.norm(np.diff(cm_values, axis=0), axis=1) / dt * 1000.0
            self.baseDf[self.vColumns[-1]] = np.concatenate([[np.nan], speeds])
            self.baseDf[self.eColumns[-1]] = (self.baseDf[self.vColumns[-1]]) ** 2 * summaryMass / self.calc_const
            if not self.ADel_coords_of_sel_atoms.isChecked():
                for proj in ['_x', '_y', '_z']:
                    self.mainDf.insert(len(self.mainDf.columns), columnName + proj, self.baseDf[columnName + proj])
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.insert(len(self.mainDf.columns), self.eColumns[-1], self.baseDf[self.eColumns[-1]])
            self.refreshLists()
            self.DCListClear()
            self.weightmassCols.append(columnName)
            self.DCAdded.addItem(columnName)

            if not self.DCAdded.isEnabled():
                self.DCAdded.setEnabled(True)
            if not self.DCRemoveCol.isEnabled():
                self.DCRemoveCol.setEnabled(True)
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Column {self.eColumns[-1]} has been added.')
        else:
            self.addMessage('Column has already been added!', result='FAILED', cause='Column has already been added')
            self.DCListClear()

    def DCChooseToRemove(self, *args):
        """
        Enables the 'DCRemoveCol' button.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        self.DCRemoveCol.setEnabled(True)

    def PMListAction(self, element):
        """
        Updates the UI based on the selected items in a list.
        
        Handles enabling/disabling a button based on the number of selected items,
        and updates a text field with the selected item texts.  Also handles deselection
        of items based on a radio button state.
        
        Args:
            self:  The instance of the class.
            element: The currently selected item (not directly used for logic, but passed as an argument).
        
        Returns:
            None
        """
        selectedColumns = self.PMList.selectedItems()
        listSize = len(selectedColumns)

        if listSize == 2:
            self.PMAddCol.setEnabled(True)
        elif listSize < 2:
            self.PMAddCol.setDisabled(True)

        if self.MinusRadio.isChecked():
            if listSize > 2:
                self.PMList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.PMSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    def PMListClear(self, *args):
        """
        Clears the selected items from the PMSelected list and disables the PMAddCol button.
         
         :param self: The instance of the class.
         
         :returns: None.
         
         Fields initialized:
         - PMSelected: A list to store selected items. Cleared by this method.
         - PMList: An object representing the list. Its selection is cleared.
         - PMAddCol: A button object. Disabled by this method.
        """
        self.PMSelected.clear()
        self.PMList.clearSelection()
        self.PMAddCol.setDisabled(True)

    def PMButtonClicked(self):
        """
        Calculates either the sum or difference based on the selected radio button.
        
        Args:
         self: The instance of the class.
        
        Initializes:
         None
        
        Returns:
         None
        """
        if self.MinusRadio.isChecked():
            self.DifferenceCalculate()
        else:
            self.SumCalculate()

    def SumCalculate(self):
        """
        Calculates the sum of selected items and adds it as a new column to the DataFrame.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            self.sumCols: A list to store the names of the calculated sum columns.
            self.baseDf: The base DataFrame where the sum column is initially created.
            self.mainDf: The main DataFrame where the sum column is copied if ADel_energy_of_sel_atoms is not checked.
            self.PMAdded: A list widget to display the added columns.
            self.eColumns: A list to store the names of energy columns.
        
        Returns:
            None
        """
        sumNames = sorted([item.text() for item in self.PMList.selectedItems()])
        sumStr = 'Sm_' + '_'.join(sumNames)
        if sumStr not in self.sumCols:
            dfColumns = [f'{name}' for name in sumNames]
            self.baseDf[sumStr] = self.baseDf[dfColumns[0]]
            for col in dfColumns[1:]:
                self.baseDf[sumStr] += self.baseDf[col]
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf[sumStr] = self.baseDf[sumStr]
            self.sumCols.append(sumStr)
            self.PMAdded.addItem(sumStr)
            self.refreshLists()
            self.PMListClear()
            if not self.PMAdded.isEnabled():
                self.PMAdded.setEnabled(True)
            if not self.PMRemoveCol.isEnabled():
                self.PMRemoveCol.setEnabled(True)
            self.eColumns.append(sumStr)
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Column {sumStr} has been added.')
        else:
            self.addMessage('Column has already been added!')

    def DifferenceCalculate(self):
        """
        Calculates the difference between two selected columns and adds it as a new column.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            baseDf: DataFrame to store the base calculations.
            mainDf: DataFrame to display the results.
            differenceCols: List to store the names of the difference columns.
            eColumns: List to store the names of the energy columns.
        
        Returns:
            None
        """
        first, second = [item.text() for item in self.PMList.selectedItems()]
        differenceStr = 'Df_' + '-'.join([first, second])
        if differenceStr not in self.differenceCols:
            self.baseDf[differenceStr] = self.baseDf[first] - self.baseDf[second]
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf[differenceStr] = self.baseDf[differenceStr]
            self.differenceCols.append(differenceStr)
            self.PMAdded.addItem(differenceStr)
            self.refreshLists()
            self.PMListClear()
            if not self.PMAdded.isEnabled():
                self.PMAdded.setEnabled(True)
            if not self.PMRemoveCol.isEnabled():
                self.PMRemoveCol.setEnabled(True)
            self._model.refreshTable(self.mainDf)
            self.eColumns.append(differenceStr)
            self.addMessage(f'Column {differenceStr} has been added.')
        else:
            self.addMessage('Column has already been added!')

    def PMChooseToRemove(self, *args):
        """
        Enables the PMRemoveCol widget.
        
        Args:
            self: The instance of the class.
        
        Initializes the following class fields:
            PMRemoveCol: A widget used to remove a column. It is enabled by this method.
        
        Returns:
            None
        """
        self.PMRemoveCol.setEnabled(True)

    def AngleListAction(self, element):
        """
        Updates the enabled state of related UI elements based on the number of selected items in the AngleList.
        
        Args:
            self:  The instance of the class.
            element: The currently selected element in the list (not directly used for logic, but part of the signal/slot connection).
        
        Initializes the following object properties:
            AngleAddCol: A QPushButton object representing the "Add Column" button. Its enabled state is updated based on the number of selected columns.
            AnglePlaneXY: A QPushButton object representing the XY plane option. Its enabled state is updated based on the number of selected columns.
            AnglePlaneYZ: A QPushButton object representing the YZ plane option. Its enabled state is updated based on the number of selected columns.
            AnglePlaneZX: A QPushButton object representing the ZX plane option. Its enabled state is updated based on the number of selected columns.
            AngleSelected: A QLabel object that displays the comma-separated text of the selected columns.
        
        Returns:
            None
        """
        selectedColumns = self.AngleList.selectedItems()
        listSize = len(selectedColumns)

        if listSize == 0:
            self.AngleAddCol.setDisabled(True)
        elif listSize == 1:
            self.AnglePlaneXY.setEnabled(True)
            self.AnglePlaneYZ.setEnabled(True)
            self.AnglePlaneZX.setEnabled(True)
            self.AngleAddCol.setEnabled(True)
        elif listSize == 2:
            self.AnglePlaneXY.setDisabled(True)
            self.AnglePlaneYZ.setDisabled(True)
            self.AnglePlaneZX.setDisabled(True)
            self.AngleAddCol.setDisabled(True)
        elif listSize == 3:
            self.AngleAddCol.setEnabled(True)

        if listSize > 3:
            self.AngleList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.AngleSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    def AngleListClear(self, *args):
        """
        Clears the selected angles and disables the 'Add Column' button.
        
        Args:
         self: The instance of the class.
        
        Initializes:
         AngleSelected: A list to store the selected angles. Cleared in this method.
         AngleList: A widget representing the list of angles. Selection is cleared.
         AngleAddCol: A button to add a column. Disabled after clearing the selection.
        
        Returns:
         None
        """
        self.AngleSelected.clear()
        self.AngleList.clearSelection()
        self.AngleAddCol.setDisabled(True)

    def AngleButtonClicked(self):
        """
        Calculates angles based on the number of selected items.
        
        If one item is selected, performs a standard angle calculation.
        If three items are selected, performs a valence angle calculation.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        colsNumber = len(self.AngleList.selectedItems())
        if colsNumber == 1:
            self.AngleCalculate()
        elif colsNumber == 3:
            self.ValenceAngleCalculate()

    def AngleCalculate(self):
        """
        Calculates and adds an angle column to the DataFrame based on selected atom and plane.
        
        Args:
            self:  The instance of the class.
        
        Initializes:
            self.angleCols: A list to store the names of added angle columns.
            self.baseDf: The base DataFrame used for calculations.
            self.mainDf: The main DataFrame to which the angle column is added.
            self.AngleAdded: A combo box displaying added angle columns.
            self.AngleRemoveCol: A button to remove added columns.
        
        Returns:
            None
        """
        atom = self.AngleList.selectedItems()[0].text()
        angle, plane = [], ''
        if self.AnglePlaneXY.isChecked():
            plane = 'xy'
        elif self.AnglePlaneYZ.isChecked():
            plane = 'yz'
        else:
            plane = 'zx'
        if f'{atom}_{plane}' not in self.angleCols:
            self.baseDf[f'{atom}_{plane}'] = np.degrees(np.arccos(np.sqrt(self.baseDf[f'{atom}_{plane[0]}'].diff() ** 2 + self.baseDf[f'{atom}_{plane[1]}'].diff() ** 2) / np.sqrt(self.baseDf[f'{atom}_x'].diff() ** 2 + self.baseDf[f'{atom}_y'].diff() ** 2 + self.baseDf[f'{atom}_z'].diff() ** 2)))
            self.mainDf.insert(len(self.mainDf.columns), f'{atom}_{plane}', self.baseDf[f'{atom}_{plane}'])
            self.angleCols.append(f'{atom}_{plane}')
            self.AngleAdded.addItem(f'{atom}_{plane}')
            if not self.AngleAdded.isEnabled():
                self.AngleAdded.setEnabled(True)
            if not self.AngleRemoveCol.isEnabled():
                self.AngleRemoveCol.setEnabled(True)
            self.refreshLists()
            self.AngleListClear()
            self._model.refreshTable(self.mainDf)
            self.addMessage(f"Column {atom}_{plane} has been added.")
        else:
            self.addMessage('Column already exists.')

    def ValenceAngleCalculate(self):
        """
        Calculates the valence angle between three selected atoms and adds it as a new column to the DataFrame.
        
        Args:
            self: The instance of the class.
        
        Initializes the following class fields:
            baseDf: DataFrame used for intermediate calculations.
            mainDf: DataFrame that stores the final results.
            angleCols: List to keep track of added angle columns.
            AngleAdded: A QComboBox widget to display added angles.
            AngleRemoveCol: A button to remove added columns.
            AnglePlaneXY: A button to set the angle plane to XY.
            AnglePlaneYZ: A button to set the angle plane to YZ.
            AnglePlaneZX: A button to set the angle plane to ZX.
        
        Returns:
            None
        """
        atoms = [item.text() for item in self.AngleList.selectedItems()]
        if f'{atoms[0]}-{atoms[1]}-{atoms[2]}' not in self.angleCols:
            atom_ids = [self._label_to_atom_id[atom] for atom in atoms]
            self.baseDf[f'{atoms[0]}-{atoms[1]}-{atoms[2]}'] = np.round(
                valence_angle(
                    self.__trajectory,
                    atom_ids[0],
                    atom_ids[1],
                    atom_ids[2],
                    use_pbc=True,
                ),
                2,
            )

            self.mainDf.insert(len(self.mainDf.columns), f'{atoms[0]}-{atoms[1]}-{atoms[2]}', self.baseDf[f'{atoms[0]}-{atoms[1]}-{atoms[2]}'])
            self.angleCols.append(f'{atoms[0]}-{atoms[1]}-{atoms[2]}')
            self.AngleAdded.addItem(f'{atoms[0]}-{atoms[1]}-{atoms[2]}')
            if not self.AngleAdded.isEnabled():
                self.AngleAdded.setEnabled(True)
            if not self.AngleRemoveCol.isEnabled():
                self.AngleRemoveCol.setEnabled(True)
            self.refreshLists()
            self.AngleListClear()
            if not self.AnglePlaneXY.isEnabled():
                self.AnglePlaneXY.setEnabled(True)
                self.AnglePlaneYZ.setEnabled(True)
                self.AnglePlaneZX.setEnabled(True)
            self._model.refreshTable(self.mainDf)
            self.addMessage(f"Column {atoms[0]}-{atoms[1]}-{atoms[2]} has been added.")
        else:
            self.addMessage('Column already exists.')

    def AngleChooseToRemove(self, *args):
        """
        Enables the AngleRemoveCol widget.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        self.AngleRemoveCol.setEnabled(True)

    def DivideListAction(self, element):
        """
        Divides a list based on selected items and updates the UI.
        
         This method handles the logic for dividing a list based on user selections.
         It enables or disables a button based on the number of selected items,
         and updates a text field with the selected column names. It also deselects
         items if more than two are selected.
        
         Parameters:
         self: The instance of the class.
         element: The currently selected element (not directly used in the logic, but part of the signal/slot connection).
        
         Returns:
         None
        """
        selectedColumns = self.DivideList.selectedItems()
        listSize = len(selectedColumns)

        if listSize > 1 and not self.DivideAddCol.isEnabled():
            self.DivideAddCol.setEnabled(True)
        elif listSize == 1 and self.DivideAddCol.isEnabled():
            self.DivideAddCol.setDisabled(True)

        if listSize > 2:
            self.DivideList.setCurrentItem(element, QItemSelectionModel.Deselect)
        self.DivideSelected.setText(', '.join([selectedColumn.text() for selectedColumn in selectedColumns]))

    def DivideListClear(self, *args):
        """
        Clears the selected items in the division list and disables the add column button.
        
         This method resets the selection state of the division list and prepares it for new selections.
        
         Parameters:
          self - The instance of the class.
        
         Returns:
          None
         
         Class Fields Initialized:
          - DivideSelected: A list to store the selected items for division. Cleared in this method.
          - DivideList: An object representing the division list. Its selection is cleared.
          - DivideAddCol: A button to add columns. Disabled after clearing the selection.
        """
        self.DivideSelected.clear()
        self.DivideList.clearSelection()
        self.DivideAddCol.setDisabled(True)

    def DivideButtonClicked(self):
        """
        Calculates the division result based on the current operands.
        
        This method triggers the internal calculation logic for division.
        
        Args:
         self:  The instance of the class.
        
        Returns:
         None.
        """
        self.DivideCalculate()

    def DivideCalculate(self):
        """
        Calculates vibrational and rotational energies based on selected atoms and adds them as new columns to the DataFrame.
        
        Parameters:
        self - The instance of the class.
        
        Initializes the following class fields:
        - `baseDf`: DataFrame used for calculations.
        - `columnsNames`: List of column names.
        - `divideCols`: List to store names of divided columns.
        - `eColumns`: List to store names of energy columns.
        - `mainDf`: Main DataFrame to which results are added.
        - `_masses`: List of masses used in calculations.
        - `calc_const`: Constant used in calculations.
        
        Returns:
        None
        """
        temporaryCols = []
        atoms = sorted([item.text() for item in self.DivideList.selectedItems()])
        colName = '_'.join(atoms)
        if colName not in self.divideCols:
            self.COMCalculate(atoms)
            for atom in atoms:
                self.baseDf[f'cm_{colName}--{atom}'] = np.sqrt((self.baseDf[f'cm_{colName}_x'] - self.baseDf[f'{atom}_x']) ** 2 + (self.baseDf[f'cm_{colName}_y'] - self.baseDf[f'{atom}_y']) ** 2 + (self.baseDf[f'cm_{colName}_z'] - self.baseDf[f'{atom}_z']) ** 2)
                temporaryCols.append(f'cm_{colName}--{atom}')
            for atom in atoms:
                self.baseDf[f'Vvib_{colName}({atom})'] = self.baseDf[f'cm_{colName}--{atom}'].diff() * 1000
                self.divineOnPOTIM(f'Vvib_{colName}({atom})', True)
                self.baseDf[f'Evib_{colName}({atom})'] = self.baseDf[f'Vvib_{colName}({atom})'] ** 2 * self._masses[self.columnsNames.index(atom)] / self.calc_const
                self.baseDf[f'Vsum_{colName}({atom})'] = np.sqrt((self.baseDf[f'{atom}_x'].diff() - self.baseDf[f'cm_{colName}_x'].diff()) ** 2 + (self.baseDf[f'{atom}_y'].diff() - self.baseDf[f'cm_{colName}_y'].diff()) ** 2 + (self.baseDf[f'{atom}_z'].diff() - self.baseDf[f'cm_{colName}_z'].diff()) ** 2) * 1000
                self.divineOnPOTIM(f'Vsum_{colName}({atom})', True)
                self.baseDf[f'Vrot_{colName}({atom})'] = np.sqrt((self.baseDf[f'Vsum_{colName}({atom})'] ** 2 - self.baseDf[f'Vvib_{colName}({atom})'] ** 2).clip(lower=0))
                self.baseDf[f'Erot_{colName}({atom})'] = self.baseDf[f'Vrot_{colName}({atom})'] ** 2 * self._masses[self.columnsNames.index(atom)] / self.calc_const
                self.eColumns.extend([f'Evib_{colName}({atom})', f'Erot_{colName}({atom})'])
                temporaryCols.extend([f'Vvib_{colName}({atom})', f'Vsum_{colName}({atom})', f'Vrot_{colName}({atom})'])
                if not self.ADel_energy_of_sel_atoms.isChecked():
                    self.mainDf.insert(len(self.mainDf.columns), f'Evib_{colName}({atom})', self.baseDf[f'Evib_{colName}({atom})'])
                    self.mainDf.insert(len(self.mainDf.columns), f'Erot_{colName}({atom})', self.baseDf[f'Erot_{colName}({atom})'])
            self.baseDf[f'Evib_{colName}'] = sum(self.baseDf[f'Evib_{colName}({atom})'] for atom in atoms)
            self.baseDf[f'Erot_{colName}'] = sum(self.baseDf[f'Erot_{colName}({atom})'] for atom in atoms)
            self.baseDf.drop(columns=temporaryCols, inplace=True)
            temporaryCols.clear()
            self.eColumns.extend([f'Evib_{colName}', f'Erot_{colName}'])
            if not self.ADel_energy_of_sel_atoms.isChecked():
                self.mainDf.insert(len(self.mainDf.columns), f'Evib_{colName}', self.baseDf[f'Evib_{colName}'])
                self.mainDf.insert(len(self.mainDf.columns), f'Erot_{colName}', self.baseDf[f'Erot_{colName}'])

            self.divideCols.append(colName)
            self.DivideAdded.addItem(colName)
            if not self.DivideAdded.isEnabled():
                self.DivideAdded.setEnabled(True)
            if not self.DivideRemoveCol.isEnabled():
                self.DivideRemoveCol.setEnabled(True)
            self.refreshLists()
            self.DivideListClear()
            self._model.refreshTable(self.mainDf)
            self.addMessage(f'Columns divided to vibrational and rotational energy {colName} have been added.')
        else:
            self.addMessage('Column already exists.')

    def DivideChooseToRemove(self, *args):
        """
        Enables the DivideRemoveCol widget.
        
        Args:
         self: The instance of the class.
        
        Returns:
         None
        """
        self.DivideRemoveCol.setEnabled(True)

    def renameColumnChoose(self):
        """
        Renames a selected column by populating a text field with its name.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            None
        
        Returns:
            None
        """
        colName = self.RenameSelect.currentText()
        if colName:
            self.RenameLine.setText(colName)
            self.RenameLine.setEnabled(True)

    def renameColumnAction(self):
        """
        Enables or disables the Rename button based on whether the selected column name 
            differs from the text in the Rename line edit.
        
            Parameters:
                self: The instance of the class.
        
            Class Fields Initialized:
                RenameButton: A QPushButton object representing the rename button. Its enabled state is modified.
                RenameLine: A QLineEdit object holding the new column name. Its text is used for comparison.
                RenameSelect: A QComboBox object representing the selected column. Its current text is used for comparison.
        
            Returns:
                None
        """
        if self.RenameSelect.currentText() != self.RenameLine.text():
            self.RenameButton.setEnabled(True)
        else:
            self.RenameButton.setDisabled(True)

    def renameColumn(self):
        """
        Renames a column in the DataFrames and updates the UI.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            eColumns: List of column names for the first DataFrame.
            distanceCols: List of column names for distance calculations.
            angleCols: List of column names for angle calculations.
            sumCols: List of column names for sum calculations.
            differenceCols: List of column names for difference calculations.
            baseDf: The base DataFrame.
            mainDf: The main DataFrame displayed in the UI.
            _model: The underlying data model.
        
        Returns:
            None
        """
        newName = self.RenameLine.text()
        oldName = self.RenameSelect.currentText()
        for array in [self.eColumns, self.distanceCols, self.angleCols, self.sumCols, self.differenceCols]:
            for column in array.copy():
                if column == oldName:
                    array[array.index(column)] = newName
        self.baseDf.rename(columns={oldName: newName}, inplace=True)
        self.mainDf.rename(columns={oldName: newName}, inplace=True)
        self.refreshLists()
        self._model.refreshTable(self.mainDf)
        self.addMessage(f'Column {oldName} has been renamed. New name is {newName}.')

    def delCoordsAction(self, state):
        """
        Deletes or adds coordinate columns to the main DataFrame based on the state.
        
        Args:
            state: A boolean indicating whether to delete or add coordinate columns. 
                   If True, coordinate columns are deleted; otherwise, they are added.
        
        Initializes:
            self.mainDf: The main DataFrame used in the application. Modified to remove or add coordinate columns.
            self.columnsNames: A list of column names. Updated after refreshing the lists.
        
        Returns:
            None
        """
        if state:
            for name in self.columnsNames:
                for proj in ['_x', '_y', '_z']:
                    self.mainDf.drop(columns=f'{name}{proj}', inplace=True, errors="ignore")
            self.refreshLists()
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with coordinates of atoms have been removed.')
        else:
            for name in reversed(self.columnsNames):
                for proj in reversed(['_x', '_y', '_z']):
                    if name + proj not in self.mainDf:
                        self.mainDf.insert(1, name + proj, self.baseDf[name + proj])
            self.refreshLists()
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with coordinates of atoms have been added.')

    def delEnergyAction(self, state):
        """
        Deletes or adds energy-related columns to the main DataFrame.
        
         This method either removes the columns specified in `self.eColumns` from
         `self.mainDf` if `state` is True, or re-inserts those columns from
         `self.baseDf` into `self.mainDf` if `state` is False. It then refreshes
         the table displayed by the model and adds a message to inform the user
         about the action taken.
        
         Parameters:
           state: A boolean indicating whether to delete (True) or add (False)
             the energy columns.
        
         Returns:
           None
        """
        if state:
            self.mainDf.drop(columns=self.eColumns, inplace=True, errors="ignore")
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with energy have been removed.')
        else:
            for column in self.eColumns:
                if column not in self.mainDf and column in self.baseDf:
                    self.mainDf.insert(len(self.mainDf.columns), column, self.baseDf[column])
            self._model.refreshTable(self.mainDf)
            self.addMessage('Columns with energy have been added.')

    def columnSelected(self, selected, deselected):
        """
        Updates the list of selected columns based on user selections.
        
        This method handles column selection and deselection events, updating an internal
        list of selected column indices and enabling/disabling a plot button accordingly.
        
        Args:
         self: The instance of the class.
         selected: The selected columns.
         deselected: The deselected columns.
        
        Returns:
         None
        
        Class Fields Initialized:
         _selected_columns: A list of integers representing the indices of the selected columns.
                            Used to track which columns are currently selected for plotting.
        """
        selected_list = selected.toList()
        deselected_list = deselected.toList()
        if selected_list and not selected_list[0].top() and selected_list[0].bottom() == len(self.mainDf) - 1 and selected_list[0].left() == selected_list[0].right():
            self._selected_columns.append(selected_list[0].left())
            self._selected_columns.sort()
        if deselected_list and self._selected_columns and not deselected_list[0].top():
            for column in deselected_list:
                self._selected_columns.remove(column.left())
        if self._selected_columns:
            self.PlotGraphButton.setEnabled(True)
        else:
            self.PlotGraphButton.setDisabled(True)

    def plotGraph(self):
        """
        Plots a graph based on the selected columns from the main DataFrame.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            self.__graph: A VRGraph object representing the plotted graph.
            self.PlotGraphButton: Disables the plot graph button after plotting.
            self._selectionModel: Clears the selection model after plotting.
        
        Returns:
            None
        """
        columns_indexes = [column.column() for column in self._selectionModel.selectedColumns()]
        df = pd.DataFrame(self.mainDf[self.mainDf.columns[0]])
        for index in columns_indexes:
            df[self.mainDf.columns[index]] = self.mainDf[self.mainDf.columns[index]]
        self.__graph = VRGraph(df)
        self.PlotGraphButton.setDisabled(True)
        self._selectionModel.clearSelection()

    def oszicarCheckboxUnlock(self):
        """
        Enables the AInclude_OSZICAR checkbox if an OSZICAR file is found in the specified directory.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            AInclude_OSZICAR: A checkbox control that is enabled if an OSZICAR file is present.
        
        Returns:
            None
        """
        directory = self.__calculation.source if self.__calculation.source.is_dir() else self.__calculation.source.parent
        if (directory / "OSZICAR").exists():
            self.AInclude_OSZICAR.setEnabled(True)

    def oszicarAction(self, state):
        """
        Adds or removes the OSZICAR dataframe to/from the main dataframe based on the provided state.
        
        Args:
            state: A boolean indicating whether to add or remove the OSZICAR dataframe.
                If True, the OSZICAR dataframe is added to the main dataframe.
                If False, the specified columns are removed from the main dataframe.
        
        Initializes:
            mainDf: The main dataframe, updated with or without the OSZICAR data.
            
        Returns:
            None
        """
        if state:
            try:
                from parsers.vasp import Parser as VaspParser

                directory = self.__calculation.source if self.__calculation.source.is_dir() else self.__calculation.source.parent
                oszicar_calculation = VaspParser(directory / "OSZICAR").parse()
                oszicarDataframe = pd.DataFrame(oszicar_calculation.properties.get("ionic_steps", []))
                if oszicarDataframe.empty:
                    self.addMessage('OSZICAR does not contain ionic-step data.')
                    return
                self.mainDf = pd.concat([self.mainDf, oszicarDataframe], axis=1)
                self.addMessage('OSZICAR dataframe has been added.')
                self._model.refreshTable(self.mainDf)
            except Exception:
                self.addMessage('Caught exception: ' + traceback.format_exc())
        else:
            self.mainDf.drop(columns=['ionic_step', 'T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'], inplace=True, errors="ignore")
            self.addMessage('OSZICAR dataframe has been removed.')
            self._model.refreshTable(self.mainDf)

    def saveTable(self):
        """
        Saves the data table to a file.
        
        Args:
            self: The object instance.
        
        Initializes:
            None
        
        Returns:
            None
        """
        tableDir = QFileDialog.getSaveFileName(None, caption='Save Table', filter="Excel (*.xlsx *.xls);;Csv (*.csv);;HTML (*.html)", selectedFilter="Excel (*.xlsx *.xls)")[0]
        if not tableDir:
            return
        try:
            output = export_dataframe(self.mainDf, tableDir)
            self.addMessage(f"File {output.name} was generated successful.")
        except PermissionError:
            self.addMessage('Close Excel table before writing.')
        except Exception:
            self.addMessage('Caught exception: ' + traceback.format_exc())

    def graphWindow(self):
        """
        Creates and displays a graph window.
        
        This method initializes the graph window, sets up the plot area,
        and displays the graph. It handles the creation of necessary widgets
        and their arrangement within the window.
        
        Args:
            self: The instance of the class.
        
        Initializes the following class fields:
            figure: The matplotlib figure object for the graph.
            canvas: The matplotlib canvas widget for displaying the graph.
            toolbar: The matplotlib toolbar for interacting with the graph.
            root: The main Tkinter window.
            plot_button: A button to trigger the graph plotting.
            x_data_entry: An entry field for inputting x-axis data.
            y_data_entry: An entry field for inputting y-axis data.
        
        Returns:
            None.
        """
        ...
