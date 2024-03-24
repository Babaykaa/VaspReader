import numpy as np
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.arrays import vbo


class VRVBO:
    """Forms vertex buffer object from inputted arrays."""
    def __init__(self, array_elements: tuple[np.ndarray, ...], indexes: np.ndarray = None, usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER'):  # GL_DYNAMIC_DRAW
        """Initializes VBO arrays of indexes and vertices, colors, normals, texCords."""
        self.vao = None
        self.array = np.array([])
        self.array_elements = tuple()
        self.element_size = 0
        self.elements_number = 0
        for index, element in enumerate(array_elements):
            if index == 0:
                element = element.astype(np.float32)
                self.elements_number = element.shape[0]
                self.array_elements = (element.shape[1], )
                self.element_size = element.itemsize
                self.array = element
            else:
                element = element.astype(np.float32)
                self.array_elements = self.array_elements + (element.shape[1], )
                self.array = np.concatenate((self.array, element), axis=1)
        self.dimension_size = sum(self.array_elements)
        self.array = vbo.VBO(self.array, usage, target)
        self.indexes = None
        if indexes is not None:
            self.elements_number = len(indexes)
            self.indexes = vbo.VBO(indexes, usage, GL_ELEMENT_ARRAY_BUFFER)

    def __del__(self) -> None:
        """A rule for deleting a VRVBO object."""
        if glDeleteBuffers:
            self.array.delete()
            # if self.vao is not None and glDeleteVertexArrays:
            #     glDeleteVertexArrays(1, [self.vao])
            if self.indexes is not None:
                self.indexes.delete()

    def create_vao_buffer(self):
        """Creates VAO buffer from VBO buffers and return the class object."""
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.array.bind()
        for index, size in enumerate(self.array_elements):
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, self.dimension_size * self.element_size, self.array + (sum(self.array_elements[:index + 1]) - self.array_elements[index]) * self.element_size)  # ctypes.c_void_p(0)
            glEnableVertexAttribArray(index)
        self.array.unbind()
        glBindVertexArray(0)
        return self

    def load_uniform_vec4(self, location, vec4) -> None:
        """Loading of vec4f uniform variable into program."""
        glUniform4f(location, *vec4)

    def load_uniform_vec3(self, location, vec3) -> None:
        """Loading of vec3f uniform variable into program."""
        glUniform3f(location, *vec3)

    def load_uniform_mat4(self, location, mat4) -> None:
        """Loading of mat4fv uniform variable into program."""
        glUniformMatrix4fv(location, 1, GL_TRUE, mat4)

    def load_uniform_mat3(self, location, mat3) -> None:
        """Loading of mat3fv uniform variable into program."""
        glUniformMatrix3fv(location, 1, GL_TRUE, mat3)

    def load_uniform_float(self, location, u_float) -> None:
        """Loading of float uniform variable into program."""
        glUniform1f(location, u_float)

    def load_uniform_int(self, location, u_int) -> None:
        """Loading of int uniform variable into program."""
        glUniform1i(location, u_int)

    def define_uniform_variable_type(self, var_type):
        """Automatically define type of uniform variable."""
        if var_type == 'vec4':
            return self.load_uniform_vec4
        elif var_type == 'vec3':
            return self.load_uniform_vec3
        elif var_type == 'mat3':
            return self.load_uniform_mat3
        elif var_type == 'mat4':
            return self.load_uniform_mat4
        elif var_type == 'float':
            return self.load_uniform_float
        else:
            raise VRVBOError('Undefined shader variable type.')

    def prepare_to_draw(self, program) -> None:
        """Starts to use the pointed program and binds VAO buffer."""
        glUseProgram(program)
        glBindVertexArray(self.vao)

    def end_of_drawing(self) -> None:
        """Unbinds VAO buffer and ends to use the pointed program."""
        glBindVertexArray(0)
        glUseProgram(0)

    def set_light_settings(self, uniform_variables_dict, Ka, Kd, Ks, Shininess, lightPositions, lightIntensities) -> None:
        """Loads light settings into program."""
        for index, position in enumerate(lightPositions):
            self.load_uniform_vec4(uniform_variables_dict[(f'lights[{index}].Position', '')], position)
            self.load_uniform_vec3(uniform_variables_dict[(f'lights[{index}].Intensity', '')], lightIntensities[index])
        self.load_uniform_vec3(uniform_variables_dict[('Kd', 'vec3')], Kd)
        self.load_uniform_vec3(uniform_variables_dict[('Ka', 'vec3')], Ka)
        self.load_uniform_vec3(uniform_variables_dict[('Ks', 'vec3')], Ks)
        self.load_uniform_float(uniform_variables_dict[('Shininess', 'float')], Shininess)

    def set_fog_parameters(self, uniform_variables_dict, eyePosition, fogColor, fogMinDist, fogMaxDist, fogPower, fogDensity) -> None:
        """Loads fog settings into program."""
        self.load_uniform_vec3(uniform_variables_dict[('EyePosition', 'vec3')], eyePosition)
        self.load_uniform_vec4(uniform_variables_dict[('fog.FogColor', '=')], fogColor)
        # self.load_uniform_float(uniform_variables_dict[('fog.FogMaxDist', '1')], fogMaxDist)
        # self.load_uniform_float(uniform_variables_dict[('fog.FogMinDist', '1')], fogMinDist)
        self.load_uniform_int(uniform_variables_dict[('fog.FogPower', '1')], fogPower)
        self.load_uniform_float(uniform_variables_dict[('fog.FogDensity', '1')], fogDensity)

    def is_texture_exist(self, uniform_variables_dict, value):
        self.load_uniform_int(uniform_variables_dict[('isTextureExist', 'int')], value)

    def set_texture_info(self, uniform_variables_dict, texture):
        self.load_uniform_int(uniform_variables_dict[('textureMap', 'sampler2D')], texture)

    def draw_from_vao_buffer(self, primitive_type, uniform_variables_dict, ModelMatrix='', ViewMatrix='', ProjectionMatrix='', NormalMatrix='', TranslationMatrix='', texture='') -> None:
        """Sends command to draw elements from VAO buffer."""
        self.load_uniform_mat4(uniform_variables_dict[('ModelMatrix', 'mat4')], ModelMatrix)
        self.load_uniform_mat4(uniform_variables_dict[('ViewMatrix', 'mat4')], ViewMatrix)
        self.load_uniform_mat4(uniform_variables_dict[('ProjectionMatrix', 'mat4')], ProjectionMatrix)
        self.load_uniform_mat3(uniform_variables_dict[('NormalMatrix', 'mat3')], NormalMatrix)
        self.load_uniform_mat4(uniform_variables_dict[('TranslationMatrix', 'mat4')], TranslationMatrix)
        if self.indexes is not None:
            self.indexes.bind()
        if texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
        glDrawElements(primitive_type, self.elements_number, GL_UNSIGNED_INT, None)
        if texture:
            glBindTexture(GL_TEXTURE_2D, 0)
        if self.indexes is not None:
            self.indexes.unbind()


class VRVBOError(Exception):
    """Class for processing of errors in VRVBO class."""
    def __init__(self, message):
        """Initializing function."""
        super(VRVBOError, self).__init__(f'VRVBO error: {message}')