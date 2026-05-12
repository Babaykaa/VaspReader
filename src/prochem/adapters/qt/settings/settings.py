"""ProChem Settings module."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import os
import json
import numpy as np
import logging
import random
from typing import Any, Self

logger = logging.getLogger(__name__)

__all__ = ["Settings"]


class Settings:
    """
    A class for managing and accessing project settings.
    
    This class provides a centralized way to load, store, and retrieve
    configuration settings for a project, ensuring consistency and
    ease of access. It utilizes a singleton pattern to guarantee only
    one instance of the settings exists.
    
    Class Attributes:
    - _instance: The single instance of the Settings class.
    - _initialized: A boolean flag indicating whether the settings have been initialized.
    
    Class Methods:
    - __new__: Creates and returns a singleton instance of the class.
    - __init__: Initializes the ProjectConfig object.
    - __set_default_settings: Initializes default settings for the visualization.
    - load_settings: Loads settings from a JSON file.
    - check_settings_keys: Checks if all keys in a valid settings dictionary are present in a check dictionary.
    - convert_values_to: Converts values within a dictionary to a specified object type.
    - get_settings_filename: Returns the settings filename.
    - __get_dict_value: Recursively retrieves a value from a nested dictionary.
    - __set_dict_value: Sets a value within a nested dictionary structure.
    - get_new_window_location: Gets a value from the new window location settings.
    - set_new_window_location: Sets a new location for the window.
    - get_scene_params: Retrieves parameters from the scene settings.
    - set_scene_params: Sets parameters for the scene.
    - get_control_params: Retrieves control parameters from the internal settings.
    - set_control_params: Sets control parameters.
    - get_processing_params: Retrieves processing parameters from the internal settings.
    - set_processing_params: Sets processing parameters within the internal dictionary.
    - save_settings: Saves the current settings to a JSON file.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs) -> Self:
        """
        Creates and returns a singleton instance of the class.
        
        This method ensures that only one instance of the class is ever created.
        It checks if an instance already exists and returns it if so; otherwise,
        it creates a new instance and stores it for future use.
        
        Args:
            cls: The class to instantiate.
        
        Returns:
            The singleton instance of the class.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_directory) -> None:
        """
        Initializes the Settings object.
        
        Stores settings file path and sets default values for 
        next comparison with loaded settings after load_settings
        function call.
        
        Args:
         self: The instance of the ProjectConfig class.
         project_directory: The root directory of the project.
        
        Attributes:
         _initialized: A boolean flag indicating whether the configuration has been initialized.
         __project_directory: The root directory of the project.
         __settings_file: The path to the settings JSON file.
        
        Returns:
         None
        """
        if not self._initialized:
            self._initialized = True
            self.__project_directory = project_directory
            self.__settings_file = os.path.join(project_directory, 'settings', 'settings.json')
            self.__set_default_settings()

    def __set_default_settings(self) -> None:
        """
        Initializes default settings.
        
        This method sets up default values for various parameters controlling
        the appearance and behavior of the program, including window
        locations, scene parameters (lighting, view, background, fog, bonds),
        control parameters, processing parameters, and atom parameters (colors,
        scales).
        
        Args:
          self: The instance of the class.
        
        Attributes Initialized:
          __new_window_location (dict): A dictionary storing default locations
            for various windows (print, control, visual, processing, graph,
            file_sharing, console, chgcar, form_poscar, oszicar, bonds).
          __scene_params (dict): A dictionary containing parameters related to
            the scene, including lighting, view, background, fog, and bond
            appearance.
          __control_params (dict): A dictionary storing parameters controlling
            user interaction and control.
          __processing_params (dict): A dictionary storing parameters related
            to data processing.
          __atoms_params (dict): A dictionary storing parameters related to
            atom representation, including colors and scales.
        """
        self.__new_window_location = {
            "print": None,
            "control": None,
            "visual": None,
            "processing": None,
            "graph": None,
            "file_sharing": None,
            "console": None,
            "chgcar": None,
            "form_poscar": None,
            "oszicar": None,
            "bonds": None
        }
        self.__scene_params = {
            'light': {
                'states': {i: False if i > 1 else True for i in range(8)},
                'positions': np.array([[10.0, 10.0, 10.0, 1.0], [10.0, 10.0, -10.0, 1.0], 
                                       [10.0, -10.0, 10.0, 1.0], [10.0, -10.0, -10.0, 1.0],
                                       [-10.0, 10.0, 10.0, 1.0], [-10.0, 10.0, -10.0, 1.0],
                                       [-10.0, -10.0, 10.0, 1.0], [-10.0, -10.0, -10.0, 1.0]]),
                'intensities': np.array([[0.8, 0.8, 0.8], [0.8, 0.8, 0.8], 
                                         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
                                         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 
                                         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
                'kd': np.array([0.3, 0.3, 0.3]),
                'ld': np.array([0.7, 0.7, 0.7]),
                'ka': np.array([0.5, 0.5, 0.5]),
                'ks': np.array([0.8, 0.8, 0.8]),
                'shininess': 10.0
            },
            'view': {
                'axes': True,
                'cell_border': True,
                'is_perspective': True,
                'eye_position': np.array([0.0, 0.0, 20.0]),
                'center': np.array([0.0, 0.0, 0.0]),
                'up': np.array([0.0, 1.0, 0.0]),
                'projection': {
                    'near': 0.1,
                    'far': 100.0
                },
                'perspective': {
                    'fov': 45.0,
                    'aspect': 1.0
                },
                'ortho': {
                    'left': -12.0,
                    'right': 12.0,
                    'top': 9.0,
                    'bottom': -9.0,
                }
            },
            'background': {
                'color': np.array([0.6, 0.6, 0.6, 1.0])
            },
            'fog': {
                'color': np.array([0.6, 0.6, 0.6, 1.0]),
                'min_dist': 10,
                'max_dist': 60,
                'power': 1,
                'density': 0.05
            },
            'bond': {
                'length': 1.8,
                'radius': 0.2
            }
        }
        self.__control_params = {
            'only_keyboard_selection': True,
            'slider_speed': 1,
            'browse_folder_path': None,
        }
        self.__processing_params = {
            'delete_coordinates_after_leave_cell': True
        }
        self.__atoms_params = {
            'colors': {
                'H': np.array([0.9, 0.9, 0.9]),
                'He': np.array([0.0, 0.95, 0.05]),
                'Li': np.array([0.8, 0.502, 1.0]),
                'Be': np.array([0.7608, 1.0, 0.0]),
                'B': np.array([1.0, 0.71, 0.71]),
                'C': np.array([0.565, 0.565, 0.565]),
                'N': np.array([0.188, 0.118, 0.99]),
                'O': np.array([1.0, 0.051, 0.051]),
                'F': np.array([0.565, 0.878, 0.314]),
                'Ne': np.array([0.77, 0.89, 0.96]),
                'Na': np.array([0.6706, 0.361, 0.949]),
                'Mg': np.array([0.5412, 1.0, 0.0]),
                'Al': np.array([0.749, 0.651, 0.651]),
                'Si': np.array([0.9412, 0.784, 0.6274]),
                'P': np.array([1.0, 0.5019, 0.0]),
                'S': np.array([1.0, 1.0, 0.157]),
                'Cl': np.array([0.1215, 0.9412, 0.1215]),
                'Ar': np.array([0.5, 0.82, 0.89]),
                'K': np.array([0.56, 0.251, 0.8314]),
                'Ca': np.array([0.2392, 1.0, 0.0]),
                'Sc': np.array([0.902, 0.902, 0.902]),
                'Ti': np.array([0.749, 0.7607, 0.78]),
                'V': np.array([0.651, 0.651, 0.671]),
                'Cr': np.array([0.5412, 0.6, 0.78]),
                'Mn': np.array([0.61177, 0.4784, 0.78]),
                'Fe': np.array([0.878, 0.4, 0.2]),
                'Co': np.array([0.9412, 0.565, 0.627]),
                'Ni': np.array([0.3137254901960784, 0.8156862745098039, 0.3137254901960784]),
                'Cu': np.array([0.7843137254901961, 0.5019607843137255, 0.2]),
                'Zn': np.array([0.49019607843137253, 0.5019607843137255, 0.6901960784313725]),
                'Ga': np.array([0.7607843137254902, 0.5607843137254902, 0.5607843137254902]),
                'Ge': np.array([0.4, 0.5607843137254902, 0.5607843137254902]),
                'As': np.array([0.7411764705882353, 0.5019607843137255, 0.8901960784313725]),
                'Se': np.array([1.0, 0.6313725490196078, 0.0]),
                'Br': np.array([0.6509803921568628, 0.1607843137254902, 0.1607843137254902]),
                'Kr': np.array([0.3607843137254902, 0.7215686274509804, 0.8196078431372549]),
                'Rb': np.array([0.4392156862745098, 0.1803921568627451, 0.6901960784313725]),
                'Sr': np.array([0.0, 1.0, 0.0]),
                'Y': np.array([0.5803921568627451, 1.0, 1.0]),
                'Zr': np.array([0.5803921568627451, 0.8784313725490196, 0.8784313725490196]),
                'Nb': np.array([0.45098039215686275, 0.7607843137254902, 0.788235294117647]),
                'Mo': np.array([0.32941176470588235, 0.7098039215686275, 0.7098039215686275]),
                'Tc': np.array([0.23137254901960785, 0.6196078431372549, 0.6196078431372549]),
                'Ru': np.array([0.1411764705882353, 0.5607843137254902, 0.5607843137254902]),
                'Rh': np.array([0.0392156862745098, 0.49019607843137253, 0.5490196078431373]),
                'Pd': np.array([0.0, 0.4117647058823529, 0.5215686274509804]),
                'Ag': np.array([0.7529411764705882, 0.7529411764705882, 0.7529411764705882]),
                'Cd': np.array([1.0, 0.8509803921568627, 0.5607843137254902]),
                'In': np.array([0.6509803921568628, 0.4588235294117647, 0.45098039215686275]),
                'Sn': np.array([0.4, 0.5019607843137255, 0.5019607843137255]),
                'Sb': np.array([0.6196078431372549, 0.38823529411764707, 0.7098039215686275]),
                'Te': np.array([0.8313725490196079, 0.47843137254901963, 0.0]),
                'I': np.array([0.5803921568627451, 0.0, 0.5803921568627451]),
                'Xe': np.array([0.25882352941176473, 0.6196078431372549, 0.6901960784313725]),
                'Cs': np.array([0.3411764705882353, 0.09019607843137255, 0.5607843137254902]),
                'Ba': np.array([0.0, 0.788235294117647, 0.0]),
                'La': np.array([0.4392156862745098, 0.8313725490196079, 1.0]),
                'Ce': np.array([1.0, 1.0, 0.7803921568627451]),
                'Pr': np.array([0.8509803921568627, 1.0, 0.7803921568627451]),
                'Nd': np.array([0.7803921568627451, 1.0, 0.7803921568627451]),
                'Pm': np.array([0.6392156862745098, 1.0, 0.7803921568627451]),
                'Sm': np.array([0.5607843137254902, 1.0, 0.7803921568627451]),
                'Eu': np.array([0.3803921568627451, 1.0, 0.7803921568627451]),
                'Gd': np.array([0.27058823529411763, 1.0, 0.7803921568627451]),
                'Tb': np.array([0.18823529411764706, 1.0, 0.7803921568627451]),
                'Dy': np.array([0.12156862745098039, 1.0, 0.7803921568627451]),
                'Ho': np.array([0.0, 1.0, 0.611764705882353]),
                'Er': np.array([0.0, 0.9019607843137255, 0.4588235294117647]),
                'Tm': np.array([0.0, 0.8313725490196079, 0.3215686274509804]),
                'Yb': np.array([0.0, 0.7490196078431373, 0.2196078431372549]),
                'Lu': np.array([0.0, 0.6705882352941176, 0.1411764705882353]),
                'Hf': np.array([0.30196078431372547, 0.7607843137254902, 1.0]),
                'Ta': np.array([0.30196078431372547, 0.6509803921568628, 1.0]),
                'W': np.array([0.12941176470588237, 0.5803921568627451, 0.8392156862745098]),
                'Re': np.array([0.14901960784313725, 0.49019607843137253, 0.6705882352941176]),
                'Os': np.array([0.14901960784313725, 0.4, 0.5882352941176471]),
                'Ir': np.array([0.09019607843137255, 0.32941176470588235, 0.5294117647058824]),
                'Pt': np.array([0.8156862745098039, 0.8156862745098039, 0.8784313725490196]),
                'Au': np.array([1.0, 0.8196078431372549, 0.13725490196078433]),
                'Hg': np.array([0.7215686274509804, 0.7215686274509804, 0.8156862745098039]),
                'Tl': np.array([0.6509803921568628, 0.32941176470588235, 0.30196078431372547]),
                'Pb': np.array([0.3411764705882353, 0.34901960784313724, 0.3803921568627451]),
                'Bi': np.array([0.6196078431372549, 0.30980392156862746, 0.7098039215686275]),
                'Po': np.array([0.6705882352941176, 0.3607843137254902, 0.9490196078431372]),
                'At': np.array([0.4588235294117647, 0.30980392156862746, 0.27058823529411763]),
                'Rn': np.array([0.25882352941176473, 0.5098039215686274, 0.5882352941176471]),
                'Fr': np.array([0.25882352941176473, 0.0, 0.4]),
                'Ra': np.array([0.0, 0.49019607843137253, 0.0]),
                'Ac': np.array([0.4392156862745098, 0.6705882352941176, 0.9803921568627451]),
                'Th': np.array([0.0, 0.7294117647058823, 1.0]),
                'Pa': np.array([0.0, 0.6313725490196078, 1.0]),
                'U': np.array([0.0, 0.5607843137254902, 1.0]),
                'Np': np.array([0.0, 0.5019607843137255, 1.0]),
                'Pu': np.array([0.0, 0.4196078431372549, 1.0]),
                'Am': np.array([0.32941176470588235, 0.3607843137254902, 0.9490196078431372]),
                'Cm': np.array([0.47058823529411764, 0.3607843137254902, 0.8901960784313725]),
                'Bk': np.array([0.5411764705882353, 0.30980392156862746, 0.8901960784313725]),
                'Cf': np.array([0.6313725490196078, 0.21176470588235294, 0.8313725490196079]),
                'Es': np.array([0.7019607843137254, 0.12156862745098039, 0.8313725490196079]),
                'Fm': np.array([0.7019607843137254, 0.12156862745098039, 0.7294117647058823]),
                'Md': np.array([0.7019607843137254, 0.050980392156862744, 0.6509803921568628]),
                'No': np.array([0.7411764705882353, 0.050980392156862744, 0.5294117647058824]),
                'Lr': np.array([0.7803921568627451, 0.0, 0.4]),
                'Rf': np.array([0.8, 0.0, 0.34901960784313724]),
                'Db': np.array([0.8196078431372549, 0.0, 0.30980392156862746]),
                'Sg': np.array([0.8509803921568627, 0.0, 0.27058823529411763]),
                'Bh': np.array([0.8784313725490196, 0.0, 0.2196078431372549]),
                'Hs': np.array([0.9019607843137255, 0.0, 0.1803921568627451]),
                'Mt': np.array([0.9215686274509803, 0.0, 0.14901960784313725]),
                'Ds': np.array([random.random(), random.random(), random.random()]),
                'Rg': np.array([random.random(), random.random(), random.random()]),
                'Cn': np.array([random.random(), random.random(), random.random()]),
                'Nh': np.array([random.random(), random.random(), random.random()]),
                'Fl': np.array([random.random(), random.random(), random.random()]),
                'Mc': np.array([random.random(), random.random(), random.random()]),
                'Lv': np.array([random.random(), random.random(), random.random()]),
                'Ts': np.array([random.random(), random.random(), random.random()]),
                'Og': np.array([random.random(), random.random(), random.random()])
            },
            'scales': {
                'H': 0.22,
                'He': 0.2,
                'Li': 0.3,
                'Be': 0.33,
                'B': 0.34,
                'C': 0.34,
                'N': 0.35,
                'O': 0.36,
                'F': 0.36,
                'Ne': 0.38,
                'Na': 0.32,
                'Mg': 0.33,
                'Al': 0.34,
                'Si': 0.35,
                'P': 0.36,
                'S': 0.37,
                'Cl': 0.38,
                'Ar': 0.4,
                'K': 0.34,
                'Ca': 0.35,
                'Sc': 0.36,
                'Ti': 0.37,
                'V': 0.37,
                'Cr': 0.38,
                'Mn': 0.39,
                'Fe': 0.39,
                'Co': 0.4,
                'Ni': 0.4,
                'Cu': 0.4,
                'Zn': 0.41,
                'Ga': 0.41,
                'Ge': 0.41,
                'As': 0.42,
                'Se': 0.42,
                'Br': 0.43,
                'Kr': 0.43,
                'Rb': 0.36,
                'Sr': 0.36,
                'Y': 0.37,
                'Zr': 0.38,
                'Nb': 0.39,
                'Mo': 0.4,
                'Tc': 0.4,
                'Ru': 0.41,
                'Rh': 0.41,
                'Pd': 0.42,
                'Ag': 0.42,
                'Cd': 0.43,
                'In': 0.43,
                'Sn': 0.44,
                'Sb': 0.44,
                'Te': 0.45,
                'I': 0.45,
                'Xe': 0.46,
                'Cs': 0.38,
                'Ba': 0.38,
                'La': 0.39,
                'Ce': 0.39,
                'Pr': 0.4,
                'Nd': 0.4,
                'Pm': 0.41,
                'Sm': 0.41,
                'Eu': 0.42,
                'Gd': 0.42,
                'Tb': 0.43,
                'Dy': 0.43,
                'Ho': 0.44,
                'Er': 0.44,
                'Tm': 0.45,
                'Yb': 0.45,
                'Lu': 0.46,
                'Hf': 0.46,
                'Ta': 0.47,
                'W': 0.47,
                'Re': 0.48,
                'Os': 0.48,
                'Ir': 0.49,
                'Pt': 0.49,
                'Au': 0.5,
                'Hg': 0.5,
                'Tl': 0.5,
                'Pb': 0.5,
                'Bi': 0.5,
                'Po': 0.5,
                'At': 0.5,
                'Rn': 0.52,
                'Fr': 0.42,
                'Ra': 0.42,
                'Ac': 0.43,
                'Th': 0.43,
                'Pa': 0.44,
                'U': 0.46,
                'Np': 0.46,
                'Pu': 0.47,
                'Am': 0.47,
                'Cm': 0.48,
                'Bk': 0.48,
                'Cf': 0.49,
                'Es': 0.49,
                'Fm': 0.5,
                'Md': 0.5,
                'No': 0.5,
                'Lr': 0.51,
                'Rf': 0.52,
                'Db': 0.52,
                'Sg': 0.53,
                'Bh': 0.53,
                'Hs': 0.54,
                'Mt': 0.54,
                'Ds': 0.55,
                'Rg': 0.55,
                'Cn': 0.56,
                'Nh': 0.56,
                'Fl': 0.57,
                'Mc': 0.57,
                'Lv': 0.58,
                'Ts': 0.58,
                'Og': 0.59
            }
        }
        logger.info(f"Default settings initialized")

    def load_settings(self) -> Self:
        """
        Loads settings from a JSON file.
        
        Args:
            self: The instance of the class.
        
        Initializes the following object properties:
            __new_window_location: A dictionary containing the new window location parameters.
            __scene_params: A dictionary containing the scene parameters.
            __control_params: A dictionary containing the control parameters.
            __processing_params: A dictionary containing the processing parameters.
        
        Returns:
            self: The instance of the class.
        """
        try:
            with open(self.get_settings_filename(), 'r') as file:
                data = json.load(file)
            for key in list(data[1]['light']['states'].keys()):
                data[1]['light']['states'][int(key)] = data[1]['light']['states'].pop(key)
            logger.info(f"Settings json read")
            __settings_default = [self.__new_window_location, self.__scene_params,
                                  self.__control_params, self.__processing_params]
            for indx, json_data in enumerate(data):
                Settings.check_settings_keys(__settings_default[indx], json_data)
                self.convert_values_to(json_data, np.ndarray)
                match indx:
                    case 0:
                        self.__new_window_location = json_data
                    case 1:
                        self.__scene_params = json_data
                    case 2:
                        self.__control_params = json_data
                    case 3:
                        self.__processing_params = json_data
                #__settings_default[indx] = json_data
                #self.convert_values_to(__settings_default[indx], np.ndarray)
            logger.info(f"Settings loaded from {self.get_settings_filename()}")
            logger.debug(f"Window location: {self.__new_window_location}")
            logger.debug(f"Scene params: {self.__scene_params}")
            logger.debug(f"Control params: {self.__control_params}")
            logger.debug(f"Processing params: {self.__processing_params}")
        except FileNotFoundError:
            self.save_settings()
            logger.warning(f"Settings file not found. Default settings saved to {self.get_settings_filename()}")
        except KeyError:
            self.save_settings()
            logger.error(f"Settings file corrupted. Default settings saved to {self.get_settings_filename()}")
        return self

    @staticmethod
    def check_settings_keys(valid_dict: dict, check_dict: dict) -> None:
        """
        Checks if all keys in a valid settings dictionary are present in a check dictionary, 
        and recursively checks nested dictionaries.
        
        Args:
            valid_dict: The dictionary containing the valid settings keys.
            check_dict: The dictionary to check against.
        
        Returns:
            None
        
        Raises:
            KeyError: If a key from valid_dict is not found in check_dict.
        """
        for key in valid_dict:
            if key not in check_dict:
                raise KeyError(f"Key {key} not found in settings file.")
            if isinstance(valid_dict[key], dict):
                Settings.check_settings_keys(valid_dict[key], check_dict[key])

    @staticmethod
    def convert_values_to(dict_object: dict, obj_type: dict) -> None:
        """
        Converts values within a dictionary to a specified object type.
        
         This method recursively iterates through a dictionary and converts NumPy arrays to lists,
         or lists to NumPy arrays, based on the provided object type. It handles nested dictionaries.
        
         Parameters:
         dict_object : The dictionary to process.
         obj_type : The target object type (list or np.ndarray).
        
         Returns:
         The modified dictionary with values converted to the specified type.
        """
        for key in dict_object:
            if isinstance(dict_object[key], dict):
                Settings.convert_values_to(dict_object[key], obj_type)
            elif obj_type == list and isinstance(dict_object[key], np.ndarray):
                dict_object[key] = dict_object[key].tolist()
            elif obj_type == np.ndarray and isinstance(dict_object[key], list):
                dict_object[key] = np.array(dict_object[key])

    def get_settings_filename(self) -> str:
        """
        Returns the settings filename.
        
        Args:
         self: The instance of the class.
        
        Returns:
         str: The settings filename stored in the __settings_file attribute.
        """
        return self.__settings_file

    @staticmethod
    def __get_dict_value(dict_object: dict, *keys) -> Any:
        """
        Recursively retrieves a value from a nested dictionary.
        
        Args:
         dict_object: The dictionary to retrieve the value from.
         *keys: A variable number of keys representing the path to the value.
        
        Returns:
         The value at the specified path in the dictionary.
        """
        if len(keys) == 1:
            return dict_object[keys[0]]
        else:
            return Settings.__get_dict_value(dict_object[keys[0]], *keys[1:])

    @staticmethod
    def __set_dict_value(dict_object: dict, value: Any, *keys) -> None:
        """
        Sets a value within a nested dictionary structure.
        
        This method allows setting a value at a specific path within a dictionary,
        creating nested dictionaries as needed if the path doesn't exist.
        
        Args:
         dict_object: The dictionary to modify.
         value: The value to set.
         *keys: A variable number of keys representing the path to the value
           within the dictionary.
        
        Returns:
         None
        """
        if len(keys) == 1:
            dict_object[keys[0]] = value
        else:
            Settings.__set_dict_value(dict_object[keys[0]], value, *keys[1:])

    def get_new_window_location(self, *keys) -> Any:
        """
        Gets a value from the new window location settings.
        
        Args:
         keys: A variable number of keys to traverse the nested dictionary 
               representing the new window location.
        
        Returns:
         The value associated with the given keys in the new window location 
         settings.
        """
        return Settings.__get_dict_value(self.__new_window_location, *keys)

    def set_new_window_location(self, value: Any, *keys) -> None:
        """
        Sets a new location for the window.
        
        This method updates the internal dictionary representing the new window location
        with the provided value and keys.
        
        Args:
          value: The new value to set for the window location.
          keys: A variable number of keys used to navigate to the specific location
            within the dictionary.
        
        Returns:
          None
        """
        Settings.__set_dict_value(self.__new_window_location, value, *keys)

    def get_scene_params(self, *keys) -> Any:
        """
        Retrieves parameters from the scene settings.
        
        Args:
            keys: A variable number of keys to access nested values within the scene parameters.
        
        Returns:
            The value associated with the given keys, or None if the keys are invalid.
        """
        return Settings.__get_dict_value(self.__scene_params, *keys)

    def set_scene_params(self, value: Any, *keys) -> None:
        """
        Sets parameters for the scene.
        
        This method updates the internal scene parameters dictionary with the given value
        and keys. It leverages an internal helper function to manage the dictionary update.
        
        Args:
          value: The value to set for the specified keys.
          *keys: A variable number of keys representing the path to the parameter
            within the scene_params dictionary.
        
        Returns:
          None
        """
        Settings.__set_dict_value(self.__scene_params, value, *keys)

    def get_control_params(self, *keys) -> Any:
        """
        Retrieves control parameters from the internal settings.
        
        Args:
            *keys: A variable number of keys to access nested values within the control parameters.
        
        Returns:
            The value associated with the given keys, or None if the keys are invalid.
        """
        return Settings.__get_dict_value(self.__control_params, *keys)

    def set_control_params(self, value: Any, *keys) -> None:
        """
        Sets control parameters.
        
        This method sets a value within the control parameters dictionary,
        allowing for nested key access.
        
        Args:
          self: The instance of the class.
          value: The value to set.
          *keys: A variable number of keys to navigate the nested dictionary structure.
        
        Returns:
          None
        """
        Settings.__set_dict_value(self.__control_params, value, *keys)

    def get_processing_params(self, *keys) -> Any:
        """
        Retrieves processing parameters from the internal settings.
        
        Args:
            *keys:  A variable number of keys to access nested values within the processing parameters.
        
        Returns:
            The value associated with the given keys, or None if the keys are invalid.
        """
        return Settings.__get_dict_value(self.__processing_params, *keys)

    def set_processing_params(self, value: Any, *keys) -> None:
        """
        Sets processing parameters within the internal dictionary.
        
        Args:
            value: The value to set for the specified keys.
            *keys: A variable number of keys representing the path to the parameter
                within the nested dictionary.
        
        Returns:
            None
        """
        Settings.__set_dict_value(self.__processing_params, value, *keys)

    def save_settings(self) -> Self:
        """
        Saves the current settings to a JSON file.
        
        This method packages the new window location, scene parameters, control parameters,
        and processing parameters into a JSON format and saves it to a file. It also logs
        information about the saved data.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            self.__new_window_location: Stores the location of the new window.
            self.__scene_params: Stores the parameters for the scene.
            self.__control_params: Stores the parameters for the control elements.
            self.__processing_params: Stores the parameters for the processing pipeline.
        
        Returns:
            self: The instance of the class.
        """
        json_data = [self.__new_window_location, self.__scene_params, 
                     self.__control_params, self.__processing_params] 
        for data in json_data:
            self.convert_values_to(data, list)
        with open(self.get_settings_filename(), 'w') as file:
            json.dump(json_data, file, indent=4)
        logger.info(f"Json data saved to {self.get_settings_filename()}")
        logger.debug(f"Window location: {self.__new_window_location}")
        logger.debug(f"Scene params: {self.__scene_params}")
        logger.debug(f"Control params: {self.__control_params}")
        logger.debug(f"Processing params: {self.__processing_params}")
        return self
