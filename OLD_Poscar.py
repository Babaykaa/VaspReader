import os
import numpy as np
from collections import Counter
import PySimpleGUI as sg
from OLD_Print import VRPrint
from OLD_GUI import VRGUI
from OLD_GUI import poscar_mode_GUI
from OLD_GUI import file_choose_window
from OLD_MD import VRMD


class VRPoscarForm(VRGUI, VRPrint):
    def __init__(self, calculation, GUI_type=poscar_mode_GUI, title='VaspReader', theme='VRGUI'):
        super(VRPoscarForm, self).__init__(GUI_type, title, resizable=False, keep_on_top=False, theme=theme)
        VRPrint.__init__(self)
        self.event, self.value = None, None
        self.calculation, self.fix_array, self.velocities = calculation, np.array([]), np.array([])
        self.steps = self.calculation['STEPS']
        self.step, self.closed = 0, False
        self.cartesian, self.direct, self.basis_matrix = [], [], self.calculation['BASIS']
        self.window['MaxStep'].update(f'Max step: {self.steps - 2}')

    def direct_to_cartesian(self):
        self.cartesian = np.dot(self.direct, self.basis_matrix)

    def basis_to_string(self):
        """Convert basis array to string format."""
        return ''.join('    ' + '    '.join(map(lambda x: '{:.8f}'.format(x), self.basis_matrix[line])) + '\n' for line in range(3))

    @staticmethod
    def atoms_string(key_p, value_p):
        """Convert list of atoms names and their count to string."""
        p_str = '    ' + ''.join(map(lambda x: '{:5}'.format(x), key_p)) + '\n'
        p_str += ''.join(map(lambda x: '{:5}'.format(x), value_p)) + '\n'
        return p_str

    def array_to_string(self, if_fixed, cartesian) -> str:
        """Convert array of coordinates into string."""
        key = 'POSITIONS' if cartesian else 'DIRECT'
        self.direct = self.calculation['DIRECT'][self.step]
        if key == 'POSITIONS':
            self.direct_to_cartesian()
        array = self.cartesian if key == 'POSITIONS' else self.direct
        if not if_fixed:
            return ''.join([f'  {line[0]:24.18f}{line[1]:24.18f}{line[2]:24.18f}\n' for line in array]) + '\n'
        else:
            return ''.join([f'  {line[0]:24.18f}{line[1]:24.18f}{line[2]:24.18f} {self.fix_array[num][0]:2}{self.fix_array[num][1]:2}{self.fix_array[num][2]:2}\n' for num, line in enumerate(array)]) + '\n'

    def calculate_velocities(self):
        self.velocities = (self.calculation['POSITIONS'][self.step + 1] - self.calculation['POSITIONS'][self.step]) / self.calculation['POTIM']

    def velocities_to_string_POSCAR(self):
        """Calculate numpy array of velocities and convert array into string."""
        return ''.join('  ' + ''.join(map(lambda x: '{:24.18f}'.format(x), self.velocities[line])) + '\n' for line in range(len(self.velocities)))

    def fix_coordinates(self):
        """Find velocities of atoms and if velocity equals 0 fix projection of coordinate in resulting POSCAR. Use with
           caution because of possible program mistakes in this aspect of VaspReader working. Returns numpy array object."""
        fix_list = []
        for index, atom in enumerate(self.velocities):
            fix_list_step = []
            [fix_list_step.append('F') if self.velocities[index][proj] == 0. else fix_list_step.append('T') for proj in range(3)]
            fix_list.append(fix_list_step.copy())
            fix_list_step.clear()
        self.fix_array = np.array(fix_list)

    def close(self):
        if not self.window.is_closed():
            self.window.close()

    def is_closed(self):
        return self.closed

    def mainloop(self):
        self.event, self.value = self.window.read(timeout=5)
        if self.event == 'ExitPOSCAR' or self.event == sg.WIN_CLOSED:
            self.closed = True
            self.window.close()
        if self.event == 'StepPOSCAR' and self.value['StepPOSCAR']:
            try:
                in_as_int = int(self.value['StepPOSCAR'])
                if in_as_int == 0:
                    self.window['StepPOSCAR'].update('')
                if in_as_int > self.steps - 2 and not len(self.value['StepPOSCAR']) == 1:
                    self.window['StepPOSCAR'].update(self.value['StepPOSCAR'][:-1])
                elif in_as_int > self.steps - 2 and len(self.value['StepPOSCAR']) == 1:
                    self.window['StepPOSCAR'].update('')
            except:
                if not len(self.value['StepPOSCAR']) == 1:
                    self.window['StepPOSCAR'].update(self.value['StepPOSCAR'][:-1])
        if self.event == 'CreatePOSCAR':
            if self.value['StepPOSCAR'] and self.value['POSCARsave']:
                self.step = int(self.value['StepPOSCAR'])
                if os.path.exists(f'{self.value["POSCARsave"]}/POSCAR'):
                    old_count = 0
                    while os.path.exists(f'{self.value["POSCARsave"]}/POSCAR_old({str(old_count)})'):
                        old_count += 1
                    os.rename(f'{self.value["POSCARsave"]}/POSCAR', f'{self.value["POSCARsave"]}/POSCAR_old({str(old_count)})')
                with open(f'{self.value["POSCARsave"]}/POSCAR', 'w') as POSCAR_f:
                    POSCAR_f.write(self.value["POSCARsave"].split('/')[-1] + '\n')
                    POSCAR_f.write('   1.00000000000000\n')
                    POSCAR_f.write(self.basis_to_string())
                    lab_dict = Counter(self.calculation['ATOMNAMES'])
                    p_atoms, p_count = [], []
                    for p_key, p_value in lab_dict.items():
                        p_atoms.append(p_key)
                        p_count.append(p_value)
                    POSCAR_f.write(self.atoms_string(p_atoms, p_count))
                    POSCAR_f.write('Selective dynamics\n')
                    if self.value['Coord'] == 'Cartesian':
                        self.calculate_velocities()
                        POSCAR_f.write('Cartesian\n')
                        if not self.value['FixCoord']:
                            POSCAR_f.write(self.array_to_string(False, True))
                        else:
                            self.fix_coordinates()
                            POSCAR_f.write(self.array_to_string(True, True))
                    else:
                        self.calculate_velocities()
                        POSCAR_f.write('Direct\n')
                        if not self.value['FixCoord']:
                            POSCAR_f.write(self.array_to_string(False, False))
                        else:
                            self.fix_coordinates()
                            POSCAR_f.write(self.array_to_string(True, False))
                    POSCAR_f.write(self.velocities_to_string_POSCAR())
                self.print(f'File {self.value["POSCARsave"]}/POSCAR successfully created.')
            elif self.value['StepPOSCAR'] and not self.value['POSCARsave']:
                self.popup('Input folder to save POSCAR before this operation.', title='Input folder.')
            elif not self.value['StepPOSCAR'] and self.value['POSCARsave']:
                self.popup('Input step before this operation.', title='Input step.')
            else:
                self.popup('Input folder to save POSCAR and step before this operation.', title='Input folder and step.')


class VRPoscarView(VRPrint):
    def __init__(self, directory, theme='VRGUI'):
        VRPrint.__init__(self)
        self.theme = theme
        self.calculation = dict()
        self.directory = directory
        self.filenames = list(filter(lambda x: 'POSCAR' in x or 'CONTCAR' in x, os.listdir(self.directory)))
        self.atoms_count_all, self.poscar_path, self.basis_scaling = 0, '', 1
        self.velocities, self.cartesian, self.direct, self.fixation, self.atoms_count, self.basis_matrix, self.atoms_names = [], [], [],  [], [], [], []
        self.basis_inverse_matrix = []
        if not self.filenames:
            self.popup('Input folder has not exist POSCAR/CONTCAR files.', title='POSCAR/CONTCAR not found.')
        else:
            if len(self.filenames) > 1:
                filename = ''
                window = VRGUI(GUI_type=file_choose_window, title='VaspReader', theme=self.theme).window_return()
                window['CHOSE'].update(self.filenames)
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
                    self.poscar_path = f'{self.directory}/{filename}'
                    self.coordinates_read()
                    self.dictionary_form()
            else:
                self.poscar_path = f'{self.directory}/{self.filenames[0]}'
                self.coordinates_read()
                self.dictionary_form()

    # noinspection PyUnresolvedReferences
    def coordinates_read(self):
        coordinate_index = -1
        cartesian = True
        with open(self.poscar_path, 'r') as poscar:
            for index, line in enumerate(poscar):
                if index == 1:
                    self.basis_scaling = float(line.split()[0])
                elif 1 < index < 5:
                    self.basis_matrix.append(list(map(float, line.split())))
                elif index == 5:
                    self.basis_matrix = np.array(self.basis_matrix)
                    self.atoms_names = line.split()
                elif index == 6:
                    self.atoms_count = list(map(int, line.split()))
                    self.atoms_count_all = sum(self.atoms_count)
                elif index == 7 or index == 8:
                    mode = line.split()[0].lower()[0]
                    if 'c' or 'd' in mode:
                        coordinate_index = index + 1
                        cartesian = True if 'c' in mode else False
                elif coordinate_index <= index < coordinate_index + self.atoms_count_all:
                    coordinates_info = line.split()
                    if len(coordinates_info) == 3:
                        self.cartesian.append(list(map(float, coordinates_info))) if cartesian else self.direct.append(list(map(lambda x: float(x) - 0.5, coordinates_info)))
                    else:
                        self.cartesian.append(list(map(float, coordinates_info[:3]))) if cartesian else self.direct.append(list(map(lambda x: float(x) - 0.5, coordinates_info[:3])))
                        self.fixation.append(coordinates_info[3:])
                elif coordinate_index + self.atoms_count_all < index <= coordinate_index + 2 * self.atoms_count_all and self.atoms_count_all:
                    velocities_line = line.split()
                    if velocities_line:
                        self.velocities.append(list(map(float, velocities_line)))
        self.cartesian = np.array([self.cartesian])
        self.direct = np.array([self.direct])
        self.velocities = np.array([self.velocities])
        self.basis_inverse_matrix = np.linalg.inv(self.basis_matrix)
        self.cartesian_to_direct() if cartesian else self.direct_to_cartesian()

    def direct_to_cartesian(self):
        self.cartesian = np.array([np.dot(self.direct[0], self.basis_matrix)])

    def cartesian_to_direct(self):
        self.direct = np.array([np.dot(self.cartesian[0], self.basis_inverse_matrix)])
        if self.cartesian.min() >= 0.:
            self.direct[0] = self.direct[0] - 0.5
            self.direct_to_cartesian()

    def dictionary_form(self):
        cube_vert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
        self.calculation = {'STEPS': 0, 'DIRECTORY': self.poscar_path, 'POSITIONS': self.cartesian, 'BASIS': self.basis_matrix, 'ATOMNUMBER': self.atoms_count_all, 'DIRECT': self.direct, 'BASIS_VERT': np.dot(cube_vert, self.basis_matrix), 'ATOMNAMES': [self.atoms_names[count] for count in range(len(self.atoms_count)) for _ in range(self.atoms_count[count])]}
        self.calculation['ID'] = [f"{self.calculation['ATOMNAMES'][index]}_{index + 1}" for index in range(len(self.calculation['ATOMNAMES']))]
        VRMD.color_choose(self.calculation)

    def return_calculation(self):
        return self.calculation if self.poscar_path else dict()
