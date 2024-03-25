from OLD_Print import VRPrint
from OLD_GUI import VRGUI
from OLD_GUI import oszicar_mode_GUI
from OLD_Graphics import VRGraphsProcessing
import os
import traceback
import PySimpleGUI as sg
import pandas as pd


def preview_columns_form(result_df):
    df_string = result_df.to_string(index=False)
    df_values = [line.split() for line in df_string.splitlines()]
    df_values[0][0] = 'Time, fs'
    df_values[0].pop(1)
    df_columns, column = [], 0
    while column != len(df_values[0]):
        column_values = []
        for row in range(len(df_values)):
            column_values.append(df_values[row][column])
        df_columns.append(column_values.copy())
        column += 1
    for column in range(len(df_columns)):
        column_width = len(max(df_columns[column], key=len)) + 4
        for row in range(len(df_columns[column])):
            while len(df_columns[column][row]) != column_width:
                df_columns[column][row] += ' '
    df_values, row = [], 0
    while row != len(df_columns[0]):
        row_values = []
        for column in range(len(df_columns)):
            row_values.append(df_columns[column][row])
        df_values.append(row_values.copy())
        row += 1
    df_string = ''
    for row in range(len(df_values)):
        for column in range(len(df_values[row])):
            df_string += df_values[row][column]
        df_string += '\n' if row != len(df_values) - 1 else ''
    return df_string


class VROszicarProcessing(VRPrint):
    def __init__(self, directory, steps=[], POTIM=[]):
        VRPrint.__init__(self)
        self.directory, self.steps = directory, steps
        self.directory_files = os.listdir(directory)
        self.oszicar_files, self.data, self.POTIM, self.oszicar_df = [], [], POTIM, pd.DataFrame()
        self.oszicar_search()
        if self.oszicar_files:
            self.form_oszicar_dataframe()
        else:
            self.print('No OSZICAR files in directory.')

    def oszicar_search(self):
        for file in self.directory_files:
            if 'OSZICAR' in file:
                self.oszicar_files.append(file)
        if self.oszicar_files:
            self.oszicar_files.sort()
        if 'OSZICAR' in self.oszicar_files:
            self.oszicar_files.append(self.oszicar_files[0])
            self.oszicar_files.pop(0)

    def oszicar_parse(self, index):
        if index > 0:
            start_count = self.data[-1][0]
        else:
            start_count = 0
        with open(f'{self.directory}/{self.oszicar_files[index]}', 'r') as osz:
            while True:
                line = osz.readline()
                if not line:
                    break
                else:
                    if 'T' in line and 'mag' in line:
                        start_count += 1
                        add_to_data = [start_count]
                        add_to_data.extend(list(map(float, line.split()[2::2])))
                        self.data.append(list(add_to_data))
                        del add_to_data
        if self.POTIM:
            prev_index = 0
            for index, POTIM in enumerate(self.POTIM):
                self.data[prev_index:self.steps[index]][0] = self.data[prev_index:self.steps[index]][0] * POTIM
                prev_index = self.steps[index]
        self.data.pop(-1)
        self.data.pop(-1)

    def form_oszicar_dataframe(self):
        for index in range(len(self.oszicar_files)):
            self.oszicar_parse(index)
        self.oszicar_fill_to_normal_len()
        self.oszicar_df = pd.DataFrame(self.data, columns=['Time, fs', 'T', 'E', 'F', 'E0', 'EK', 'SP', 'SK', 'mag'])

    def oszicar_fill_to_normal_len(self):
        if self.steps:
            while len(self.data) != self.steps - 2:
                if len(self.data) > self.steps - 2:
                    self.data.pop(-1)
                else:
                    self.data.append([None for _ in range(9)])


class VROszicarMode(VROszicarProcessing, VRGUI, VRPrint):
    def __init__(self, directory, GUI_type=oszicar_mode_GUI, title='VaspReader', theme='VRGUI'):
        super(VROszicarMode, self).__init__(directory)
        VRGUI.__init__(self, GUI_type, title, resizable=True, keep_on_top=False, theme=theme)
        VRPrint.__init__(self)
        self.theme = theme
        self.event, self.value = None, None
        self.directory = directory
        self.window['TablePreview'].update(preview_columns_form(self.oszicar_df))

    def mainloop(self):
        if self.oszicar_files:
            while True:
                self.event, self.value = self.window.read(timeout=5)
                if self.event == sg.WINDOW_CLOSED or self.event == 'Exit':
                    self.window.close()
                    break
                if self.event == 'CreateExcel':
                    self.save_table()
                if self.event == 'GraphMode':
                    self.window.hide()
                    self.print('Entering graph window.')
                    VRGraphsProcessing(self.oszicar_df, theme=self.theme).mainloop()
                    self.window.un_hide()

    def save_table(self):
        tabledir = sg.PopupGetFile(message='Input directory to save table', title='Save table', save_as=True,
                                   no_window=True, keep_on_top=True, default_path='OszicarDataframe',
                                   file_types=(("Excel File", "*.xlsx"), ("Csv File", "*.csv"), ("Html File", "*.html")))
        if tabledir.endswith('.xlsx'):
            try:
                writer = pd.ExcelWriter(tabledir)
                self.oszicar_df.to_excel(writer, sheet_name='my_analysis', index=False)
                # Auto-adjust columns' width
                for column in self.oszicar_df:
                    column_width = max(self.oszicar_df[column].astype(str).map(len).max(), len(column))
                    col_idx = self.oszicar_df.columns.get_loc(column)
                    writer.sheets['my_analysis'].set_column(col_idx, col_idx, column_width)
                writer.save()
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except PermissionError:
                self.popup('Close Excel table before writing.', title='OpenXslError')
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
        elif tabledir.endswith('.csv'):
            try:
                self.oszicar_df.to_csv(tabledir, index=False)
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
        elif tabledir.endswith('.html'):
            try:
                self.oszicar_df.to_html(tabledir, index=False, na_rep='')
                self.print(f"File {tabledir.split('/')[-1]} was generated successful.")
            except Exception as err:
                self.print('Caught exception: ' + traceback.format_exc() + '\n' +
                           'Please report your error by e-mail: solovykh.aa19@physics.msu.ru')
