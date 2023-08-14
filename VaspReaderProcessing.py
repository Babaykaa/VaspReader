import os
import traceback
import numpy as np
import pandas as pd
from VaspReaderGUI import VRGUI
from VaspReaderGUI import processing_GUI
from VaspReaderGUI import egg_window
from VaspReaderPrint import VRPrint
from VaspReaderGraphics import VRGraphsProcessing
from VaspReaderOszicar import VROszicarProcessing
from VaspReaderOszicar import preview_columns_form
import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageSequence


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
        self.show_ester_egg = 0
        if self.selected_names:
            self.columns_names = self.remove_subscript_in_names(self.selected_names)
            self.coord_columns = [name + self.coord_projection[j] for name in self.columns_names for j in range(3)]
            self.direct_columns = [name + self.direct_projection[j] for name in self.columns_names for j in range(3)]
            self.base_df = self.form_base_pandas_df()
            self.v_columns, self.e_columns = self.velocities_and_energies_calc()
            self.distance_cols, self.angle_cols, self.weightmass_cols, self.sum_cols, self.difference_cols, self.divide_cols = [], [], [], [], [], []
            self.angle_names_selected, self.divide_names_selected, self.distance_names_selected, self.difference_names_selected = [], [], [], []
            self.base_df.drop(self.base_df.index[-1], inplace=True)
            self.main_df = pd.DataFrame(self.base_df)
            for v in self.v_columns:
                del self.main_df[v]
            for d in self.direct_columns:
                del self.main_df[d]
            self.coordinates_delete()
            self.window['DistAtoms'].update(values=self.columns_names)
            self.window['AtomAngle'].update(values=self.columns_names)
            self.window['WeightAtom'].update(values=self.columns_names)
            self.update_choose_elements()
            self.window['DivideAtoms'].update(values=self.columns_names)
            self.window['SelectedAtoms'].update(self.columns_names)
            self.oszicar_checkbox_unlock()
        else:
            self.main_df = pd.DataFrame()
            timeArr = np.arange(0, float(self.calculation['POTIM']) * self.calculation['STEPS'],
                                float(self.calculation['POTIM']))
            self.main_df.insert(0, 'Time, fs', timeArr[:self.calculation['STEPS']])
            # self.window['CreateExcel'].update(disabled=True)
            # self.window['GraphMode'].update(disabled=True)
            # self.window['TableActiveCheck'].update(disabled=True)
            self.window['DelCoordCheck'].update(disabled=True)
            self.window['EnergyCheck'].update(disabled=True)
            self.oszicar_checkbox_unlock()
        self.window.un_hide()

    @staticmethod
    def remove_subscript_in_names(names):
        names = names.copy()
        renamed = []
        for name in names:
            renamed.append(''.join(name.split('_')))
        return renamed

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
                    if step > 0:
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
        data = data.reshape((-1, 3 * len(self.selected_names)))
        base_df = pd.DataFrame(data, columns=self.direct_columns)
        if self.delete_after_leave:
            base_df.mask(base_df >= 1, inplace=True)
            base_df.mask(base_df <= 0, inplace=True)
        timeArr = np.arange(0, float(self.calculation['POTIM']) * self.calculation['STEPS'], float(self.calculation['POTIM']))
        base_df.insert(0, 'Time, fs', timeArr[:self.calculation['STEPS']])
        for name in self.columns_names:
            for num, proj in enumerate(self.coord_projection):
               base_df[f'{name}{proj}'] = self.calculation['BASIS'][0][num] * base_df[f'{name}_dir_1'] + self.calculation['BASIS'][1][num] * base_df[f'{name}_dir_2'] + self.calculation['BASIS'][2][num] * base_df[f'{name}_dir_3']
        return base_df

    def velocities_and_energies_calc(self):
        v_columns = ['V_' + column for column in self.columns_names]
        e_columns = ['E_' + column for column in self.columns_names]
        for num, column in enumerate(v_columns):
            self.base_df[column] = (self.base_df[self.columns_names[num] + '_x'].diff() ** 2 + self.base_df[self.columns_names[num] + '_y'].diff() ** 2 + self.base_df[self.columns_names[num] + '_z'].diff() ** 2) ** (1 / 2) / float(self.calculation['POTIM']) * 1000
        for num, column in enumerate(e_columns):
            self.base_df[column] = (self.base_df[v_columns[num]]) ** 2 * self.masses[num] / self.calc_const
        self.base_df.drop(self.base_df.index[0], inplace=True)
        self.base_df.reset_index(drop=True, inplace=True)
        return v_columns, e_columns

    def coordinates_delete(self):
        for coord in self.coord_columns:
            del self.main_df[coord]

    def distance_combo_click(self, selected_element, other_element):
        selected = self.value[selected_element]
        dist = self.columns_names.copy()
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
        first, second = self.value['DistAtoms']
        if f'{first}--{second}' in self.base_df:
            self.popup('Column has already been added.', title='DuplicateError')
        else:
            coefficients = self.direct_curve_choose(first, second)
            self.base_df[f'{first}--{second}'] = ((self.base_df[second + '_x'] - self.base_df[first + '_x'] - coefficients[0]) ** 2 + (self.base_df[second + '_y'] - self.base_df[first + '_y'] - coefficients[1]) ** 2 + (self.base_df[second + '_z'] - self.base_df[first + '_z'] - coefficients[2]) ** 2) ** (1 / 2)
            self.main_df[f'{first}--{second}'] = self.base_df[f'{first}--{second}']

            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.distance_cols.append(f'{first}--{second}')
            if len(self.distance_cols) == 1:
                self.window['DistAdded'].update(disabled=False)
            self.window['DistAtoms'].update(values=self.columns_names)
            self.window['DistList'].update('')
            self.window['DistAdded'].update(values=self.distance_cols)
            self.window['AddDist'].update(disabled=True)
            self.update_choose_elements()
            self.distance_names_selected.clear()
            self.print(f'Column {first}--{second} has been added.')

    def remove_columns(self, add_element, remove_element, cols_list):
        to_delete = self.value[add_element]
        self.base_df.drop(columns=to_delete, inplace=True)
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
        self.update_choose_elements()
        self.print(f'Column {to_delete} has been removed.')

    def remove_COM(self):
        COM_delete = self.value['COMAdded']
        to_delete = [f'{COM_delete}_x', f'{COM_delete}_y', f'{COM_delete}_z', f'V{COM_delete}', f'E{COM_delete}']
        self.base_df.drop(columns=to_delete, inplace=True)
        to_delete.remove(f'V{COM_delete}')
        if not self.value['DelCoordCheck']:
            self.main_df.drop(columns=to_delete, inplace=True) if not self.value['EnergyCheck'] else self.main_df.drop(columns=to_delete[:3], inplace=True)
        else:
            if not self.value['EnergyCheck']:
                self.main_df.drop(columns=to_delete[-1], inplace=True)
        self.v_columns.remove(f'V{COM_delete}')
        self.print(f'Columns with {self.e_columns[-1]} have been removed.')
        self.e_columns.remove(f'E{COM_delete}')
        self.columns_names.remove(COM_delete)
        self.weightmass_cols.remove(COM_delete)
        self.window['DistAtoms'].update(values=self.columns_names)
        self.window['AtomAngle'].update(values=self.columns_names)
        self.window['WeightAtom'].update(values=self.columns_names)
        self.window['RemoveAtomWeight'].update(disabled=True)
        self.update_choose_elements()
        if len(self.weightmass_cols) == 0:
            self.window['COMAdded'].update(disabled=True)
            self.window['COMAdded'].update(values=[])
            self.window['RemoveAtomWeight'].update(disabled=True)
        else:
            self.window['COMAdded'].update(values=self.weightmass_cols)
            self.window['RemoveAtomWeight'].update(disabled=True)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))

    def angle_listbox_event(self):
        if self.value['AtomAngle']:
            if len(self.value['AtomAngle']) == 1:
                self.window['xy'].update(value=False, disabled=False)
                self.window['yz'].update(value=False, disabled=False)
                self.window['zx'].update(value=False, disabled=False)
                self.angle_names_selected = self.value['AtomAngle']
                self.window['AtomList'].update(self.angle_names_selected[0])
                self.window['AddAngle'].update(disabled=True)
            else:
                if len(self.value['AtomAngle']) > len(self.angle_names_selected):
                    self.angle_names_selected.append(*set(self.value['AtomAngle']).difference(set(self.angle_names_selected)))
                elif len(self.value['AtomAngle']) < len(self.angle_names_selected):
                    self.angle_names_selected.remove(*set(self.angle_names_selected).difference(set(self.value['AtomAngle'])))
                self.window['xy'].update(value=False, disabled=True)
                self.window['yz'].update(value=False, disabled=True)
                self.window['zx'].update(value=False, disabled=True)
                if len(self.angle_names_selected) > 3:
                    self.angle_names_selected = []
                    self.window['AtomAngle'].update(set_to_index=[])
                    self.window['AddAngle'].update(disabled=True)
                elif len(self.angle_names_selected) == 3:
                    self.window['AddAngle'].update(disabled=False)
                self.window['AtomList'].update('-'.join(self.angle_names_selected))
        else:
            self.window['xy'].update(value=False, disabled=True)
            self.window['yz'].update(value=False, disabled=True)
            self.window['zx'].update(value=False, disabled=True)
            self.window['AddAngle'].update(disabled=True)
            self.window['AtomList'].update('')
            self.angle_names_selected = []

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
        atom = self.angle_names_selected[0]
        angle, plane = [], ''
        for element in ['xy', 'yz', 'zx']:
            if self.value[element]:
                plane = element
        if f'{atom}_{plane}' not in self.angle_cols:
            self.base_df[f'{atom}_{plane}'] = np.degrees(np.arccos(np.sqrt(self.base_df[f'{atom}_{plane[0]}'].diff() ** 2 + self.base_df[f'{atom}_{plane[1]}'].diff() ** 2) / np.sqrt(self.base_df[f'{atom}_x'].diff() ** 2 + self.base_df[f'{atom}_y'].diff() ** 2 + self.base_df[f'{atom}_z'].diff() ** 2)))
            self.main_df.insert(len(self.main_df.columns), f'{atom}_{plane}', self.base_df[f'{atom}_{plane}'])
            self.print(f"Column {atom}_{plane} has been added.")
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.angle_cols.append(f'{atom}_{plane}')
            if len(self.angle_cols) == 1:
                self.window['AngleAdded'].update(disabled=False)
            self.window['AngleAdded'].update(values=self.angle_cols)
            self.update_choose_elements()
        else:
            self.popup('Column already exists.', title='DuplicateError')
        self.angle_names_selected = []

    def valence_angle_add(self):
        atoms = self.angle_names_selected
        if f'{atoms[0]}-{atoms[1]}-{atoms[2]}' not in self.angle_cols:
            self.base_df[f'{atoms[0]}--{atoms[2]}'] = sum([(self.base_df[f'{atoms[0]}{proj}'] - self.base_df[f'{atoms[2]}{proj}']) ** 2 for proj in ['_x', '_y', '_z']])
            self.base_df[f'{atoms[0]}--{atoms[1]}'] = sum([(self.base_df[f'{atoms[0]}{proj}'] - self.base_df[f'{atoms[1]}{proj}']) ** 2 for proj in ['_x', '_y', '_z']])
            self.base_df[f'{atoms[1]}--{atoms[2]}'] = sum([(self.base_df[f'{atoms[1]}{proj}'] - self.base_df[f'{atoms[2]}{proj}']) ** 2 for proj in ['_x', '_y', '_z']])

            self.base_df[f'{atoms[0]}-{atoms[1]}-{atoms[2]}'] = np.round(np.degrees(np.arccos((self.base_df[f'{atoms[0]}--{atoms[1]}'] + self.base_df[f'{atoms[1]}--{atoms[2]}'] - self.base_df[f'{atoms[0]}--{atoms[2]}']) / (2 * self.base_df[f'{atoms[0]}--{atoms[1]}'] ** 0.5 * self.base_df[f'{atoms[1]}--{atoms[2]}'] ** 0.5))), 2)

            self.base_df.drop(columns=[f'{atoms[0]}--{atoms[2]}', f'{atoms[0]}--{atoms[1]}', f'{atoms[1]}--{atoms[2]}'], inplace=True)

            self.main_df.insert(len(self.main_df.columns), f'{atoms[0]}-{atoms[1]}-{atoms[2]}', self.base_df[f'{atoms[0]}-{atoms[1]}-{atoms[2]}'])
            self.print(f"Column {atoms[0]}-{atoms[1]}-{atoms[2]} has been added.")
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.angle_cols.append(f'{atoms[0]}-{atoms[1]}-{atoms[2]}')
            if len(self.angle_cols) == 1:
                self.window['AngleAdded'].update(disabled=False)
            self.window['AngleAdded'].update(values=self.angle_cols)
            self.update_choose_elements()
        else:
            self.popup('Column already exists.', title='DuplicateError')
        self.angle_names_selected = []

    def weight_add(self):
        weightmass = self.value['WeightAtom']
        column_name = 'cm_' + '_'.join(weightmass)
        if f'E{column_name}' not in self.e_columns:
            weight_masses = dict()
            for name in self.selected_names:
                rname = ''.join(name.split('_'))
                if rname in weightmass:
                    weight_masses[rname] = self.calculation['MASSES'][self.calculation['ID-TO-NUM'][name]]
            summary_mass = sum([weight_masses[name] for name in weightmass])
            direct_cols = ['_dir_1', '_dir_2', '_dir_3']
            for index, proj in enumerate(['_x', '_y', '_z']):
                self.base_df[f"{column_name}{direct_cols[index]}"] = np.zeros(self.calculation['STEPS'] - 2)
                self.base_df[f"{column_name}{proj}"] = np.zeros(self.calculation['STEPS'] - 2)
                for atom in weightmass:
                    self.base_df[f"{column_name}{proj}"] += self.base_df[f"{atom}{proj}"] * weight_masses[atom] / summary_mass
                    self.base_df[f"{column_name}{direct_cols[index]}"] += self.base_df[f"{atom}{direct_cols[index]}"] * weight_masses[atom] / summary_mass
            self.v_columns.append(f'V{column_name}')
            self.e_columns.append(f'E{column_name}')
            self.base_df[self.v_columns[-1]] = np.sqrt(self.base_df[f'{column_name}_x'].diff() ** 2 + self.base_df[f'{column_name}_y'].diff() ** 2 + self.base_df[f'{column_name}_z'].diff() ** 2) / float(self.calculation['POTIM']) * 1000
            self.base_df[self.e_columns[-1]] = (self.base_df[self.v_columns[-1]]) ** 2 * summary_mass / self.calc_const
            if not self.value['DelCoordCheck']:
                self.main_df.insert(len(self.columns_names) * 3 + 1, column_name + '_dir_1', self.base_df[column_name + '_dir_1'])
                self.main_df.insert(len(self.columns_names) * 3 + 2, column_name + '_dir_2', self.base_df[column_name + '_dir_2'])
                self.main_df.insert(len(self.columns_names) * 3 + 3, column_name + '_dir_3', self.base_df[column_name + '_dir_3'])
                self.main_df.insert(len(self.columns_names) * 3 + 4, column_name + '_x', self.base_df[column_name + '_x'])
                self.main_df.insert(len(self.columns_names) * 3 + 5, column_name + '_y', self.base_df[column_name + '_y'])
                self.main_df.insert(len(self.columns_names) * 3 + 6, column_name + '_z', self.base_df[column_name + '_z'])
            if not self.value['EnergyCheck']:
                self.main_df.insert(len(self.main_df.columns), self.e_columns[-1], self.base_df[self.e_columns[-1]])
            self.columns_names.append(column_name)
            self.window['DistAtoms'].update(values=self.columns_names)
            self.window['AtomAngle'].update(values=self.columns_names)
            self.window['WeightAtom'].update(values=self.columns_names)
            self.window['WeightList'].update('')
            self.window['AddAtomWeight'].update(disabled=True)
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.weightmass_cols.append(column_name)
            if len(self.weightmass_cols) == 1:
                self.window['COMAdded'].update(disabled=False)
            self.window['COMAdded'].update(values=self.weightmass_cols)
            self.update_choose_elements()
            self.print(f'Column {self.e_columns[-1]} has been added.')
        else:
            self.popup('Column has already been added!', title='DuplicateError')

    def sum_add(self):
        sum_names = self.value['SumAtom']
        sum_str = 'Sm_' + '_'.join(sum_names)
        if sum_str not in self.sum_cols:
            df_columns = [f'{name}' for name in sum_names]
            self.base_df[sum_str] = self.base_df[df_columns[0]]
            for col in df_columns[1:]:
                self.base_df[sum_str] += self.base_df[col]
            if not self.value['EnergyCheck']:
                self.main_df[sum_str] = self.base_df[sum_str]
            self.window['SumList'].update('')
            self.window['AddAtomSum'].update(disabled=True)
            self.update_choose_elements()
            self.sum_cols.append(sum_str)
            if len(self.sum_cols) == 1:
                self.window['SumAdded'].update(disabled=False)
            self.window['SumAdded'].update(values=self.sum_cols)
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.e_columns.append(sum_str)
            self.print(f'Column {sum_str} has been added.')
        else:
            self.popup('Column has already been added!', title='DuplicateError')

    def remove_sum(self):
        deleting_sum = self.value['SumAdded']
        self.sum_cols.remove(deleting_sum)
        self.base_df.drop(columns=deleting_sum, inplace=True)
        if not self.value['EnergyCheck']:
            self.main_df.drop(columns=deleting_sum, inplace=True)
        if not self.sum_cols:
            self.window['SumAdded'].update(disabled=True)
            self.window['SumAdded'].update(values=[])
            self.window['RemoveAtomSum'].update(disabled=True)
        else:
            self.window['SumAdded'].update(disabled=False)
            self.window['SumAdded'].update(values=self.sum_cols)
            self.window['RemoveAtomSum'].update(disabled=True)
        self.update_choose_elements()
        self.e_columns.remove(deleting_sum)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))
        self.print(f'Column {deleting_sum} has been removed.')

    def difference_add(self):
        first, second = difference_names = self.difference_names_selected
        difference_str = 'Df_' + '_'.join(difference_names)
        if difference_str not in self.difference_cols:
            self.base_df[difference_str] = self.base_df[first] - self.base_df[second]
            if not self.value['EnergyCheck']:
                self.main_df[difference_str] = self.base_df[difference_str]
            self.window['MinusList'].update('')
            self.window['AddAtomMinus'].update(disabled=True)
            self.window['MinusAtom'].update(values=self.main_df.columns[1:])
            self.difference_cols.append(difference_str)
            if len(self.difference_cols) == 1:
                self.window['MinusAdded'].update(disabled=False)
            self.window['MinusAdded'].update(values=self.difference_cols)
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.update_choose_elements()
            self.difference_names_selected.clear()
            self.e_columns.append(difference_str)
            self.print(f'Column {difference_str} has been added.')
        else:
            self.popup('Column has already been added!', title='DuplicateError')

    def remove_difference(self):
        deleting_difference = self.value['MinusAdded']
        self.difference_cols.remove(deleting_difference)
        self.base_df.drop(columns=deleting_difference, inplace=True)
        if not self.value['EnergyCheck']:
            self.main_df.drop(columns=deleting_difference, inplace=True)
        if not self.difference_cols:
            self.window['MinusAdded'].update(disabled=True)
            self.window['MinusAdded'].update(values=[])
            self.window['RemoveAtomMinus'].update(disabled=True)
        else:
            self.window['MinusAdded'].update(disabled=False)
            self.window['MinusAdded'].update(values=self.difference_cols)
            self.window['RemoveAtomMinus'].update(disabled=True)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))
        self.update_choose_elements()
        self.e_columns.remove(deleting_difference)
        self.print(f'Column {deleting_difference} has been removed.')

    def two_variants_listbox_click(self, names_buffer, listbox_name, selected, button_name, join_separator, sort_output):
        values = self.value[listbox_name]
        if values:
            if not names_buffer:
                names_buffer = values.copy()
            else:
                if len(values) > len(names_buffer):
                    if len(names_buffer) < 2:
                        for value in values:
                            if value not in names_buffer:
                                names_buffer.append(value)
                        self.window[button_name].update(disabled=False)
                    else:
                        for value in values:
                            if value not in names_buffer:
                                names_buffer.append(value)
                        names_buffer.pop(0)
                        self.window[listbox_name].update(set_to_index=[index for index, name in enumerate(self.columns_names) if name in names_buffer])
                else:
                    for value in names_buffer:
                        if value not in values:
                            names_buffer.remove(value)
                    self.window[listbox_name].update(set_to_index=[index for index, name in enumerate(self.columns_names) if name in names_buffer])
                    self.window[button_name].update(disabled=True)
        else:
            names_buffer.clear()
        if sort_output:
            self.window[selected].update(join_separator.join(sorted(names_buffer, key=lambda x: x.split('_')[-1])))
        else:
            self.window[selected].update(join_separator.join(names_buffer))
        return names_buffer

    def divide_add(self):
        temporary_columns = []
        atoms = self.divide_names_selected
        col_name = '_'.join(atoms)
        if col_name not in self.divide_cols:
            self.value['WeightAtom'] = atoms
            self.weight_add()
            for atom in atoms:
                self.base_df[f'cm_{col_name}--{atom}'] = np.sqrt((self.base_df[f'cm_{col_name}_x'] - self.base_df[f'{atom}_x']) ** 2 + (self.base_df[f'cm_{col_name}_y'] - self.base_df[f'{atom}_y']) ** 2 + (self.base_df[f'cm_{col_name}_z'] - self.base_df[f'{atom}_z']) ** 2)
                temporary_columns.append(f'cm_{col_name}--{atom}')
            for atom in atoms:
                self.base_df[f'Vvib_{col_name}({atom})'] = self.base_df[f'cm_{col_name}--{atom}'].diff() * 1000 / self.calculation['POTIM']
                self.base_df[f'Evib_{col_name}({atom})'] = self.base_df[f'Vvib_{col_name}({atom})'] ** 2 * self.masses[self.columns_names.index(atom)] / self.calc_const
                self.base_df[f'Vsum_{col_name}({atom})'] = np.sqrt((self.base_df[f'{atom}_x'].diff() - self.base_df[f'cm_{col_name}_x'].diff()) ** 2 + (self.base_df[f'{atom}_y'].diff() - self.base_df[f'cm_{col_name}_y'].diff()) ** 2 + (self.base_df[f'{atom}_z'].diff() - self.base_df[f'cm_{col_name}_z'].diff()) ** 2) * 1000 / self.calculation['POTIM']
                self.base_df[f'Vrot_{col_name}({atom})'] = np.sqrt((self.base_df[f'Vsum_{col_name}({atom})'] ** 2 - self.base_df[f'Vvib_{col_name}({atom})'] ** 2).clip(lower=0))
                self.base_df[f'Erot_{col_name}({atom})'] = self.base_df[f'Vrot_{col_name}({atom})'] ** 2 * self.masses[self.columns_names.index(atom)] / self.calc_const
                self.e_columns.extend([f'Evib_{col_name}({atom})', f'Erot_{col_name}({atom})'])
                temporary_columns.extend([f'Vvib_{col_name}({atom})', f'Vsum_{col_name}({atom})', f'Vrot_{col_name}({atom})'])
                if not self.value['EnergyCheck']:
                    self.main_df.insert(len(self.main_df.columns), f'Evib_{col_name}({atom})', self.base_df[f'Evib_{col_name}({atom})'])
                    self.main_df.insert(len(self.main_df.columns), f'Erot_{col_name}({atom})', self.base_df[f'Erot_{col_name}({atom})'])
            self.base_df[f'Evib_{col_name}'] = sum(self.base_df[f'Evib_{col_name}({atom})'] for atom in atoms)
            self.base_df[f'Erot_{col_name}'] = sum(self.base_df[f'Erot_{col_name}({atom})'] for atom in atoms)
            self.base_df.drop(columns=temporary_columns, inplace=True)
            temporary_columns.clear()
            self.e_columns.extend([f'Evib_{col_name}', f'Erot_{col_name}'])
            if not self.value['EnergyCheck']:
                self.main_df.insert(len(self.main_df.columns), f'Evib_{col_name}', self.base_df[f'Evib_{col_name}'])
                self.main_df.insert(len(self.main_df.columns), f'Erot_{col_name}', self.base_df[f'Erot_{col_name}'])

            self.divide_cols.append(col_name)
            self.divide_names_selected.clear()
            self.window['DivideAtoms'].update(self.columns_names)
            self.window['DivideList'].update('')
            self.window['AddAtomsDivide'].update(disabled=True)
            self.window['DivideAdded'].update(values=self.divide_cols, disabled=False)
            self.update_choose_elements()
            if self.value['TableActiveCheck']:
                self.window['TablePreview'].update(preview_columns_form(self.main_df))
            self.print(f'Columns divided to vibrational and rotational energy {col_name} have been added.')
        else:
            self.popup('Column has already been added!', title='DuplicateError')

    def remove_divide(self):
        deleting_divide = self.value['DivideAdded']
        elements = deleting_divide.split('_')
        atoms = []
        for num, element in enumerate(elements):
            if num % 2 == 0:
                atoms.append(element)
            else:
                atoms[-1] = atoms[-1] + '_' + element
        to_delete_cols = [f'Evib_{deleting_divide}', f'Erot_{deleting_divide}']
        for atom in atoms:
            to_delete_cols.extend([f'Evib_{deleting_divide}({atom})', f'Erot_{deleting_divide}({atom})'])
        self.divide_cols.remove(deleting_divide)
        self.base_df.drop(columns=to_delete_cols, inplace=True)
        if not self.value['EnergyCheck']:
            self.main_df.drop(columns=to_delete_cols, inplace=True)
        [self.e_columns.remove(value) for value in to_delete_cols]
        if not self.divide_cols:
            self.window['DivideAdded'].update(disabled=True)
            self.window['DivideAdded'].update(values=[])
            self.window['RemoveAtomsDivide'].update(disabled=True)
        else:
            self.window['DivideAdded'].update(disabled=False)
            self.window['DivideAdded'].update(values=self.difference_cols)
            self.window['RemoveAtomsDivide'].update(disabled=True)
        if self.value['TableActiveCheck']:
            self.window['TablePreview'].update(preview_columns_form(self.main_df))
        self.update_choose_elements()
        self.print(f'Columns divided to vibrational and rotational energy {deleting_divide} have been removed.')

    def update_choose_elements(self):
        columns = list(self.main_df.columns[1:])
        upd_columns = []
        if self.value is not None and not self.value['DelCoordCheck']:
            for column in columns:
                if '_x' not in column and '_y' not in column and '_z' not in column and '_dir_1' not in column and '_dir_2' not in column and '_dir_3' not in column:
                    upd_columns.append(column)
        else:
            upd_columns = columns
        self.window['RenameColChoose'].update(values=upd_columns)
        self.window['RenameInput'].update('', disabled=True)
        self.window['SumAtom'].update(values=self.main_df.columns[1:])
        self.window['MinusAtom'].update(values=self.main_df.columns[1:])

    def mainloop(self):
        # self.window['TablePreview'].update(list(self.main_df.columns))
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
                if self.value['DelCoordCheck']:
                    for name in self.columns_names:
                        for proj in ['_x', '_y', '_z']:
                            self.main_df.drop(columns=f'{name}{proj}', inplace=True)
                    self.print('Columns with coordinates of atoms have been removed.')
                    self.update_choose_elements()
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))
                else:
                    for name in reversed(self.columns_names):
                        for proj in reversed(['_x', '_y', '_z']):
                            self.main_df.insert(1, name + proj, self.base_df[name + proj])
                    self.print('Columns with coordinates of atoms have been added.')
                    self.update_choose_elements()
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
                    for column in self.e_columns:
                        self.main_df.insert(len(self.main_df.columns), column, self.base_df[column])
                    self.print('Columns with energy have been added.')
                    if self.value['TableActiveCheck']:
                        self.window['TablePreview'].update(preview_columns_form(self.main_df))

            if self.event == 'DistAtoms':
                self.distance_names_selected = self.two_variants_listbox_click(self.distance_names_selected, 'DistAtoms', 'DistList', 'AddDist', ', ', True)
            if self.event == 'AddDist':
                self.distance_add()
            if self.event == 'DistAdded':
                if self.value['DistAdded'] != '':
                    self.window['RemoveDist'].update(disabled=False)
            if self.event == 'RemoveDist':
                self.remove_columns('DistAdded', 'RemoveDist', self.distance_cols)

            if self.event == 'AtomAngle':
                self.angle_listbox_event()
            if self.event == 'xy':
                self.angle_plane_events('xy', 'yz', 'zx')
            if self.event == 'yz':
                self.angle_plane_events('yz', 'xy', 'zx')
            if self.event == 'zx':
                self.angle_plane_events('zx', 'xy', 'yz')
            if self.event == 'AddAngle':
                if len(self.angle_names_selected) == 1:
                    self.angle_add()
                elif len(self.angle_names_selected) == 3:
                    self.valence_angle_add()
            if self.event == 'AngleAdded':
                if self.value['AngleAdded'] != '':
                    self.window['RemoveAngle'].update(disabled=False)
            if self.event == 'RemoveAngle':
                self.remove_columns('AngleAdded', 'RemoveAngle', self.angle_cols)

            if self.event == 'WeightAtom':
                if len(self.value['WeightAtom']) > 1:
                    self.window['AddAtomWeight'].update(disabled=False)
                else:
                    self.window['AddAtomWeight'].update(disabled=True)
                self.window['WeightList'].update(', '.join(self.value['WeightAtom']))
            if self.event == 'AddAtomWeight':
                self.weight_add()
            if self.event == 'COMAdded':
                if self.value['COMAdded'] != '':
                    self.window['RemoveAtomWeight'].update(disabled=False)
            if self.event == 'RemoveAtomWeight':
                self.remove_COM()

            if self.event == 'SumAtom':
                if len(self.value['SumAtom']) > 1:
                    self.window['AddAtomSum'].update(disabled=False)
                else:
                    self.window['AddAtomSum'].update(disabled=True)
                self.window['SumList'].update(', '.join(self.value['SumAtom']))
            if self.event == 'AddAtomSum':
                self.sum_add()
            if self.event == 'SumAdded':
                if self.value['SumAdded'] != '':
                    self.window['RemoveAtomSum'].update(disabled=False)
            if self.event == 'RemoveAtomSum':
                self.remove_sum()

            if self.event == 'MinusAtom':
                self.difference_names_selected = self.two_variants_listbox_click(self.difference_names_selected, 'MinusAtom', 'MinusList', 'AddAtomMinus', '---', False)
            if self.event == 'AddAtomMinus':
                self.difference_add()
            if self.event == 'MinusAdded':
                if self.value['MinusAdded'] != '':
                    self.window['RemoveAtomMinus'].update(disabled=False)
            if self.event == 'RemoveAtomMinus':
                self.remove_difference()

            if self.event == 'DivideAtoms':
                self.divide_names_selected = self.two_variants_listbox_click(self.divide_names_selected, 'DivideAtoms', 'DivideList', 'AddAtomsDivide', ', ', True)
            if self.event == 'AddAtomsDivide':
                self.divide_add()
            if self.event == 'DivideAdded':
                if self.value['DivideAdded'] != '':
                    self.window['RemoveAtomsDivide'].update(disabled=False)
            if self.event == 'RemoveAtomsDivide':
                self.remove_divide()

            if self.event == 'RenameColChoose':
                self.window['RenameInput'].update(self.value['RenameColChoose'], disabled=False)
            if self.event == 'RenameInput':
                if self.value['RenameInput'] != self.value['RenameColChoose']:
                    self.window['RenameSubmit'].update(disabled=False)
                else:
                    self.window['RenameSubmit'].update(disabled=True)
            if self.event == 'RenameSubmit':
                name = self.value['RenameInput']
                for array in [self.e_columns, self.distance_cols, self.angle_cols, self.sum_cols, self.difference_cols, self.divide_names_selected, self.distance_names_selected, self.difference_names_selected]:
                    for column in array.copy():
                        if column == self.value['RenameColChoose']:
                            array[array.index(column)] = name
                self.base_df.rename(columns={self.value['RenameColChoose']: name}, inplace=True)
                self.main_df.rename(columns={self.value['RenameColChoose']: name}, inplace=True)
                if self.value['TableActiveCheck']:
                    self.window['TablePreview'].update(preview_columns_form(self.main_df))
                self.print(f'Column {self.value["RenameColChoose"]} has been renamed. New name is {name}.')
                self.update_choose_elements()

            if self.event == 'RenameImage':
                if self.show_ester_egg < 4:
                    self.print('Nothing here.')
                    self.show_ester_egg += 1
                elif self.show_ester_egg == 4:
                    self.print('Do you really hope to find something clicking this image?')
                    self.show_ester_egg += 1
                elif self.show_ester_egg == 5:
                    self.print('Come on. Click it much stronger.')
                    self.show_ester_egg += 1
                elif 5 < self.show_ester_egg < 10:
                    self.show_ester_egg += 1
                else:
                    self.print('Wow wow, you are really crazy. Okay, I\'l show you something interesting!')
                    self.show_ester_egg = 0
                    window = VRGUI(egg_window, title='Something fine', location=self.window.current_location(), element_justification='c', margins=(0, 0), element_padding=(0, 0)).window_return()
                    gif_filename = 'Debug_Wallpaper\\starwars.gif'

                    interframe_duration = Image.open(gif_filename).info['duration']  # get how long to delay between frames
                    win_closed = False
                    while True:
                        for frame in ImageSequence.Iterator(Image.open(gif_filename)):
                            event, values = window.read(timeout=interframe_duration)
                            if event == sg.WIN_CLOSED:
                                win_closed = True
                                break
                            window['-EGGIMAGE-'].update(data=ImageTk.PhotoImage(frame))
                        if win_closed:
                            break

            if self.event == 'GraphMode':
                self.window.hide()
                self.print('Entering graph window.')
                VRGraphsProcessing(self.main_df, theme=self.theme).mainloop()
                self.window.un_hide()
