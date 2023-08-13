import numpy as np
from VaspReaderGUI import VRGUI
from VaspReaderGUI import file_choose_window
from VaspReaderGUI import chgcar_window
from VaspReaderPrint import VRPrint
import PySimpleGUI as sg
import os
import math
import matplotlib.colors as matcol


class VRChgcar(VRGUI, VRPrint):

    def __init__(self, directory='', folder='', atoms_number=None, basis=None, GUI_type=chgcar_window, title='VaspReader', theme='VRGUI', **kwargs):
        super(VRChgcar, self).__init__(GUI_type, title, resizable=True, keep_on_top=False, theme=theme, **kwargs)
        VRPrint.__init__(self)
        self.directory = directory
        self.event, self.value = None, None
        self.folder = folder
        self.window['-CHGCAR-FILENAME-'].update(f'Folder: {self.folder}')
        self.theme = theme
        self.incar_name, self.chgcar_name = '', ''
        self.chgcar_array, self.atoms_number, self.values, self.basis = np.array([]), atoms_number, [], basis
        self.color = [1.0, 1.0, 1.0, 1.0]
        self.transparent = 1.0
        self.array_shape, self.points_to_draw, self.coordinates_array = (0,), [], []
        self.mode, self.draw_mode = None, 'Points'
        self.load_model, self.draw_model = False, False
        self.close = False
        if atoms_number is not None and basis is not None:
            incar_normal, chgcar_normal = self.incar_check(), self.chgcar_check()
            if not (incar_normal and chgcar_normal):
                self.close = True
                self.window.close()
            else:
                self.window.un_hide()
        else:
            self.close = True
            self.window.close()

    def __bool__(self):
        return not self.close

    def incar_check(self):
        files = os.listdir(self.directory)
        files = [file for file in files if 'INCAR' in file]
        repeat = len(files)
        if repeat > 1:
            filename = ''
            window = VRGUI(GUI_type=file_choose_window, title='VaspReader', theme=self.theme).window_return()
            window['CHOSE'].update(files)
            while True:
                event, value = window.read()
                if event == sg.WINDOW_CLOSED:
                    window.close()
                    break
                if event == 'SUBMIT':
                    filename = value['CHOSE'][0]
                    window.close()
                    break
            if filename:
                self.incar_name = filename
        elif repeat == 1:
            self.incar_name = files[0]
        else:
            return False
        lcharge_line = False
        spin_polarized = False
        with open(f'{self.directory}\\{self.incar_name}', 'r') as incar:
            while True:
                line = incar.readline()
                if not line:
                    break
                if 'LCHARG' in line and 'TRUE' in line and not '#' in line:
                    lcharge_line = True
                if 'ISPIN' in line and '2' in line and not '#' in line:
                    spin_polarized = True
                if spin_polarized and lcharge_line:
                    break
        if spin_polarized and lcharge_line:
            return True
        else:
            return False

    def chgcar_check(self):
        files = os.listdir(self.directory)
        files = [file for file in files if 'CHGCAR' in file]
        repeat = len(files)
        if repeat > 1:
            filename = ''
            window = VRGUI(GUI_type=file_choose_window, title='VaspReader', theme=self.theme).window_return()
            window['CHOSE'].update(files)
            while True:
                event, value = window.read()
                if event == sg.WINDOW_CLOSED:
                    window.close()
                    break
                if event == 'SUBMIT':
                    filename = value['CHOSE'][0]
                    window.close()
                    break
            if filename:
                self.chgcar_name = filename
                return True
        elif repeat == 1:
            self.chgcar_name = files[0]
            return True
        else:
            return False

    def chgcar_read(self):
        can_read, can_read_array_shape = False, False
        array_shape, number_of_array_elements, read_count = None, -1, 0
        array, abs_array = np.array([]), []
        atoms_count, preread_lines, preread_lines_count, to_skip = 0, 0, 0, 0
        values = set()
        self.window['-CHGCAR-STATUS-'].update('reading of values.')
        self.window['-CHGCAR-PROGRESS-'].update(current_count=1)
        with open(f'{self.directory}\\{self.chgcar_name}', 'r') as chgcar:
            while True:
                line = chgcar.readline()
                if not line:
                    break
                if self.mode == 'Spin Up + Spin Down':
                    if can_read and can_read_array_shape:
                        self.array_shape = list(map(int, line.split()))
                        number_of_array_elements = self.array_shape[0] * self.array_shape[1] * self.array_shape[2]
                        array = np.zeros(number_of_array_elements)
                        can_read_array_shape = False
                        continue
                    elif can_read and not can_read_array_shape:
                        split_line = line.split()
                        for num, element in enumerate(split_line):
                            element = float(element)
                            power = -math.floor(math.log10(abs(element)))
                            element = round(element, power)
                            array[read_count + num] = element
                            values.add(element)
                        read_count += len(split_line)
                        if read_count == number_of_array_elements:
                            self.window['-CHGCAR-PROGRESS-'].update(current_count=2)
                            self.window['-CHGCAR-STATUS-'].update('forming of array.')
                            break
                    if not line.strip() and not can_read:
                        can_read = True
                        can_read_array_shape = True
                elif self.mode == 'Spin Up - Spin Down':
                    if 'augmentation occupancies' in line:
                        atoms_count += 1
                    if atoms_count == self.atoms_number:
                        to_skip = math.ceil(int(line.split()[-1]) / 5)
                        can_read_array_shape = True
                        preread_lines = math.ceil(atoms_count / 5)
                        atoms_count = 0
                        continue
                    if to_skip:
                        to_skip -= 1
                        continue
                    if not can_read and can_read_array_shape:
                        preread_lines_count += 1
                        if preread_lines_count == preread_lines:
                            can_read = True
                            preread_lines_count = 0
                            continue
                    if can_read and can_read_array_shape:
                        self.array_shape = list(map(int, line.split()))
                        number_of_array_elements = self.array_shape[0] * self.array_shape[1] * self.array_shape[2]
                        array = np.zeros(number_of_array_elements)
                        can_read_array_shape = False
                        continue
                    elif can_read and not can_read_array_shape:
                        split_line = line.split()
                        for num, element in enumerate(split_line):
                            element = float(element)
                            power = -math.floor(math.log10(abs(element)))
                            element = round(element, power)
                            array[read_count + num] = element
                            values.add(element)
                        read_count += len(split_line)
                        if read_count == number_of_array_elements:
                            self.window['-CHGCAR-PROGRESS-'].update(current_count=2)
                            self.window['-CHGCAR-STATUS-'].update('forming of array.')
                            break
        self.chgcar_array = array.reshape(tuple(self.array_shape))
        self.values = sorted(values)
        self.window['-CHGCAR-VALUE-'].update(range=(0, len(self.values) - 1), value=0, disabled=False)
        self.window['-CHGCAR-VALUE-SHOW-'].update(f'{self.values[0]: .1e}')
        self.window['-CHGCAR-PROGRESS-'].update(current_count=3)
        self.window['-CHGCAR-STATUS-'].update('done.')

    def form_coordinates_array_to_draw_points(self):
        x, y, z = np.where(self.chgcar_array == self.values[int(self.value["-CHGCAR-VALUE-"])])
        self.coordinates_array.clear()
        [self.coordinates_array.append(np.dot(np.array([(z[i] / (self.array_shape[0] - 1) - 0.5), (y[i] / (self.array_shape[1] - 1) - 0.5), (x[i] / (self.array_shape[2] - 1) - 0.5)]), self.basis).tolist()) for i in range(x.shape[0])]

    def mainloop(self):
        self.event, self.value = self.window.read(timeout=10)
        if self.event == '-CHGCAR-CLOSE-' or self.event == sg.WINDOW_CLOSED:
            self.window.close()
            self.coordinates_array.clear()
            self.close = True
        if self.event == '-CHGCAR-DRAW-MODE-':
            self.draw_mode = self.value['-CHGCAR-DRAW-MODE-']
        if self.event == '-CHGCAR-READ-':
            self.mode = self.value['-CHGCAR-READ-MODE-']
            self.chgcar_read()
        if self.event == '-CHGCAR-TRANSPARENT-':
            self.transparent = self.value['-CHGCAR-TRANSPARENT-'] / 100
            self.color = tuple(self.color[:3]) + (1.0 - self.transparent, )
        if self.event == '-CHGCAR-COLOR-':
            if self.value['-CHGCAR-COLOR-'] != 'None':
                self.color = self.value['-CHGCAR-COLOR-']
                self.window['-CHGCAR-COLOR-BUTTON-'].update(button_color=self.color)
                self.color = matcol.to_rgba(self.color, alpha=1.0 - self.transparent)
        if self.event == '-CHGCAR-VALUE-':
            self.window['-CHGCAR-VALUE-SHOW-'].update(f'{self.values[int(self.value["-CHGCAR-VALUE-"])]: .1e}')
        if self.event == '-CHGCAR-DRAW-':
            if self.draw_mode == 'Isosurface':
                # self.points_to_draw = np.where(self.chgcar_array == self.values[int(self.value["-CHGCAR-VALUE-"])], 1.0, 0.0)
                rgba = np.zeros((*self.array_shape, 4))
                self.points_to_draw = np.where(self.chgcar_array == self.values[int(self.value["-CHGCAR-VALUE-"])])
                rgba[self.points_to_draw[0], self.points_to_draw[1], self.points_to_draw[2]] = [*self.color]
                self.points_to_draw = rgba
            elif self.draw_mode == 'Points':
                self.form_coordinates_array_to_draw_points()
            self.load_model, self.draw_model = True, True


# VRChgcar(r'C:\Users\AlexS\OneDrive\Рабочий стол\Учеба\Научная работа\К диплому\POSS_Ar_90_down_12_5_eV_after', 32, np.array([[20.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 20.0]])).mainloop()
