"""Shaders compilation class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.


import traceback
import os
import logging
import OpenGL
from OpenGL.GL import *
from enum import Enum

OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)

__all__ = [
    "Shaders",
    "ShaderType",
    "ShaderError"
]


class ShaderType(Enum):
    """Enum for shader types."""
    VERTEX = GL_VERTEX_SHADER
    FRAGMENT = GL_FRAGMENT_SHADER
    GEOMETRY = GL_GEOMETRY_SHADER
    TESS_CONTROL = GL_TESS_CONTROL_SHADER
    TESS_EVALUATION = GL_TESS_EVALUATION_SHADER
    COMPUTE = GL_COMPUTE_SHADER


class Shaders:
    """
    A class for working with shaders and programs compilation.
    
    This class provides methods for compiling and linking shaders into a program,
    managing uniform variables, and searching for subroutines within the program.
    It also provides a method for adding new shader types to the class.

    Class Methods:
    __init__: Initializes the class and compiles shaders.
    __add__: Adds a new shader type to the class.
    __call__: Returns the program ID.
    delete_shader_file: Deletes a shader file from the class.
    search_for_uniform_variables: Searches for uniform variables in the program.
    search_subroutine_location: Searches for subroutines in the program.
    define_shaders_types: Defines shader types.
    compyle_shader: Compiles shaders.
    load_shader_info: Loads shader information.
    delete_shader: Deletes shaders.
    create_shader_program: Creates shader programs.
    delete_program: Deletes shader programs.

    """

    def __init__(self, directory: str, shader_files: list[str], shader_types: list[str]):
        """
        Initializes the class, compiles shaders and creates a program.
        
        Obtains the directory of shader files, a list of shader file names,
        and a list of shader types. It then defines the shader types and
        compiles the shaders. Finally, it creates a program and searches
        for uniform variables and subroutines within the program.

        Args:
         self: The instance of the class.
         directory: The directory containing the shader files.
         shader_files: A list of strings representing the names of the shader files.
         shader_types: A list of strings representing the types of the shaders.
        
        Attributes:
         program: The ID of the program.
         shaders: A dictionary storing the status of each shader.
         uniform_variables: A dictionary storing the locations of uniform variables.
         subroutine_variables: A dictionary storing the locations of subroutines.
         directory: The directory containing the shader files.
         shader_files: A list of strings representing the names of the shader files.
         shader_types: A list of strings representing the types of the shaders.

        Returns:
         None

        P.S. Please always check positions of files and types of shaders in list.
        """
        self.program = 0
        self.shaders = dict()
        self.uniform_variables = dict()
        self.subroutine_variables = dict()
        self.directory = directory
        self.shader_files = shader_files
        self.shader_types = shader_types
        self.define_shaders_types(self.shader_types) # TODO: move following lines to OpenGL widget
        for index, file in enumerate(shader_files):
            self.compyle_shader(file, self.shader_types[index])
        self.create_shader_program()
        self.search_for_uniform_variables()
        logger.info(f"Shaders compiled")

    def define_shaders_types(self, array) -> None:
        """Function defining type of shader."""
        for index, s_type in enumerate(list(array)):
            match s_type:
                case 'VERTEX':
                    array[index] = ShaderType.VERTEX
                case 'FRAGMENT':
                    array[index] = ShaderType.FRAGMENT
                case 'GEOMETRY':
                    array[index] = ShaderType.GEOMETRY
                case 'TESS_CONTROL':
                    array[index] = ShaderType.TESS_CONTROL
                case 'TESS_EVALUATION':
                    array[index] = ShaderType.TESS_EVALUATION
                case 'COMPUTE':
                    array[index] = ShaderType.COMPUTE
                case _:
                    raise ShaderError('Error in names of shader types.')

    def compyle_shader(self, file, shader_type) -> None:
        """Compiles shaders and raise errors if compilation is not succeed."""
        shader = glCreateShader(shader_type.value)
        if shader == 0:
            raise ShaderError('Cannot load shader.')
        glShaderSource(shader, self.load_shader_info(file))
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not status:
            raise ShaderError(f'Error while compiling {shader_type} shader.')
        self.shaders[shader] = True

    def load_shader_info(self, file) -> str:
        """Reads shader file and save it in string variable."""
        path = os.path.join(self.directory, file) if self.directory else file
        try:
            f = open(path, 'r', encoding="utf-8", errors='ignore')
        except:
            raise ShaderError(f'File {path} does not exist.')
        else:
            f.close()
        shader_source = ""
        with open(path) as f:
            shader_source = f.read()
        return str.encode(shader_source)

    def delete_shader(self, shader) -> None:
        """Deletes shader."""
        if shader in self.shaders:
            glDeleteShader(shader)
            self.shaders[shader] = False

    def create_shader_program(self) -> None:
        """Creates program and add shaders to it."""
        try:
            self.program = glCreateProgram()
        except Exception as e:
            raise ShaderError(f'Exception: {traceback.format_exc()}.')
        if not self.program:
            raise ShaderError('Cannot create program.')
        for shader in self.shaders:
            if self.shaders[shader]:
                glAttachShader(self.program, shader)  # Connect shaders into program
        glLinkProgram(self.program)  # Join the flats program
        status = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not status:
            raise ShaderError('Error with linking program.')

    def delete_program(self) -> None:
        """Deletes program."""
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0

    def __add__(self, other: list[str, str]):
        """Function to add a new type of shader to class object."""
        try:
            file, shader_type = other
        except:
            raise ShaderError('Add function requires pair of file, shader type.')
        self.define_shaders_types([shader_type])
        if shader_type in self.shader_types:
            raise ShaderError('Shader is already exist.')
        else:
            self.shader_types.append(shader_type)
            self.shader_files.append(file)

    def delete_shader_file(self, file) -> None:
        """Deletes shader file."""
        ind = self.shader_files.index(file)
        self.shader_files.pop(ind)
        self.shader_types.pop(ind)

    def search_for_uniform_variables(self) -> None:
        """Automatically define uniform variables in shader and save it in dictionary."""
        uniforms_number = glGetProgramInterfaceiv(self.program, GL_UNIFORM, GL_ACTIVE_RESOURCES)
        types = [GL_NAME_LENGTH, GL_TYPE, GL_LOCATION, GL_BLOCK_INDEX]
        for i in range(uniforms_number):
            # results = np.zeros(4)
            results = glGetProgramResourceiv(self.program, GL_UNIFORM, i, 4, types, 4, None)[-1]
            if results[-1] != -1:
                continue
            name_buf_size = results[0] + 1
            name = glGetProgramResourceName(self.program, GL_UNIFORM, i, name_buf_size, None)[-1]
            name = ''.join([chr(int(el)) for el in name][:-2])
            type_name = ''
            for file in self.shader_files:
                with open(os.path.join(self.directory, file) if self.directory else file, 'r') as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if name in line:
                            type_name = line.split()[1]
                            break
                if type_name:
                    break
            self.uniform_variables[(name, type_name)] = results[2]

    def search_subroutine_location(self, variable_name, variable, shader: [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, ...]) -> None:
        """Searching for any subroutines in program."""
        if self.subroutine_variables.get(variable_name, None) is not None:
            self.subroutine_variables.pop(variable_name)
        self.subroutine_variables[variable_name] = glGetSubroutineIndex(self.program, shader, variable)

    def __call__(self) -> int:
        """Returns program ID."""
        return self.program


class ShaderError(Exception):
    """Class for processing of errors in Shader class."""
    def __init__(self, message):
        """Initializing function."""
        super(ShaderError, self).__init__('Error in Shaders occurs.\nMessage: ' + message)
