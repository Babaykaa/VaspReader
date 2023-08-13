import _tkinter
import os
import re
import subprocess
import threading
import time
import PySimpleGUI as sg
from VaspReaderGUI import VRGUI
from VaspReaderGUI import redactor_window
from VaspReaderPrint import VRPrint


class VRRedactor(VRGUI, VRPrint):
    menu = [['&File', ['&Open', '---', '&Save', 'Save As', '---', 'E&xit']], ['&Edit', ['!&Undo', '!&Redo', '---', '!Copy', '!Paste', '---', 'Search']], ['VASP', ['Check POSCAR']]]

    def __init__(self, open_directory='', GUI_type=redactor_window, title='VaspReader'):
        super(VRRedactor, self).__init__(GUI_type, title, resizable=True, keep_on_top=False)
        VRPrint.__init__(self)
        self.window['-FILETEXT-'].Widget.configure(undo=True)
        self.window.bind('<Control-f>', 'Ctrl-F')
        self.window.bind('<Control-c>', 'Ctrl-C')
        self.window.bind('<Control-v>', 'Ctrl-V')
        self.window['-FILETEXT-'].bind('<FocusIn>', 'Focus')
        self.window['-FILETEXT-'].bind('<KeyPress-Left>', 'Left')
        self.window['-FILETEXT-'].bind('<KeyPress-Right>', 'Right')
        self.window['-FILETEXT-'].bind('<KeyPress-Up>', 'Up')
        self.window['-FILETEXT-'].bind('<KeyPress-Down>', 'Down')
        self.window['-FILETEXT-'].bind('<Button-1>', 'Click')
        self.window['-FILETEXT-'].bind('<ButtonRelease-1>', 'Select')
        self.window['-FILETEXT-'].set_cursor(cursor='xterm', cursor_color='Black')
        for element in ['-SAVE-', '-SAVEAS-', '-UNDO-', '-REDO-', '-SEARCH-', '-FIND-DOWN-', '-FIND-UP-', '-FINDER-CLOSE-']:
            self.window[element].set_cursor(cursor='hand2')
        # arrow -standart; good cursors: watch, umbrella, sb_v_double_arrow, sb_h_double_arrow, question_arrow, exchange, fleur, hand2, heart
        self.window['-FINDER-'].update(visible=False)
        self.event, self.value = None, None
        self.last_event = None
        self.file_path, self.filename = open_directory, ''
        self.selected_from_to = [[], []]
        self.row, self.column = None, None
        self.rows_number = 1
        self.found_matches, self.match_index, self.newline_indexes = [], -1, []
        self.now_menu = self.menu.copy()
        self.undo_enable, self.redo_enable, self.copy_enable, self.paste_enable = False, False, False, False
        self.menu_parameters = [self.undo_enable, self.redo_enable, self.copy_enable, self.paste_enable]
        self.check_selected, self.window_close = False, False
        if self.file_path:
            self.open_file(get_file=False)
            self.window['-FILETEXT-'].Widget.edit_reset()

    @ staticmethod
    def check_permissions(path):
        bytes_string = bin(os.lstat(path).st_mode)[-9:]
        permissions_list = tuple(map(lambda x: bool(int(x)), list(bytes_string)))[:2]
        num_mode = [ind + 1 for ind, val in enumerate(permissions_list) if val]
        modes = ['n', 'r', 'w', 'r+w']
        return modes[sum(num_mode)]

    def open_file(self, get_file=True):
        try:
            if get_file:
                self.file_path = sg.PopupGetFile(message='Open file', title='Open file', no_window=True, keep_on_top=True, file_types=(("Txt files", "*.txt"), ("All files", "*.*")))
            with open(self.file_path, 'r') as new_file:
                self.window['-FILETEXT-'].update(new_file.read())
            self.filename = self.file_path.split('\\')[-1]
            self.window.set_title(f'VaspReader ({self.filename})')
            if self.check_permissions(self.file_path) == 'r':
                self.window['-FILETEXT-'].update(disabled=True)
            else:
                self.window['-FILETEXT-'].update(disabled=False)
        except UnicodeDecodeError:
            self.popup('Error of reading file.', title='Error')
            self.window_close = True
        except PermissionError:
            self.popup('You don\'t have enough permissions to open this file.')
            self.window_close = True

    def number_of_selected_rows(self):
        try:
            self.window['-SELCOUNT-'].update('Number of selected rows: ' + str(self.window['-FILETEXT-'].Widget.count("sel.first", "sel.last", "lines")[0]))
            self.selected_from_to = list(map(lambda x: list(map(int, x.split('.'))), [self.window['-FILETEXT-'].Widget.index("sel.first"), self.window['-FILETEXT-'].Widget.index("sel.last")]))
        except _tkinter.TclError:
            self.window['-SELCOUNT-'].update('Number of selected rows: 0')
            self.selected_from_to = [[], []]
        except TypeError:
            self.window['-SELCOUNT-'].update('Number of selected rows: 0')
            self.selected_from_to = list(map(lambda x: list(map(int, x.split('.'))), [self.window['-FILETEXT-'].Widget.index("sel.first"), self.window['-FILETEXT-'].Widget.index("sel.last")]))

    def row_column_update(self, selected_rows=False):
        self.row, self.column = list(map(int, self.window['-FILETEXT-'].Widget.index('insert').split('.')))
        self.window['-POSITION-'].update(f'row: {self.row}, column: {self.column}')
        if selected_rows:
            self.number_of_selected_rows()

    def find_matches(self):
        self.found_matches.clear()
        start, end = 0, len(self.value['-FILETEXT-']) - 1
        try:
            while True:
                if self.found_matches:
                    start = self.found_matches[-1] + 1
                self.found_matches.append(self.value['-FILETEXT-'].index(self.value['-FIND-'], start, end))
        except ValueError:
            self.window['-FIND-MATCHES-'].update(f'Found {len(self.found_matches)} matches.')
        if not self.newline_indexes:
            self.newline_indexes.append(-1)
            try:
                while True:
                    if self.newline_indexes:
                        start = self.newline_indexes[-1] + 1
                    self.newline_indexes.append(self.value['-FILETEXT-'].index('\n', start, end))
            except ValueError:
                self.newline_indexes.append(len(self.value['-FILETEXT-']))

    def search_previous(self):
        if self.found_matches:
            self.match_index -= 1
            if self.match_index == -1:
                self.match_index = len(self.found_matches) - 1
            self.search_set_cursor()

    def search_next(self):
        if self.found_matches:
            self.match_index += 1
            if self.match_index == len(self.found_matches):
                self.match_index = 0
            self.search_set_cursor()

    def search_set_cursor(self):
        row, column, max_column = -1, -1, -1
        for index, value in enumerate(self.newline_indexes):
            if value < self.found_matches[self.match_index]:
                row, column = index + 1, self.found_matches[self.match_index] - self.newline_indexes[index] - 1
                max_column = self.newline_indexes[index + 1] - self.newline_indexes[index]
            else:
                break
        self.window['-FILETEXT-'].set_focus()
        self.window['-FILETEXT-'].Widget.mark_set('insert', f'{row}.{column}')
        self.window['-FILETEXT-'].Widget.xview_moveto((column - 20) / max_column if column > 20 else 0)
        self.window['-FILETEXT-'].set_vscroll_position((row - 10) / (len(self.newline_indexes) - 1) if row > 10 else 0)

    def check_selected_from_to_value(self):
        if self.selected_from_to[0]:
            self.window['-COPY-'].update(disabled=False)
        else:
            self.window['-COPY-'].update(disabled=True)
        self.check_selected = False

    def menu_update(self):
        if self.menu_parameters != [self.undo_enable, self.redo_enable, self.copy_enable, self.paste_enable]:
            if self.undo_enable:
                self.now_menu[1][-1][0] = '&Undo'
            else:
                self.now_menu[1][-1][0] = '!&Undo'
            if self.redo_enable:
                self.now_menu[1][-1][1] = '&Redo'
            else:
                self.now_menu[1][-1][1] = '!&Redo'
            if self.copy_enable:
                self.now_menu[1][-1][3] = 'Copy'
            else:
                self.now_menu[1][-1][3] = '!Copy'
            if self.copy_enable:
                self.now_menu[1][-1][4] = 'Paste'
            else:
                self.now_menu[1][-1][4] = '!Paste'
            self.menu_parameters = [self.undo_enable, self.redo_enable, self.copy_enable, self.paste_enable]
            self.window['-MENU-'].update(menu_definition=self.now_menu)
            self.window.refresh()

    def edit_operation(self, operation, element, menu_parameter):
        try:
            self.window['-FILETEXT-'].Widget.edit_undo() if operation else self.window['-FILETEXT-'].Widget.edit_redo()
        except:
            self.window[element].update(disabled=True)
            menu_parameter = False

    def mainloop(self):
        while True:
            self.event, self.value = self.window.read(timeout=20)
            if self.event:
                self.window.refresh()
            self.menu_update()
            if self.check_selected:
                self.check_selected_from_to_value()
            if self.event == sg.WINDOW_CLOSED or self.event == 'Exit' or self.window_close:
                self.window.close()
                break
            if self.event == 'Open':
                self.open_file()
                self.window['-FILETEXT-'].Widget.edit_reset()
                self.window['-FILETEXT-'].Widget.edit_modified(False)
            if self.event in ['-FILETEXT-Focus', '-FILETEXT-Click', '-FILETEXT-Select']:
                self.row_column_update(True)
                self.check_selected = True
            if self.event in ['-FILETEXT-Left', '-FILETEXT-Right', '-FILETEXT-Up', '-FILETEXT-Down']:
                self.row_column_update(True)
            if self.event == '-UNDO-' or self.event == 'Undo':
                self.edit_operation(True, '-UNDO-', self.undo_enable)
                self.window['-REDO-'].update(disabled=False)
                self.redo_enable = True
            if self.event == '-REDO-' or self.event == 'Redo':
                self.edit_operation(False, '-REDO-', self.redo_enable)
                self.window['-UNDO-'].update(disabled=False)
                self.undo_enable = True
            if self.event in '-FILETEXT-':
                detected_input = [self.row - 1, self.column]
                self.row_column_update()
                self.window['-UNDO-'].update(disabled=False)
                self.undo_enable = True
                self.window['-REDO-'].update(disabled=True)
                self.redo_enable = False
                self.newline_indexes.clear()
                self.window.set_title(f'VaspReader ({self.filename}) *')
            if self.event == '-SEARCH-' or self.event == 'Ctrl-F' or self.event == 'Search':
                self.window['-FINDER-'].update(visible=True)
                self.window['-FIND-'].set_focus()
            if self.event == '-FIND-':
                if self.value['-FIND-']:
                    self.find_matches()
            if self.event == '-FIND-UP-':
                self.search_previous()
            if self.event == '-FIND-DOWN-':
                self.search_next()
            if self.event == '-FINDER-CLOSE-':
                self.window['-FINDER-'].update(visible=False)
            if self.event == '-SAVE-' or self.event == 'Save':
                if self.file_path:
                    try:
                        with open(self.file_path, 'w') as saver:
                            saver.write(self.value['-FILETEXT-'])
                        self.window.set_title(f'VaspReader ({self.filename})')
                    except PermissionError:
                        self.popup('This file cannot be change.')
                    self.window['-FILETEXT-'].Widget.edit_reset()
                else:
                    self.event = '-SAVEAS-'
            if self.event == '-SAVEAS-' or self.event == 'Save As':
                self.file_path = sg.PopupGetFile(message='Save As', title='Save file', no_window=True, save_as=True, keep_on_top=True, file_types=(("Txt files", "*.txt"), ("All files", "*.*")))
                if self.file_path:
                    try:
                        with open(self.file_path, 'w') as saver:
                            saver.write(self.value['-FILETEXT-'])
                        self.window.set_title(f'VaspReader ({self.filename})')
                    except PermissionError:
                        self.popup('This file cannot be change.')
                    self.window['-FILETEXT-'].Widget.edit_reset()


# VRRedactor().mainloop()
# subprocess.Popen([r'C:\Program Files (x86)\Notepad++\notepad++.exe', r'C:\Users\AlexS\OneDrive\Рабочий стол\TEST_CFG.txt']).wait()
