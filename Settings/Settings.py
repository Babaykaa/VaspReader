import os
import json
import numpy as np
from Logs.VRLogger import sendDataToLogger


class VRSettings:
    __project_directory = os.path.abspath('')

    @sendDataToLogger
    def __init__(self, logger):
        self.__loger = logger
        self.print_window_location = None
        self.visual_window_location = None
        self.processing_window_location = None
        self.graph_proc_window_location = None
        self.file_sharing_window_location = None
        self.console_window_location = None
        self.chgcar_window_location = None
        self.form_poscar_window_location = None
        self.bonds_window_location = None
        self.del_coords_leave_cell = True
        self.light_settings = {'POSITIONS': np.zeros((8, 4)).tolist(), 'INTENSITIES': np.zeros((8, 3)).tolist()}
        self.set_standard_light()
        self.background_color = (0.0, 0.0, 0.0, 1.0)
        self.view_axes = True
        self.view_cell = True
        self.only_keyboard_sel = True

    def get_logger(self):
        return self.__loger

    @sendDataToLogger
    def set_standard_light(self):
        self.light_settings['POSITIONS'][0] = [10.0, 10.0, 10.0, 0.0]
        self.light_settings['INTENSITIES'][0] = [0.4, 0.4, 0.4]

    @sendDataToLogger
    def load_settings(self):
        try:
            with open(self.__project_directory + r'\Settings\settings.json', 'r') as file:
                data = json.load(file)
            self.print_window_location = data['print_window_location']
            self.visual_window_location = data['visual_window_location']
            self.processing_window_location = data['processing_window_location']
            self.graph_proc_window_location = data['graph_proc_window_location']
            self.file_sharing_window_location = data['file_sharing_window_location']
            self.console_window_location = data['console_window_location']
            self.chgcar_window_location = data['chgcar_window_location']
            self.form_poscar_window_location = data['form_poscar_window_location']
            self.bonds_window_location = data['bonds_window_location']
            self.del_coords_leave_cell = data['del_coords_leave_cell']
            self.light_settings = data['light_settings']
            self.background_color = data['background_color']
            self.view_axes = data['view_axes']
            self.view_cell = data['view_cell']
            self.only_keyboard_sel = data['only_keyboard_sel']
        except FileNotFoundError:
            pass
        return self

    def save_settings(self, loger):
        loger.insert_logs(self.__class__.__name__, 'save_settings', result='IN PROGRESS')
        variables = vars(self)
        variables.pop('_VRSettings__loger')
        with open(self.__project_directory + r'\Settings\settings.json', 'w') as file:
            json.dump(variables, file)
        loger.insert_logs(self.__class__.__name__, 'save_settings')
        return self

    def __repr__(self):
        variables_dict = vars(self)
        variables_dict.pop('_VRSettings__loger')
        info_string = '{\n'
        for variable in variables_dict:
            info_string += f'{variable}: {variables_dict[variable]},\n'
        info_string += '}'
        return f"""VaspReader settings option with variables:\n{info_string}."""
