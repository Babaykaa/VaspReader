import os
import copy
import random
import numpy as np
from Logs.VRLogger import sendDataToLogger


def deleted_positions_to_none(direct_positions_array, positions_array):
    for step in range(len(direct_positions_array)):
        for atom in range(len(direct_positions_array[step])):
            for proj in range(len(direct_positions_array[step][atom])):
                if direct_positions_array[step][atom][proj] == 10.:
                    positions_array[step][atom][proj] = None


def atoms_info_filling(dictionary):
    dictionary['RADII'] = []
    for _, name in enumerate(set(dictionary['ATOMNAMES'])):
        dictionary['ATOMSINFO'][name] = {'COLORVALUE': [], 'RADII': 1, 'FILLED': False}

    for i in range(dictionary['ATOMNUMBER']):
        atom = dictionary['ATOMNAMES'][i]
        now_filling_atom = dictionary['ATOMSINFO'][dictionary['ATOMNAMES'][i]]
        if not now_filling_atom['FILLED']:
            if atom == 'O':
                now_filling_atom['COLORVALUE'] = np.asarray([1, 0, 0]) # 'red'
                now_filling_atom['RADII'] = 0.3
            elif atom == 'Si':
                now_filling_atom['COLORVALUE'] = np.asarray([1, 1, 0])  # 'yellow'
                now_filling_atom['RADII'] = 0.4
            elif atom == 'H':
                now_filling_atom['COLORVALUE'] = np.asarray([0.5, 0.5, 0.5])  # 'gray'
                now_filling_atom['RADII'] = 0.2
            elif atom == 'C':
                now_filling_atom['COLORVALUE'] = np.asarray([0.2, 0.2, 0.2])  # 'black'
                now_filling_atom['RADII'] = 0.33
            elif atom == 'He':
                now_filling_atom['COLORVALUE'] = np.asarray([0, 1, 0])  # 'green'
                now_filling_atom['RADII'] = 0.18
            elif atom == 'Ar':
                now_filling_atom['COLORVALUE'] = np.asarray([0.6, 0, 0.6])  # 'purple'
                now_filling_atom['RADII'] = 0.34
            elif atom == 'Xe':
                now_filling_atom['COLORVALUE'] = np.asarray([0.05, 0, 0.6])  # 'blue'
                now_filling_atom['RADII'] = 0.38
            elif atom == 'Mo':
                now_filling_atom['COLORVALUE'] = np.asarray([0, 0.78, 0.78]) # old violet 0.63, 0, 0.63 '#00c6c6' #a100a1
                now_filling_atom['RADII'] = 0.5
            elif atom == 'S':
                now_filling_atom['COLORVALUE'] = np.asarray([1.0, 1.0, 0])  # '#ffff00'
                now_filling_atom['RADII'] = 0.36
            elif atom == 'N':
                now_filling_atom['COLORVALUE'] = np.asarray([0, 0, 1]) # old light blue '#0000ff'
                now_filling_atom['RADII'] = 0.24
            elif atom == 'Ne':
                now_filling_atom['COLORVALUE'] = np.asarray([0.543, 0.27, 0.07])  # '#8b4513'
                now_filling_atom['RADII'] = 0.16
            elif atom == 'Cl':
                now_filling_atom['COLORVALUE'] = np.asarray([0.12, 0.77, 0.65])  # '1fc4a6'
                now_filling_atom['RADII'] = 0.3
            else:
                r, g, b = random.random(), random.random(), random.random()
                rad = random.uniform(0.24, 0.42)
                now_filling_atom['COLORVALUE'] = np.asarray([r, g, b])
                now_filling_atom['RADII'] = rad
            now_filling_atom['FILLED'] = True


    for i in range(dictionary['ATOMNUMBER']):
        dictionary['RADII'].append(dictionary['ATOMSINFO'][dictionary['ATOMNAMES'][i]]['RADII'])
    return dictionary


def form_atoms_with_nums_dict(parser_parameters):
    parser_parameters['ATOM-NUMBERS'] = dict()
    for uniq_atom in set(parser_parameters['ATOMNAMES']):
        for number, atom in enumerate(parser_parameters['ATOMNAMES']):
            if atom == uniq_atom:
                stripped_atom = uniq_atom.rstrip()
                if stripped_atom in parser_parameters['ATOM-NUMBERS']:
                    parser_parameters['ATOM-NUMBERS'][stripped_atom].append(number)
                else:
                    parser_parameters['ATOM-NUMBERS'][stripped_atom] = [number]
    for key in parser_parameters['ATOM-NUMBERS']:
        parser_parameters['ATOM-NUMBERS'][key] = np.array(parser_parameters['ATOM-NUMBERS'][key])


class VRMD:

    @sendDataToLogger
    def __init__(self, directory, logger):
        self.__logger = logger
        self.different_calculations = False
        self._parser_parameters = {'DIRECTORY': directory, 'ATOMSINFO': dict(), 'CALC_TYPE': 'VASP'}
        self.XMLLIST = []
        vaspnum, self.breaker, self.no_vaspruns = 0, False, False
        try:
            for vaspfile in os.listdir(directory):
                if vaspfile.endswith('.xml'):
                    vaspnum += 1
                    self._parser_parameters[vaspfile] = {'ATOMNAMES': [], 'ATOMNUMBER': 0, 'POMASS': [], 'POSITIONS': [], 'POTIM': 0., 'TYPE': []}
                    self.XMLLIST.append(vaspfile)
        except AttributeError:
            pass
        self.XMLLIST.sort()
        self._parser_parameters['XMLLIST'] = self.XMLLIST
        if vaspnum == 0:
            self.breaker = True
            self.__logger
        elif vaspnum != 0:
            for v_ind in range(len(self.XMLLIST)):
                POTIM_read, BASIS_read = True, True
                first_read_check, first_cord_read = True, True
                vaspdir = directory + '\\' + self.XMLLIST[v_ind]
                with open(vaspdir, 'r') as VASP:
                    while True:
                        line = VASP.readline()
                        if not line:
                            break
                        if '<atoms>' in line:
                            self._parser_parameters[self.XMLLIST[v_ind]]['ATOMNUMBER'] = int(line.split()[1])
                        if '<field type="int">atomtype</field>' in line:
                            VASP.readline()
                            for index in range(self._parser_parameters[self.XMLLIST[v_ind]]['ATOMNUMBER']):
                                atomtype = VASP.readline()
                                self._parser_parameters[self.XMLLIST[v_ind]]['ATOMNAMES'].append((atomtype.split('>')[2]).split('<')[0])
                                self._parser_parameters[self.XMLLIST[v_ind]]['TYPE'].append(int(atomtype.split('<')[4].split('>')[1]))
                        if POTIM_read and 'name="POTIM">' in line:
                            self._parser_parameters[self.XMLLIST[v_ind]]['POTIM'] = float(line.split()[2].split('<')[0])
                            POTIM_read = False
                        if 'name="POMASS">' in line:
                            for mass in line.split()[2:-1]:
                                self._parser_parameters[self.XMLLIST[v_ind]]['POMASS'].append(float(mass))
                            self._parser_parameters[self.XMLLIST[v_ind]]['POMASS'].append(float((line.split()[-1]).split('<')[0]))
                        if '<varray name="positions" >' in line:  # <varray name="positions" >
                            try:
                                if first_read_check:
                                    first_read_check = False
                                else:
                                    array = [list(map(float, VASP.readline().split()[1:4])) for _ in range(self._parser_parameters[self.XMLLIST[v_ind]]['ATOMNUMBER'])]
                                    if first_cord_read:
                                        self._parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'].append(array)
                                        first_cord_read = False
                                    if array != self._parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'][-1]:
                                        self._parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'].append(array)
                            except:
                                self.breaker = True
                        if BASIS_read and '<varray name="basis" >' in line:
                            basis_str = [VASP.readline() for _ in range(3)]
                            basis = [list(map(float, basis_str[index].split()[1:4])) for index in range(len(basis_str))]
                            self._parser_parameters[self.XMLLIST[v_ind]]['BASIS'] = basis
                            BASIS_read = False
                self._parser_parameters[self.XMLLIST[v_ind]]['VASPLEN'] = len(self._parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'])
            self._parser_parameters['MASSES'] = [self._parser_parameters[self.XMLLIST[0]]['POMASS'][index - 1] for index in self._parser_parameters[self.XMLLIST[0]]['TYPE']]
            self._parser_parameters['STEPS_LIST'] = [self._parser_parameters[self.XMLLIST[0]]['VASPLEN']]
            for xml in self.XMLLIST[1:]:
                self._parser_parameters['STEPS_LIST'].append(self._parser_parameters['STEPS_LIST'][-1] + self._parser_parameters[xml]['VASPLEN'] - 1)
            self._parser_parameters['STEPS'] = sum([self._parser_parameters[xml]['VASPLEN'] for xml in self.XMLLIST]) - len(self.XMLLIST) + 1
            self._parser_parameters['ATOMNAMES'] = self._parser_parameters[self.XMLLIST[0]]['ATOMNAMES']
            form_atoms_with_nums_dict(self._parser_parameters)
            self.removed_atoms_find(self._parser_parameters)
            self.position_array_form(self._parser_parameters)
            self._parser_parameters['POTIM'] = [self._parser_parameters[xml_file]['POTIM'] for xml_file in self._parser_parameters['XMLLIST']]
            if not self.breaker:
                try:
                    self._parser_parameters['POSITIONS'] = np.array(self._parser_parameters['POSITIONS'])
                    self._parser_parameters['BASIS'] = self._parser_parameters[self._parser_parameters['XMLLIST'][0]]['BASIS']
                    self._parser_parameters['ATOMNUMBER'] = self._parser_parameters[self._parser_parameters['XMLLIST'][0]]['ATOMNUMBER']
                    for i in range(self._parser_parameters['ATOMNUMBER']):
                        if self._parser_parameters['ATOMNAMES'][i][-1] == ' ':
                            self._parser_parameters['ATOMNAMES'][i] = self._parser_parameters['ATOMNAMES'][i][:-1]
                    self._parser_parameters['BASIS'] = np.array(self._parser_parameters['BASIS'])
                    cube_vert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                                 [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5],
                                 [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
                    # Создание вершин границы ячейки
                    self._parser_parameters['BASIS_VERT'] = np.dot(np.asarray(cube_vert), self._parser_parameters['BASIS'])
                    self._parser_parameters['DIRECT'] = np.copy(self._parser_parameters['POSITIONS'])
                    self._parser_parameters['POSITIONS'] = self._parser_parameters['POSITIONS'] - 0.5
                    # Преобразование координат из дискретных в декартовы в соответствии с базисом
                    for m in range(self._parser_parameters['STEPS']):
                        self._parser_parameters['POSITIONS'][m] = np.dot(self._parser_parameters['POSITIONS'][m], self._parser_parameters['BASIS'])
                    deleted_positions_to_none(self._parser_parameters['DIRECT'], self._parser_parameters['POSITIONS'])
                    self._parser_parameters = atoms_info_filling(self._parser_parameters)
                    self._parser_parameters['ID'] = [self._parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1) for ind in range(self._parser_parameters['ATOMNUMBER'])]
                    self._parser_parameters['ID-TO-NUM'] = {self._parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1): ind for ind in range(self._parser_parameters['ATOMNUMBER'])}
                except KeyError:
                    self.breaker = True

    def get_logger(self):
        return self.__logger

    def __call__(self, *args, **kwargs):
        return self._parser_parameters

    def removed_atoms_find(self, dictionary):
        XML = dictionary.get('XMLLIST')
        self.breaker = False
        if len(XML) > 1:
            for file in range(len(XML) - 1):
                index_f2, differ = 0, []
                for f1_element in dictionary[XML[file]]['POSITIONS'][-1]:
                    if f1_element == dictionary[XML[file + 1]]['POSITIONS'][0][index_f2]:
                        index_f2 += 1 if index_f2 < len(dictionary[XML[file + 1]]['POSITIONS'][0]) - 1 else 0
                        differ.append(False)
                        continue
                    else:
                        differ.append(True)
                dictionary[XML[file + 1]]['REMOVED'] = differ
                if file != 0:
                    for index in range(len(dictionary[XML[file]]['REMOVED'])):
                        if dictionary[XML[file]]['REMOVED'][index]:
                            dictionary[XML[file + 1]]['REMOVED'].insert(index, True)
                if sum(differ) != dictionary[XML[0]]['ATOMNUMBER'] - dictionary[XML[file + 1]]['ATOMNUMBER']:
                    self.different_calculations = True
                    self.breaker = True

    @ staticmethod
    def position_array_form(dictionary):
        XML = dictionary['XMLLIST']
        dictionary['POSITIONS'] = copy.deepcopy(dictionary[XML[0]]['POSITIONS'])
        for positions in range(1, len(XML)):
            for different_pos in range(len(dictionary[XML[positions]]['REMOVED'])):
                if dictionary[XML[positions]]['REMOVED'][different_pos]:
                    for array_value in range(len(dictionary[XML[positions]]['POSITIONS'])):
                        dictionary[XML[positions]]['POSITIONS'][array_value].insert(different_pos, [10., 10., 10.])
            dictionary['POSITIONS'] += dictionary[XML[positions]]['POSITIONS'][1:]


class QEMD:
    __atomic_units_distance_constant = 1.889725988579

    def __init__(self, directory, logger):
        self.__logger = logger
        self.directory = directory
        self.calculation_files = dict()
        self.dir_to_read_files = None
        self.input_file = None
        self.breaker = False
        self.number_of_atom_types = 0
        self._parser_parameters = {'DIRECTORY': directory, 'ATOMNAMES': [], 'ATOMSINFO': dict(), 'POTIM': [], 'STEPS_LIST': [], 'POSITIONS': [], 'POMASS': [], 'MASSES': [], 'CALC_TYPE': 'QE'}
        if self.check_for_QE_files(self.directory):
            self.read_cell_file()
            self.read_coord_file()
            self.read_input_file()
            form_atoms_with_nums_dict(self._parser_parameters)
            self._parser_parameters = atoms_info_filling(self._parser_parameters)
            self._parser_parameters['ID'] = [self._parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1) for ind in range(self._parser_parameters['ATOMNUMBER'])]
            self._parser_parameters['ID-TO-NUM'] = {self._parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1): ind for ind in range(self._parser_parameters['ATOMNUMBER'])}
        else:
            self.breaker = True

    def get_logger(self):
        return self.__logger

    def __call__(self, *args, **kwargs):
        return self._parser_parameters

    def cartesian_to_direct(self):
        self._parser_parameters['DIRECT'] = np.array([np.dot(self._parser_parameters['POSITIONS'], np.linalg.inv(self._parser_parameters['BASIS']))])[0]
        self._parser_parameters['DIRECT'] = self._parser_parameters['DIRECT'] - 0.5
        self.direct_to_cartesian()

    def direct_to_cartesian(self):
        self._parser_parameters['POSITIONS'] = np.array([np.dot(self._parser_parameters['DIRECT'], self._parser_parameters['BASIS'])])[0]

    def check_for_QE_files(self, directory):
        files = os.listdir(directory)
        folders = []
        requirements = ['vel', 'pos', 'cel']
        for file in files:
            extension = file.split('.')[-1]
            if extension == file and os.path.isdir(directory + '\\' + file):
                folders.append(file)
            elif extension == 'in':
                self.input_file = file
            elif extension in requirements:
                requirements.remove(extension)
                self.calculation_files[extension] = file
        if not requirements:
            self.dir_to_read_files = directory
            return True
        else:
            for folder in folders:
                result = self.check_for_QE_files(directory + '\\' + folder)
                if result:
                    return True
            return False

    def read_coord_file(self):
        steps_counter = 0
        now_potim = None
        prev_time = None
        temp_array = []
        with open(self.dir_to_read_files + '\\' + self.calculation_files['pos']) as coord:
            while True:
                line = coord.readline()
                line_info = line.split()
                if not line:
                    break
                if len(line_info) == 2:
                    if now_potim is None:
                        now_potim = float(line_info[-1])
                        prev_time = now_potim
                        self._parser_parameters['POTIM'].append(now_potim)
                    else:
                        now_time = float(line_info[-1])
                        if round((now_time - prev_time), 6) != round(now_potim, 6):
                            now_potim = now_time - prev_time
                            self._parser_parameters['STEPS_LIST'].append(steps_counter)
                            self._parser_parameters['POTIM'].append(now_potim)
                        prev_time = now_time
                    steps_counter += 1
                    if temp_array:
                        self._parser_parameters['POSITIONS'].append(temp_array)
                        temp_array = []
                else:
                    temp_array.append(list(map(float, line_info)))
        self._parser_parameters['STEPS_LIST'].append(steps_counter)
        self._parser_parameters['STEPS'] = steps_counter - 1
        self._parser_parameters['POSITIONS'] = np.array(self._parser_parameters['POSITIONS']) / self.__atomic_units_distance_constant
        self.cartesian_to_direct()

    def read_cell_file(self):
        with open(self.dir_to_read_files + '\\' + self.calculation_files['cel']) as cell:
            cell.readline()
            self._parser_parameters['BASIS'] = np.array([list(map(float, cell.readline().split())), list(map(float, cell.readline().split())), list(map(float, cell.readline().split()))])
            self._parser_parameters['BASIS'] = self._parser_parameters['BASIS'] / self.__atomic_units_distance_constant
            cube_vert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                         [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5],
                         [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
            # Создание вершин границы ячейки
            self._parser_parameters['BASIS_VERT'] = np.dot(np.asarray(cube_vert), self._parser_parameters['BASIS'])

    def read_input_file(self):
        mass_count = 0
        with open(self.directory + '\\' + self.input_file) as inp:
            while True:
                line = inp.readline()
                if not line:
                    break
                elif 'nat' in line:
                    self._parser_parameters['ATOMNUMBER'] = int(line.split('nat')[-1].split()[1].split(',')[0])
                elif 'ntyp' in line:
                    self.number_of_atom_types = int(line.split('ntyp')[-1].split()[1].split(',')[0])
                elif 'ATOMIC_SPECIES' in line:
                    for _ in range(self.number_of_atom_types):
                        info = inp.readline().split()[:2]
                        self._parser_parameters['POMASS'].append(float(info[-1].split('d')[0]))
                elif 'ATOMIC_POSITIONS' in line:
                    for _ in range(self._parser_parameters['ATOMNUMBER']):
                        info = inp.readline().split()[0]
                        self._parser_parameters['ATOMNAMES'].append(info)
                        if len(self._parser_parameters['ATOMNAMES']) > 1 and self._parser_parameters['ATOMNAMES'][-1] != self._parser_parameters['ATOMNAMES'][-2]:
                            mass_count += 1
                        self._parser_parameters['MASSES'].append(self._parser_parameters['POMASS'][mass_count])



QEMD(r'C:\Users\AlexS\Documents\Science_work\QuantumEspresso\POSS_with_He')
