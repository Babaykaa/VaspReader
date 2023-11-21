import os
import copy
import random
import numpy as np


class VRMD:
    def __init__(self, directory):
        self.different_calculations = False
        self.parser_parameters = {'DIRECTORY': directory}
        self.XMLLIST = []
        vaspnum, self.breaker, self.no_vaspruns = 0, False, False
        try:
            for vaspfile in os.listdir(directory):
                if vaspfile.endswith('.xml'):
                    vaspnum += 1
                    self.parser_parameters[vaspfile] = {'ATOMNAMES': [], 'ATOMNUMBER': 0, 'POMASS': [], 'POSITIONS': [], 'POTIM': 0., 'TYPE': []}
                    self.XMLLIST.append(vaspfile)
        except AttributeError:
            pass
        self.XMLLIST.sort()
        self.parser_parameters['XMLLIST'] = self.XMLLIST
        if vaspnum == 0:
            self.no_vaspruns = True
            self.breaker = True
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
                            self.parser_parameters[self.XMLLIST[v_ind]]['ATOMNUMBER'] = int(line.split()[1])
                        if '<field type="int">atomtype</field>' in line:
                            VASP.readline()
                            for index in range(self.parser_parameters[self.XMLLIST[v_ind]]['ATOMNUMBER']):
                                atomtype = VASP.readline()
                                self.parser_parameters[self.XMLLIST[v_ind]]['ATOMNAMES'].append((atomtype.split('>')[2]).split('<')[0])
                                self.parser_parameters[self.XMLLIST[v_ind]]['TYPE'].append(int(atomtype.split('<')[4].split('>')[1]))
                        if POTIM_read and 'name="POTIM">' in line:
                            self.parser_parameters[self.XMLLIST[v_ind]]['POTIM'] = float(line.split()[2].split('<')[0])
                            POTIM_read = False
                        if 'name="POMASS">' in line:
                            for mass in line.split()[2:-1]:
                                self.parser_parameters[self.XMLLIST[v_ind]]['POMASS'].append(float(mass))
                            self.parser_parameters[self.XMLLIST[v_ind]]['POMASS'].append(float((line.split()[-1]).split('<')[0]))
                        if '<varray name="positions" >' in line:  # <varray name="positions" >
                            try:
                                if first_read_check:
                                    first_read_check = False
                                else:
                                    array = [list(map(float, VASP.readline().split()[1:4])) for _ in range(self.parser_parameters[self.XMLLIST[v_ind]]['ATOMNUMBER'])]
                                    if first_cord_read:
                                        self.parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'].append(array)
                                        first_cord_read = False
                                    if array != self.parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'][-1]:
                                        self.parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'].append(array)
                            except:
                                self.breaker = True
                        if BASIS_read and '<varray name="basis" >' in line:
                            basis_str = [VASP.readline() for _ in range(3)]
                            basis = [list(map(float, basis_str[index].split()[1:4])) for index in range(len(basis_str))]
                            self.parser_parameters[self.XMLLIST[v_ind]]['BASIS'] = basis
                            BASIS_read = False
                self.parser_parameters[self.XMLLIST[v_ind]]['VASPLEN'] = len(self.parser_parameters[self.XMLLIST[v_ind]]['POSITIONS'])
            self.parser_parameters['MASSES'] = [self.parser_parameters[self.XMLLIST[0]]['POMASS'][index - 1] for index in self.parser_parameters[self.XMLLIST[0]]['TYPE']]
            self.parser_parameters['STEPS_LIST'] = [self.parser_parameters[self.XMLLIST[0]]['VASPLEN']]
            for xml in self.XMLLIST[1:]:
                self.parser_parameters['STEPS_LIST'].append(self.parser_parameters['STEPS_LIST'][-1] + self.parser_parameters[xml]['VASPLEN'] - 1)
            self.parser_parameters['STEPS'] = sum([self.parser_parameters[xml]['VASPLEN'] for xml in self.XMLLIST]) - len(self.XMLLIST) + 1
            self.parser_parameters['ATOMNAMES'] = self.parser_parameters[self.XMLLIST[0]]['ATOMNAMES']
            self.form_atoms_with_nums_dict()
            self.removed_atoms_find(self.parser_parameters)
            self.position_array_form(self.parser_parameters)
            self.parser_parameters['POTIM'] = [self.parser_parameters[xml_file]['POTIM'] for xml_file in self.parser_parameters['XMLLIST']]
            if not self.breaker:
                try:
                    self.parser_parameters['POSITIONS'] = np.array(self.parser_parameters['POSITIONS'])
                    self.parser_parameters['BASIS'] = self.parser_parameters[self.parser_parameters['XMLLIST'][0]]['BASIS']
                    self.parser_parameters['ATOMNUMBER'] = self.parser_parameters[self.parser_parameters['XMLLIST'][0]]['ATOMNUMBER']
                    for i in range(self.parser_parameters['ATOMNUMBER']):
                        if self.parser_parameters['ATOMNAMES'][i][-1] == ' ':
                            self.parser_parameters['ATOMNAMES'][i] = self.parser_parameters['ATOMNAMES'][i][:-1]
                    self.parser_parameters['BASIS'] = np.array(self.parser_parameters['BASIS'])
                    cube_vert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                                 [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5],
                                 [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
                    # Создание вершин границы ячейки
                    self.parser_parameters['BASIS_VERT'] = np.dot(cube_vert, self.parser_parameters['BASIS'])
                    self.parser_parameters['DIRECT'] = np.copy(self.parser_parameters['POSITIONS'])
                    self.parser_parameters['POSITIONS'] = self.parser_parameters['POSITIONS'] - 0.5
                    # Преобразование координат из дискретных в декартовы в соответствии с базисом
                    for m in range(self.parser_parameters['STEPS']):
                        self.parser_parameters['POSITIONS'][m] = np.dot(self.parser_parameters['POSITIONS'][m], self.parser_parameters['BASIS'])
                    deleted_positions_to_none(self.parser_parameters['DIRECT'], self.parser_parameters['POSITIONS'])
                    self.parser_parameters = self.color_choose(self.parser_parameters)
                    self.parser_parameters['ID'] = [self.parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1) for ind in range(self.parser_parameters['ATOMNUMBER'])]
                    self.parser_parameters['ID-TO-NUM'] = {self.parser_parameters['ATOMNAMES'][ind] + "_" + str(ind + 1): ind for ind in range(self.parser_parameters['ATOMNUMBER'])}
                except KeyError:
                    self.breaker = True

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

    def form_atoms_with_nums_dict(self):
        self.parser_parameters['ATOM-NUMBERS'] = dict()
        for uniq_atom in set(self.parser_parameters['ATOMNAMES']):
            for number, atom in enumerate(self.parser_parameters['ATOMNAMES']):
                if atom == uniq_atom:
                    stripped_atom = uniq_atom.rstrip()
                    if stripped_atom in self.parser_parameters['ATOM-NUMBERS']:
                        self.parser_parameters['ATOM-NUMBERS'][stripped_atom].append(number)
                    else:
                        self.parser_parameters['ATOM-NUMBERS'][stripped_atom] = [number]

    @ staticmethod
    def color_choose(dictionary):
        # Задание цвета и размеров атомов
        dictionary['COLORNAME'], dictionary['COLORVALUE'], dictionary['RADII'] = [], [], []
        Uncommon_atom, unc_color, unc_radii = list(), list(), list()
        for i in range(dictionary['ATOMNUMBER']):
            if dictionary['ATOMNAMES'][i] == 'O':
                dictionary['COLORNAME'].append('red')
                dictionary['COLORVALUE'].append([1, 0, 0])
                dictionary['RADII'].append(0.3)
            elif dictionary['ATOMNAMES'][i] == 'Si':
                dictionary['COLORNAME'].append('yellow')
                dictionary['COLORVALUE'].append([1, 1, 0])
                dictionary['RADII'].append(0.4)
            elif dictionary['ATOMNAMES'][i] == 'H':
                dictionary['COLORNAME'].append('gray')
                dictionary['COLORVALUE'].append([0.5, 0.5, 0.5])
                dictionary['RADII'].append(0.2)
            elif dictionary['ATOMNAMES'][i] == 'C':
                dictionary['COLORNAME'].append('black')
                dictionary['COLORVALUE'].append([0.2, 0.2, 0.2])
                dictionary['RADII'].append(0.33)
            elif dictionary['ATOMNAMES'][i] == 'He':
                dictionary['COLORNAME'].append('green')
                dictionary['COLORVALUE'].append([0, 1, 0])
                dictionary['RADII'].append(0.18)
            elif dictionary['ATOMNAMES'][i] == 'Ar':
                dictionary['COLORNAME'].append('purple')
                dictionary['COLORVALUE'].append([0.6, 0, 0.6])
                dictionary['RADII'].append(0.34)
            elif dictionary['ATOMNAMES'][i] == 'Xe':
                dictionary['COLORNAME'].append('blue')
                dictionary['COLORVALUE'].append([0.05, 0, 0.6])
                dictionary['RADII'].append(0.38)
            elif dictionary['ATOMNAMES'][i] == 'Mo':
                dictionary['COLORNAME'].append('#00c6c6') # #a100a1
                dictionary['COLORVALUE'].append([0, 0.78, 0.78]) # old violet 0.63, 0, 0.63
                dictionary['RADII'].append(0.5)
            elif dictionary['ATOMNAMES'][i] == 'S':
                dictionary['COLORNAME'].append('#ffff00')
                dictionary['COLORVALUE'].append([1.0, 1.0, 0])
                dictionary['RADII'].append(0.36)
            elif dictionary['ATOMNAMES'][i] == 'N':
                dictionary['COLORNAME'].append('#0000ff')
                dictionary['COLORVALUE'].append([0, 0, 1]) # old light blue
                dictionary['RADII'].append(0.24)
            elif dictionary['ATOMNAMES'][i] == 'Ne':
                dictionary['COLORNAME'].append('#8b4513')
                dictionary['COLORVALUE'].append([0.543, 0.27, 0.07])
                dictionary['RADII'].append(0.16)
            elif dictionary['ATOMNAMES'][i] == 'Cl':
                dictionary['COLORNAME'].append('1fc4a6')
                dictionary['COLORVALUE'].append([0.12, 0.77, 0.65])
                dictionary['RADII'].append(0.3)
            else:
                if len(Uncommon_atom) != 0:
                    Uncommon_atom.append(dictionary['ATOMNAMES'][i])
                    if Uncommon_atom[-1] == Uncommon_atom[-2]:
                        dictionary['COLORVALUE'].append(unc_color[-1])
                        dictionary['RADII'].append(unc_radii[-1])
                        unc_color.append(dictionary['COLORVALUE'][-1])
                        unc_radii.append(dictionary['RADII'][-1])
                    else:
                        r, g, b = random.random(), random.random(), random.random()
                        rad = random.uniform(0.24, 0.42)
                        dictionary['COLORVALUE'].append([r, g, b])
                        dictionary['RADII'].append(rad)
                        unc_color.append([r, g, b])
                        unc_radii.append(rad)
                if len(Uncommon_atom) == 0:
                    Uncommon_atom.append(dictionary['ATOMNAMES'][i])
                    r, g, b = random.random(), random.random(), random.random()
                    rad = random.uniform(0.24, 0.42)
                    dictionary['COLORVALUE'].append([r, g, b])
                    dictionary['RADII'].append(rad)
                    unc_color.append([r, g, b])
                    unc_radii.append(rad)
        return dictionary


def deleted_positions_to_none(direct_positions_array, positions_array):
    for step in range(len(direct_positions_array)):
        for atom in range(len(direct_positions_array[step])):
            for proj in range(len(direct_positions_array[step][atom])):
                if direct_positions_array[step][atom][proj] == 10.:
                    positions_array[step][atom][proj] = None
