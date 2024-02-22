import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class VRShaders:
    """VaspReader shaders compile class. Union shader files into programs for next using in VaspReader visualisation
    functions."""
    VERTEX = GL_VERTEX_SHADER
    FRAGMENT = GL_FRAGMENT_SHADER
    GEOMETRY = GL_GEOMETRY_SHADER
    TESS_CONTROL = GL_TESS_CONTROL_SHADER
    TESS_EVALUATION = GL_TESS_EVALUATION_SHADER
    COMPUTE = GL_COMPUTE_SHADER

    def __init__(self, directory: str, shader_files: list[str], shader_types: list[str]):
        """Initialize class function. Requires:

        directory - directory of shader files,

        shader_files - list of string names of shaders for next form pathnames of files,

        shader_types - shaders type: VERTEX, FRAGMENT, GEOMETRY, TESS_CONTROL, TESS_EVALUATION or COMPUTE.

        Please always check positions of files and types of shaders in list."""
        self.program = 0
        self.shaders = dict()
        self.uniform_variables_dict = dict()
        self.subroutine_variables = dict()
        self.directory = directory
        self.shader_files = shader_files
        self.shader_types = shader_types
        self.define_shaders_types(self.shader_types)
        for index, file in enumerate(shader_files):
            self.compyle_shader(file, self.shader_types[index])
        self.create_shader_program()
        self.search_for_uniform_variables()

    def define_shaders_types(self, array) -> None:
        """Function for define type of shader."""
        for index, s_type in enumerate(list(array)):
            if s_type == 'VERTEX':
                array[index] = self.VERTEX
            elif s_type == 'FRAGMENT':
                array[index] = self.FRAGMENT
            elif s_type == 'GEOMETRY':
                array[index] = self.GEOMETRY
            elif s_type == 'TESS_CONTROL':
                array[index] = self.TESS_CONTROL
            elif s_type == 'TESS_EVALUATION':
                array[index] = self.TESS_EVALUATION
            elif s_type == 'COMPUTE':
                array[index] = self.COMPUTE
            else:
                raise VRShaderError('Error in names of shader types.')

    def compyle_shader(self, file, shader_type) -> None:
        """Compiles shaders and raise errors if compilation is not succeed."""
        shader = glCreateShader(shader_type)
        if shader == 0:
            raise VRShaderError('Cannot load shader.')
        glShaderSource(shader, self.load_shader_info(file))
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not status:
            raise VRShaderError(f'Error while compiling {shader_type} shader.')
        self.shaders[shader] = True

    def load_shader_info(self, file):
        """Reads shader file and save it in string variable."""
        path = f'{self.directory}\\{file}'
        try:
            f = open(path, 'r', encoding="utf-8", errors='ignore')
        except:
            raise VRShaderError(f'File {path} does not exist.')
        else:
            f.close()
        shader_source = ""
        with open(path) as f:
            shader_source = f.read()
        return str.encode(shader_source)

    def delete_shader(self, shader) -> None:
        if shader in self.shaders:
            glDeleteShader(shader)
            self.shaders[shader] = False

    def create_shader_program(self) -> None:
        """Creates program and add shaders to it."""
        try:
            self.program = glCreateProgram()
        except Exception as e:
            raise VRShaderError(f'Exception: {e}.')
        if not self.program:
            raise VRShaderError('Cannot create program.')
        for shader in self.shaders:
            if self.shaders[shader]:
                glAttachShader(self.program, shader)  # Connect shaders into program
        glLinkProgram(self.program)  # Join the flats program
        status = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not status:
            raise VRShaderError('Error with linking program.')

    def delete_program(self) -> None:
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0

    def __add__(self, other: list[str, str]):
        """Function to add a new type of shader to class object."""
        try:
            file, shader_type = other
        except:
            raise VRShaderError('Add function requires pair of file, shader type.')
        shader_type = [shader_type]
        self.define_shaders_types(shader_type)
        if shader_type[0] in self.shader_types:
            raise VRShaderError('Shader is already exist.')
        else:
            self.shader_types.append(*shader_type)
            self.shader_files.append(file)

    def delete_shader_file(self, file) -> None:
        ind = self.shader_files.index(file)
        self.shader_files.pop(ind)
        self.shader_types.pop(ind)

    def search_for_uniform_variables(self) -> None:
        """Automatically define uniform variables in shader and save it in dictionary."""
        numUniforms = glGetProgramInterfaceiv(self.program, GL_UNIFORM, GL_ACTIVE_RESOURCES)
        types = [GL_NAME_LENGTH, GL_TYPE, GL_LOCATION, GL_BLOCK_INDEX]
        for i in range(numUniforms):
            # results = np.zeros(4)
            results = glGetProgramResourceiv(self.program, GL_UNIFORM, i, 4, types, 4, None)[-1]
            if results[-1] != -1:
                continue
            nameBufSize = results[0] + 1
            name = glGetProgramResourceName(self.program, GL_UNIFORM, i, nameBufSize, None)[-1]
            name = ''.join([chr(int(el)) for el in name][:-2])
            type_name = ''
            for file in self.shader_files:
                with open(f'{self.directory}\\{file}', 'r') as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if name in line:
                            type_name = line.split()[1]
                            break
                if type_name:
                    break
            self.uniform_variables_dict[(name, type_name)] = results[2]

    def search_subroutine_location(self, variable_name, variable, shader: [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, ...]) -> None:
        """Searching for any subroutines in program."""
        if self.subroutine_variables.get(variable_name, None) is not None:
            self.subroutine_variables.pop(variable_name)
        self.subroutine_variables[variable_name] = glGetSubroutineIndex(self.program, shader, variable)

    def __call__(self) -> int:
        """Returns program ID."""
        return self.program


class VRShaderError(Exception):
    """Class for processing of errors in VRShader class."""
    def __init__(self, message):
        """Initializing function."""
        super(VRShaderError, self).__init__('Error in VRShaders occurs.\nMessage:' + message)