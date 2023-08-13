import os
import traceback
import numpy as np
import pandas as pd
import math
from VaspReaderGUI import VRGUI
from VaspReaderGUI import processing_GUI
from VaspReaderPrint import VRPrint
from VaspReaderGraphics import VRGraphsProcessing
from VaspReaderOszicar import VROszicarProcessing
from VaspReaderOszicar import preview_columns_form
import PySimpleGUI as sg


class VRProcessing(VRGUI, VRPrint):
    """VaspReader processing class. Initialising of this class create a window for processing molecular dynamic results
       from VASP program. Use this with mainloop function, which work with events sent by window."""
    calc_const = 2 * 9.65 * 1000
    coord_projection = ('_x', '_y', '_z')
    direct_projection = ('_dir_1', '_dir_2', '_dir_3')

    def __init__(self, selected_atoms, calculation, name, delete_after_leave, GUI_type=processing_GUI, title='VaspReader', theme='VRGUI'):
        super(VRProcessing, self).__init__(GUI_type, title, resizable=True, keep_on_top=False, theme=theme)
        VRPrint.__init__(self)
        self.window.hide()
        self.theme = theme
        self.event, self.value = None, None
        self.calculation = calculation
        self.delete_after_leave = delete_after_leave
        self.name = name
        self.selected_atoms = selected_atoms
        self.masses = self.selected_data_form('MASSES')
        self.selected_names = self.selected_data_form('ID')
        self.coord_columns = [name + self.coord_projection[j] for name in self.selected_names for j in range(3)]
        self.direct_columns = [name + self.direct_projection[j] for name in self.selected_names for j in range(3)]
        self.base_df = self.form_base_pandas_df()
        self.v_columns, self.e_columns = self.velocities_and_energies_calc()
        self.distance_cols, self.angle_cols, self.weightmass_cols, self.sum_cols = [], [], [], []
        self.divide_names_selected = []
        self.lines_to_none = {column[2:]: -1 for column in self.e_columns}
        self.deleted_columns, self.deleted_positions = [], []
        if self.delete_after_leave:
            self.set_to_none_after_leave_cell()
        else:
            pass
            # self.vasprun_mistakes_fix() # deprecated
        self.base_df.drop(self.base_df.index[-1], inplace=True)
        self.main_df = pd.DataFrame(self.base_df)
        for v in self.v_columns:
            del self.main_df[v]
        for d in self.direct_columns:
            del self.main_df[d]
        self.coordinates_delete()
        self.window['FirstAtomDist'].update(values=self.selected_names)
        self.window['SecondAtomDist'].update(values=self.selected_names)
        self.window['AtomAngle'].update(values=self.selected_names)
        self.window['WeightAtom'].update(values=self.selected_names)
        self.window['SumAtom'].update(values=self.selected_names)
        self.window['DevideAtoms'].update(values=self.selected_names)
        self.window['SelectedAtoms'].update(self.selected_names)
        self.oszicar_checkbox_unlock()
        self.window.un_hide()

    def save_table(self):
        tabledir = sg.PopupGetFile(message='Input directory to save table', title='Save table', save_as=True,
                                   no_window=True, keep_on_top=True, default_extension=self.name, default_path=self.name,
                                   file_types=(("Excel File", "*.xlsx"), ("Csv File", "*.csv"), ("Html File", "*.html")))
        if tabledir.endswith('.xlsx'):
            try:
                writer = pd.ExcelWriter(tabledir)
                self.main_df.to_excel(writer, sheet_name='my_analysis', index=False)
                # Auto-adjust columns' width
                for column in self.main_df:
                    column_width = max(self.main_df[column].astype(str).map(len).max(), len(column))
                    col_idx = self.main_df.columns.get_loc(column)
                    writer.sheets['my_analysis'].set_column(col_idx, col_idx, column_width)
                writer.close()
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except PermissionError:
                self.popup('Close Excel table before writing.', title='OpenXslError')
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
        elif tabledir.endswith('.csv'):
            try:
                self.main_df.to_csv(tabledir, index=False)
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
        elif tabledir.endswith('.html'):
            try:
                self.main_df.to_html(tabledir, index=False, na_rep='')
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')

    def oszicar_checkbox_unlock(self):
        files = os.listdir(self.calculation['DIRECTORY'])
        for file in files:
            if 'OSZICAR' in file:
                self.window['OSZICARcheck'].update(disabled=False)
                break

    def selected_data_form(self, dict_name):
        return [self.calculation[dict_name][i] for i in range(self.calculation['ATOMNUMBER']) if self.selected_atoms[i]]

    @staticmethod
    def atom_away(direct, data):
        bad_columns = []
        for num, _ in enumerate(direct):
            if direct[num] - data[num] > 0.9:
                bad_columns.append((num, 'minus'))
            elif data[num] - direct[num] > 0.9:
                bad_columns.append((num, 'plus'))
        return bad_columns

    def atom_away_columns_fix(self, data, counter, bad_columns, step, atom_num):
        new_col = self.calculation['DIRECT'][step][atom_num].tolist()
        for num, operation in bad_columns:
            expr_factor = round(abs(self.calculation['DIRECT'][step][atom_num][num] - data[step - 1][counter][num]))
            if operation == 'plus':
                new_col[num] = new_col[num] + expr_factor
            else:
                new_col[num] = new_col[num] - expr_factor
        return np.array(new_col)


    def form_base_pandas_df(self):
        data = []
        for step in range(self.calculation['STEPS']):
            temp, counter = [], 0
            for atom_num in range(self.calculation['ATOMNUMBER']):
                if self.selected_atoms[atom_num]:
                    if not self.delete_after_leave and step > 0:
                        bad_columns = self.atom_away(self.calculation['DIRECT'][step][atom_num], data[step - 1][counter])
                        if bad_columns:
                            temp.append(self.atom_away_columns_fix(data, counter, bad_columns, step, atom_num))
                        else:
                            temp.append(self.calculation['DIRECT'][step][atom_num])
                        del bad_columns
                    else:
                        temp.append(self.calculation['DIRECT'][step][atom_num])
                    counter += 1
            data.append(temp.copy())
            del temp
        data = np.asarray(data)
        cartesian = np.dot(data, self.calculation['BASIS']).reshape((-1, 3 * len(self.selected_names))).transpose()
        data = data.reshape((-1, 3 * len(self.selected_names)))
        main_df = pd.DataFrame(data, columns=self.direct_columns)
        timeArr = np.arange(0, float(self.calculation['POTIM']) * self.calculation['STEPS'], float(self.calculation['POTIM']))
        main_df.insert(0, 'Time, fs', timeArr[:self.calculation['STEPS']])
        for num, column in enumerate(self.coord_columns):
            main_df[column] = cartesian[num]
        return main_df

    def velocities_and_energies_calc(self):
        supportive_df = pd.DataFrame(self.base_df).shift(periods=-1)
        v_columns = ['V_' + column for column in self.selected_names]
        e_columns = ['E_' + column for column in self.selected_names]
        start_index = len(self.direct_columns)
        for num, column in enumerate(v_columns):
            self.base_df[column] = ((self.base_df[self.selected_names[num] + '_x'] - supportive_df[self.selected_names[num] + '_x']) ** 2 + (self.base_df[self.selected_names[num] + '_y'] - supportive_df[self.selected_names[num] + '_y']) ** 2 + (self.base_df[self.selected_names[num] + '_z'] - supportive_df[self.selected_names[num] + '_z']) ** 2) ** (1 / 2) / float(self.calculation['POTIM']) * 1000
        for num, column in enumerate(e_columns):
            self.base_df[column] = (self.base_df[v_columns[num]]) ** 2 * self.masses[num] / self.calc_const
        self.base_df.drop(self.base_df.index[0], inplace=True)
        self.base_df.reset_index(drop=True, inplace=True)
        return v_columns, e_columns

    def set_to_none_after_leave_cell(self):
        for i in range(len(self.e_columns)):
            for j in range(self.calculation['STEPS'] - 2):
                if self.base_df[self.e_columns[i]][j + 1] > self.base_df[self.e_columns[i]][j] * 10:
                    self.lines_to_none[self.e_columns[i][2:]] = j + 1
                    break
        for ID in self.lines_to_none:
            if self.lines_to_none[ID] != -1:
                for step in range(self.lines_to_none[ID], self.calculation['STEPS'] - 2):
                    self.base_df.loc[step, f'E_{ID}'] = None

    def vasprun_mistakes_fix(self):
        for column in self.base_df.columns:
            for index in range(1, len(self.base_df[column]) - 1):
                if abs(self.base_df[column][index - 1] * 10) < abs(self.base_df[column][index]) and abs(self.base_df[column][index]) > abs(self.base_df[column][index + 1] * 10):
                    self.base_df[column][index] = self.base_df[column][index - 1]

    def coordinates_delete(self):
        for coord in self.coord_columns:
            del self.main_df[coord]

    def distance_combo_click(self, selected_element, other_element):
        selected = self.value[selected_element]
        dist = self.selected_names.copy()
        dist.remove(selected)
        other = self.value[other_element]
        self.window[other_element].update(values=dist)
        self.window[other_element].update(other)
        if self.value[other_element] != '':
            self.window['AddDist'].update(disabled=False)

    def direct_curve_choose(self, first, second):
        periodical_coefficients = []
        for proj in ['_dir_1', '_dir_2', '_dir_3']:
            periodical_coefficients.append(round(self.base_df[second + proj][0] - self.base_df[first + proj][0]))
        return np.dot(np.asarray(periodical_coefficients), self.calculation['BASIS'])

    def distance_add(self):
        if self.value['FirstAtomDist'] != '' and self.value['SecondAtomDist'] != '':
            first, second = self.value['FirstAtomDist'], self.value['SecondAtomDist']
            if first + '--' + second in self.main_df:
                self.popup('Column has already been added.', title='DuplicateError')
            else:
                coefficients = self.direct_curve_choose(first, second)
                self.main_df[first + '--' + second] = ((self.base_df[second + '_x'] - self.base_df[first + '_x'] - coefficients[0]) ** 2 + (self.base_df[second + '_y'] - self.base_df[first + '_y'] - coefficients[1]) ** 2 + (self.base_df[second + '_z'] - self.base_df[first + '_z'] - coefficients[2]) ** 2) ** (1 / 2)
                if self.lines_to_none[first] != -1 and self.lines_to_none[second] != -1:
                    for num in range(min(self.lines_to_none[first], self.lines_to_none[second]), self.calculation['STEPS'] - 1):
                        self.main_df.loc[num, first + '--' + second] = None
                elif self.lines_to_none[first] != -1 and self.lines_to_none[second] == -1:
                    for num in range(self.lines_to_none[first], self.calculation['STEPS'] - 1):
                        self.main_df.loc[num, first + '--' + second] = None
                elif self.lines_to_none[first] == -1 and self.lines_to_none[second] != -1:
                    for num in range(self.lines_to_none[second], self.calculation['STEPS'] - 1):
                        self.main_df.loc[num, first + '--' + second] = None
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.distance_cols.append(first + '--' + second)
            if len(self.distance_cols) == 1:
                self.window['DistAdded'].update(disabled=False)
            self.window['DistAdded'].update(values=self.distance_cols)
            self.print(f'Column {first}--{second} has been added.')
        else:
            self.popup('Choose atoms before add.', title='EmptyChooseError')

    def remove_columns(self, add_element, remove_element, cols_list):
        to_delete = self.value[add_element]
        self.main_df.drop(columns=to_delete, inplace=True)
        cols_list.remove(to_delete)
        if len(cols_list) == 0:
            self.window[add_element].update(disabled=True)
            self.window[add_element].update(values=[])
            self.window[remove_element].update(disabled=True)
        else:
            self.window[add_element].update(values=cols_list)
            self.window[remove_element].update(disabled=True)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))
        self.print(f'Column {to_delete} has been removed.')

    def remove_COM(self):
        COM_delete = self.value['COMAdded']
        to_delete = [f'{COM_delete}_x', f'{COM_delete}_y', f'{COM_delete}_z', f'V_{COM_delete}', f'E_{COM_delete}']
        self.base_df.drop(columns=to_delete, inplace=True)
        to_delete.remove(f'V_{COM_delete}')
        if not self.value['DelCoordCheck']:
            self.main_df.drop(columns=to_delete, inplace=True) if not self.value['EnergyCheck'] else self.main_df.drop(columns=to_delete[:3], inplace=True)
        else:
            if not self.value['EnergyCheck']:
                self.main_df.drop(columns=to_delete[-1], inplace=True)
        for col in self.main_df.columns:
            if COM_delete in col:
                self.main_df.drop(columns=[col], inplace=True)
        self.v_columns.remove(f'V_{COM_delete}')
        self.print(f'Columns with {self.e_columns[-1]} have been removed.')
        self.e_columns.remove(to_delete[-1])
        self.selected_names.remove(COM_delete)
        self.weightmass_cols.remove(COM_delete)
        self.lines_to_none.pop(COM_delete)
        self.window['FirstAtomDist'].update(values=self.selected_names)
        self.window['SecondAtomDist'].update(values=self.selected_names)
        self.window['AtomAngle'].update(values=self.selected_names)
        self.window['WeightAtom'].update(values=self.selected_names)
        self.window['RemoveAtomWeight'].update(disabled=True)
        if len(self.weightmass_cols) == 0:
            self.window['COMAdded'].update(disabled=True)
            self.window['COMAdded'].update(values=[])
            self.window['RemoveAtomWeight'].update(disabled=True)
        else:
            self.window['COMAdded'].update(values=self.weightmass_cols)
            self.window['RemoveAtomWeight'].update(disabled=True)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))

    def angle_plane_events(self, event_plane, *others_planes):
        if self.value[event_plane]:
            self.window['AddAngle'].update(disabled=False)
            self.window[others_planes[0]].update(disabled=True)
            self.window[others_planes[1]].update(disabled=True)
        else:
            self.window['AddAngle'].update(disabled=True)
            self.window[others_planes[0]].update(disabled=False)
            self.window[others_planes[1]].update(disabled=False)

    def angle_add(self):
        atom = self.value['AtomAngle']
        angle, plane = [], ''
        for element in ['xy', 'yz', 'zx']:
            if self.value[element]:
                plane = element
        for c in range(self.calculation['STEPS'] - 3):
            velocity = ((self.base_df[atom + '_x'][c + 1] - self.base_df[atom + '_x'][c]) ** 2 +
                        (self.base_df[atom + '_y'][c + 1] - self.base_df[atom + '_y'][c]) ** 2 +
                        (self.base_df[atom + '_z'][c + 1] - self.base_df[atom + '_z'][c]) ** 2) ** (1 / 2)
            v = ((self.base_df[atom + f'_{plane[0]}'][c + 1] - self.base_df[atom + f'_{plane[0]}'][c]) ** 2 +
                 (self.base_df[atom + f'_{plane[1]}'][c + 1] - self.base_df[atom + f'_{plane[1]}'][c]) ** 2) ** (1 / 2)
            angle.append(math.degrees(math.acos(v / velocity)))
        angle.append(angle[-1])
        try:
            self.main_df.insert(len(self.main_df.columns), atom + f'_{plane}_angle', np.array(angle))
            if self.lines_to_none[atom] != -1:
                for step in range(self.lines_to_none[atom], self.calculation['STEPS'] - 1):
                    self.main_df.loc[step, atom + f'_{plane}_angle'] = None
            self.print(f"Column {atom}_{plane}_angle has been added.")
        except ValueError:
            self.popup('Column already exists.', title='DuplicateError')
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))
        self.angle_cols.append(atom + f'_{plane}_angle')
        if len(self.angle_cols) == 1:
            self.window['AngleAdded'].update(disabled=False)
        self.window['AngleAdded'].update(values=self.angle_cols)

    def weight_add(self):
        weightmass = self.value['WeightAtom']
        column_name = 'COM_' + '_'.join(weightmass)
        if f'E_{column_name}' not in self.e_columns:
            weight_masses = dict()
            for num, name in enumerate(self.selected_names):
                if name in weightmass:
                    weight_masses[name] = self.masses[num]
            summary_mass = sum([weight_masses[name] for name in weightmass])
            for index, proj in enumerate(['_x', '_y', '_z']):
                self.base_df['TEMP'] = [0.0 for i in range(self.calculation['STEPS'] - 2)]
                for atom in weightmass:
                    self.base_df['TEMP'] += self.base_df[f"{atom}{proj}"] * weight_masses[atom] / summary_mass
                self.base_df.insert(len(self.selected_names) * 3 + index + 1, f"{column_name}{proj}", self.base_df['TEMP'])
                self.base_df.drop(columns=['TEMP'], inplace=True)
            self.selected_names.append(column_name)
            self.window['FirstAtomDist'].update(values=self.selected_names)
            self.window['SecondAtomDist'].update(values=self.selected_names)
            self.window['AtomAngle'].update(values=self.selected_names)
            self.window['WeightAtom'].update(values=self.selected_names)
            self.v_columns.append(f'V_{column_name}')
            self.e_columns.append(f'E_{column_name}')
            DopDF = self.base_df[[column for column in [f'{column_name}_{proj}' for proj in ['x', 'y', 'z']]]].copy()
            DopDF = DopDF.shift(periods=-1)
            self.base_df.insert(self.base_df.columns.get_loc(self.v_columns[-2]) + 1, self.v_columns[-1], ((self.base_df[column_name + '_x'] - DopDF[column_name + '_x']) ** 2 + (self.base_df[column_name + '_y'] - DopDF[column_name + '_y']) ** 2 + (self.base_df[column_name + '_z'] - DopDF[column_name + '_z']) ** 2) ** (1 / 2) / float(self.calculation['POTIM']) * 1000)
            self.base_df.insert(self.base_df.columns.get_loc(self.e_columns[-2]) + 1, self.e_columns[-1], (self.base_df[self.v_columns[-1]]) ** 2 * summary_mass / self.calc_const)
            to_none = list()
            for atom in weightmass:
                if self.lines_to_none[atom] != -1:
                    to_none.append(self.lines_to_none[atom])
            if to_none:
                self.lines_to_none[column_name] = min(to_none)
                for step in range(self.lines_to_none[column_name], self.calculation['STEPS'] - 2):
                    for proj in ['_x', '_y', '_z']:
                        self.base_df.loc[step, f"column_name{proj}"] = None
                    self.base_df.loc[step, self.v_columns[-1]] = None
                    self.base_df.loc[step, self.e_columns[-1]] = None
            else:
                self.lines_to_none[column_name] = -1
            if not self.value['DelCoordCheck']:
                self.main_df.insert(len(self.selected_names) * 3 + 1, column_name + '_x', self.base_df[column_name + '_x'])
                self.main_df.insert(len(self.selected_names) * 3 + 2, column_name + '_y', self.base_df[column_name + '_y'])
                self.main_df.insert(len(self.selected_names) * 3 + 3, column_name + '_z', self.base_df[column_name + '_z'])
            if not self.value['EnergyCheck']:
                self.main_df.insert(self.main_df.columns.get_loc(self.e_columns[-2]) + 1, self.e_columns[-1], self.base_df[self.e_columns[-1]])
            self.window['WeightList'].update('')
            self.window['AddAtomWeight'].update(disabled=True)
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.weightmass_cols.append(column_name)
            if len(self.weightmass_cols) == 1:
                self.window['COMAdded'].update(disabled=False)
            self.window['COMAdded'].update(values=self.weightmass_cols)
            self.print(f'Column {self.e_columns[-1]} has been added.')
        else:
            self.popup('Column has already been added!', title='DuplicateError')

    def sum_add(self):
        sum_atoms = self.value['SumAtom']
        sum_str = 'E_Sum_' + '_'.join(sum_atoms)
        if sum_str not in self.e_columns:
            df_columns = [f'E_{atom}' for atom in sum_atoms]
            self.base_df.insert(self.base_df.columns.get_loc(self.e_columns[-1]) + 1, sum_str, self.base_df[df_columns[0]])
            for column in df_columns[1:]:
                self.base_df[sum_str] += self.base_df[column]
            to_none = []
            for atom in sum_atoms:
                if self.lines_to_none[atom] != -1:
                    to_none.append(self.lines_to_none[atom])
            if to_none:
                for step in range(min(to_none), self.calculation['STEPS'] - 2):
                    self.base_df.loc[step, sum_str] = None
            if not self.value['EnergyCheck']:
                self.main_df.insert(self.main_df.columns.get_loc(self.e_columns[-1]) + 1, sum_str, self.base_df[sum_str])
            if self.value['SumDel']:
                self.deleted_columns.append(df_columns)
                if len(self.deleted_columns) > 1:
                    repeating_atoms = list()
                    for atom in self.deleted_columns[-1]:
                        for column in self.deleted_columns:
                            if column != self.deleted_columns[-1]:
                                for deleted_atom in column:
                                    if atom == deleted_atom:
                                        repeating_atoms.append(atom)
                    if len(repeating_atoms) != 0:
                        for repeat_to_del in repeating_atoms:
                            df_columns.remove(repeat_to_del)
                temp = []
                for num, atom in enumerate(self.e_columns):
                    for sum_atom in df_columns:
                        if atom == sum_atom:
                            temp.append(num)
                self.deleted_positions.append(temp)
                self.main_df.drop(columns=df_columns, inplace=True)
                for sum_atom in df_columns:
                    self.e_columns.remove(sum_atom)
            elif not self.value['SumDel']:
                self.deleted_columns.append('No atoms')
            self.window['SumList'].update('')
            self.window['AddAtomSum'].update(disabled=True)
            self.window['SumAtom'].update(values=self.selected_names)
            self.e_columns.append(sum_str)
            self.sum_cols.append(sum_str)
            if len(self.sum_cols) == 1:
                self.window['SumAdded'].update(disabled=False)
            self.window['SumAdded'].update(values=self.sum_cols)
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.print(f'Column {sum_str} has been added.')
        else:
            self.popup('Column has already been added!', title='DuplicateError')

    def remove_sum(self):
        deleting_sum = self.value['SumAdded']
        self.e_columns.remove(deleting_sum)
        trace_position = 0
        for num, column in enumerate(self.sum_cols):
            if deleting_sum == column:
                trace_position = num
        self.base_df.drop(columns=deleting_sum, inplace=True)
        self.main_df.drop(columns=deleting_sum, inplace=True)
        if self.deleted_columns[trace_position] != 'No atoms':
            self.main_df.drop(columns=self.e_columns, inplace=True)
            for place in range(len(self.deleted_positions[trace_position])):
                self.e_columns.insert(self.deleted_positions[trace_position][place],
                                      self.deleted_columns[trace_position][place])
            if self.value['DelCoordCheck']:
                for col in range(len(self.e_columns)):
                    self.main_df.insert(1 + col, self.e_columns[col], self.base_df[self.e_columns[col]])
            else:
                for col in range(len(self.e_columns)):
                    self.main_df.insert(1 + 3 * len(self.selected_names) + col, self.e_columns[col], self.main_df[self.e_columns[col]])
            self.deleted_positions.pop(trace_position)
            self.deleted_columns.pop(trace_position)
            self.sum_cols.pop(trace_position)
        else:
            self.deleted_columns.pop(trace_position)
            self.sum_cols.pop(trace_position)
        if self.sum_cols:
            self.window['SumAdded'].update(disabled=True)
            self.window['SumAdded'].update(values=[])
            self.window['RemoveAtomSum'].update(disabled=True)
        else:
            self.window['SumAdded'].update(disabled=False)
            self.window['SumAdded'].update(values=self.sum_cols)
            self.window['RemoveAtomSum'].update(disabled=False)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))
        self.print(f'Column {deleting_sum} has been removed.')

    def devide_listbox_click(self):
        values = self.value['DevideAtoms']
        if values:
            if not self.divide_names_selected:
                self.divide_names_selected = values.copy()
            else:
                if len(values) > len(self.divide_names_selected):
                    if len(self.divide_names_selected) < 2:
                        for value in values:
                            if value not in self.divide_names_selected:
                                self.divide_names_selected.append(value)
                    else:
                        for value in values:
                            if value not in self.divide_names_selected:
                                self.divide_names_selected.append(value)
                        self.divide_names_selected.pop(0)
                        self.window['DevideAtoms'].update(set_to_index=[index for index, name in enumerate(self.selected_names) if name in self.divide_names_selected])
                else:
                    for value in self.divide_names_selected:
                        if value not in values:
                            self.divide_names_selected.remove(value)
                    self.window['DevideAtoms'].update(set_to_index=[index for index, name in enumerate(self.selected_names) if name in self.divide_names_selected])

        else:
            self.divide_names_selected.clear()
        self.window['DevideList'].update(', '.join(sorted(self.divide_names_selected, key=lambda x: x.split('_')[-1])))

    def divide_add(self):
        temporary_columns = []
        atoms = self.divide_names_selected
        col_name = '_'.join(atoms)
        # index_to_set = [index for index, name in enumerate(self.selected_names) if name in atoms]
        self.value['WeightAtom'] = atoms
        self.value['SumAtom'] = atoms
        self.weight_add()
        self.sum_add()
        for atom in atoms:
            self.base_df[f'COM_{col_name}--{atom}'] = np.sqrt((self.base_df[f'COM_{col_name}_x'] - self.base_df[f'{atom}_x']) ** 2 + (self.base_df[f'COM_{col_name}_y'] - self.base_df[f'{atom}_y']) ** 2 + (self.base_df[f'COM_{col_name}_z'] - self.base_df[f'{atom}_z']) ** 2)
            temporary_columns.append(f'COM_{col_name}--{atom}')
        for atom in atoms:
            self.base_df[f'V_col_{atom}'] = self.base_df[f'COM_{col_name}--{atom}'].diff() * 1000 / self.calculation['POTIM']

    def mainloop(self):
        self.window.perform_long_operation(lambda: self.window['TablePreview'].update(preview_columns_form(self.main_df)), end_key='None')
        while True:
            self.event, self.value = self.window.read()
            if self.event == sg.WINDOW_CLOSED or self.event == 'Exit':
                self.window.close()
                self.print('Processing window has been closed.')
                break
            if self.event == 'CreateExcel':
                self.save_table()
            if self.event == 'TableActiveCheck':
                if not self.value['TableActiveCheck']:
                    self.window['TablePreview'].update('', disabled=True)
                    self.print('Table preview has been turned off.')
                else:
                    self.window['TablePreview'].update(preview_columns_form(self.main_df), disabled=True)
                    self.print('Table preview has been turned on.')
            if self.event == 'DelCoordCheck':
                delete_coord_list = list()
                if self.value['DelCoordCheck']:
                    for i in range(3 * len(self.selected_names)):
                        delete_coord_list.append(self.main_df.columns[1 + i])
                    self.main_df.drop(columns=delete_coord_list, inplace=True)
                    self.print('Columns with coordinates of atoms have been removed.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))
                else:
                    for num, _ in self.selected_names:
                        for proj in ['_x', '_y', '_z']:
                            self.main_df.insert(1 + num, self.selected_names + proj, self.base_df[self.selected_names + proj])
                    self.print('Columns with coordinates of atoms have been added.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))

            if self.event == 'OSZICARcheck':
                if self.value['OSZICARcheck']:
                    osz_dataframe = VROszicarProcessing(self.calculation['DIRECTORY'], self.calculation['STEPS'], self.calculation['POTIM']).oszicar_df
                    self.main_df = pd.concat([self.main_df, osz_dataframe[osz_dataframe.columns[1:]]], axis=1)
                    self.print('OSZICAR dataframe has been added.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))
                else:
                    self.main_df.drop(columns=['T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'], inplace=True)
                    self.print('OSZICAR dataframe has been removed.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))

            if self.event == 'EnergyCheck':
                if self.value['EnergyCheck']:
                    self.main_df.drop(columns=self.e_columns, inplace=True)
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))
                    self.print('Columns with energy have been removed.')
                else:
                    if self.value['DelCoordCheck']:
                        for col in range(len(self.e_columns)):
                            self.main_df.insert(1 + col, self.e_columns[col], self.base_df[self.e_columns[col]])
                    else:
                        for col in range(len(self.e_columns)):
                            self.main_df.insert(1 + 3 * len(self.selected_atoms) + col, self.e_columns[col], self.base_df[self.e_columns[col]])
                    self.print('Columns with energy have been added.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))
            if self.event == 'FirstAtomDist':
                self.distance_combo_click('FirstAtomDist', 'SecondAtomDist')
            if self.event == 'SecondAtomDist':
                self.distance_combo_click('SecondAtomDist', 'FirstAtomDist')
            if self.event == 'AddDist':
                self.distance_add()
            if self.event == 'DistAdded':
                if self.value['DistAdded'] != '':
                    self.window['RemoveDist'].update(disabled=False)
            if self.event == 'RemoveDist':
                self.remove_columns('DistAdded', 'RemoveDist', self.distance_cols)

            if self.event == 'AtomAngle':
                if not self.value['xy'] and not self.value['yz'] and not self.value['zx']:
                    self.window['xy'].update(disabled=False)
                    self.window['yz'].update(disabled=False)
                    self.window['zx'].update(disabled=False)
            if self.event == 'xy':
                self.angle_plane_events('xy', 'yz', 'zx')
            if self.event == 'yz':
                self.angle_plane_events('yz', 'xy', 'zx')
            if self.event == 'zx':
                self.angle_plane_events('zx', 'xy', 'yz')
            if self.event == 'AddAngle':
                self.angle_add()
            if self.event == 'AngleAdded':
                if self.value['AngleAdded'] != '':
                    self.window['RemoveAngle'].update(disabled=False)
            if self.event == 'RemoveAngle':
                self.remove_columns('AngleAdded', 'RemoveAngle', self.angle_cols)

            if self.event == 'WeightAtom':
                list_weightmass_calc = self.value['WeightAtom']
                if len(list_weightmass_calc) > 1:
                    self.window['AddAtomWeight'].update(disabled=False)
                else:
                    self.window['AddAtomWeight'].update(disabled=True)
                COM_str = ', '.join(list_weightmass_calc)
                self.window['WeightList'].update(COM_str)
            if self.event == 'AddAtomWeight':
                self.weight_add()
            if self.event == 'COMAdded':
                if self.value['COMAdded'] != '':
                    self.window['RemoveAtomWeight'].update(disabled=False)
            if self.event == 'RemoveAtomWeight':
                self.remove_COM()

            if self.event == 'SumAtom':
                list_sum_calc = self.value['SumAtom']
                if len(list_sum_calc) > 1:
                    self.window['AddAtomSum'].update(disabled=False)
                else:
                    self.window['AddAtomSum'].update(disabled=True)
                sum_str = ', '.join(list_sum_calc)
                self.window['SumList'].update(sum_str)
            if self.event == 'AddAtomSum':
                self.sum_add()
            if self.event == 'SumAdded':
                if self.value['SumAdded'] != '':
                    self.window['RemoveAtomSum'].update(disabled=False)
            if self.event == 'RemoveAtomSum':
                self.remove_sum()
            '''listbox - 'DevideAtoms'; atoms_names - 'DevideList'; add button - 'AddAtomsDivide';
             added divide - 'DivideAdded'; remove_columns - 'RemoveAtomsDivide' '''
            if self.event == 'DevideAtoms':
                self.devide_listbox_click()
            if self.event == 'AddAtomsDivide':
                self.divide_add()
            if self.event == 'GraphMode':
                self.window.hide()
                self.print('Entering graph window.')
                VRGraphsProcessing(self.main_df, theme=self.theme).mainloop()
                self.window.un_hide()
