import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.WGL import *


class Primitives:

    def __init__(self, scaling, color: list, vertices=None, colors=None, normal=None, indexes=None):
        self.scaling = scaling
        self.color = color
        self.vertex_array = np.array([]) if vertices is None else vertices
        self.color_array = np.array([]) if colors is None else colors
        self.normal_array = np.array([]) if normal is None else normal
        self.indexes_array = np.array([]) if indexes is None else indexes

    def get_coordinates(self):
        return self.vertex_array, self.color_array

    def Cube(self, draw_type=GL_TRIANGLE_STRIP):
        self.vertex_array = np.array([[-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, -1.0],
                                      [1.0, 1.0, 1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0],
                                      [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0],
                                      [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0],
                                      [-1.0, -1.0, 1.0], [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, -1.0, 1.0],
                                      [-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0]]) * self.scaling
        self.color_array = np.array([self.color] * len(self.vertex_array))
        self.normal_array = np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0],
                                      [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                                      [0.0, -1.0, 0.0], [0.0, -1.0, 0.0], [0.0, -1.0, 0.0], [0.0, -1.0, 0.0],
                                      [-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0],
                                      [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0],
                                      [0.0, 0.0, -1.0], [0.0, 0.0, -1.0], [0.0, 0.0, -1.0], [0.0, 0.0, -1.0]])
        if draw_type == GL_TRIANGLES:
            self.indexes_array = np.array([0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7, 8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15, 16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23])
        elif draw_type == GL_QUADS:
            self.indexes_array = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        return self.vertex_array, self.color_array, self.normal_array, self.indexes_array

    def Sphere(self, radius, nSlices, nStacks):
        nVerts = (nSlices + 1) * (nStacks + 1)
        elements = (nSlices * 2 * (nStacks - 1)) * 3
        p = np.zeros(3 * nVerts) # vertices
        n = np.zeros(3 * nVerts) # normals
        tex = np.zeros(2 * nVerts) # tex coords
        el = np.zeros(elements, dtype=np.int32) # elements

        # Generate positions and normals
        theta, phi = 0, 0
        thetaFac = 2 * np.pi / nSlices
        phiFac = np.pi / nStacks
        nx, ny, nz, s, t = 0.0, 0.0, 0.0, 0.0, 0.0
        idx = 0
        tIdx = 0
        for i in range(0, nSlices + 1):
            theta = i * thetaFac
            s = i / nSlices
            for j in range(0, nStacks + 1):
                phi = j * phiFac
                t = j / nStacks
                nx = np.sin(phi) * np.cos(theta)
                ny = np.sin(phi) * np.sin(theta)
                nz = np.cos(phi)
                p[idx] = radius * nx; p[idx+1] = radius * ny; p[idx+2] = radius * nz
                n[idx] = nx; n[idx+1] = ny; n[idx+2] = nz
                idx += 3

                tex[tIdx] = s; tex[tIdx+1] = t
                tIdx += 2
        # Generate the element list
        idx = 0
        for i in range(0, nSlices):
            stackStart = i * (nStacks + 1)
            nextStackStart = (i + 1) * (nStacks + 1)
            for j in range(0, nStacks):
                if j == 0:
                    el[idx] = stackStart; el[idx+1] = stackStart + 1; el[idx+2] = nextStackStart + 1
                    idx += 3
                elif j == nStacks - 1:
                    el[idx] = stackStart + j; el[idx+1] = stackStart + j + 1; el[idx+2] = nextStackStart + j
                    idx += 3
                else:
                    el[idx] = stackStart + j; el[idx+1] = stackStart + j + 1; el[idx+2] = nextStackStart + j + 1; el[idx+3] = nextStackStart + j; el[idx+4] = stackStart + j; el[idx+5] = nextStackStart + j + 1
                    idx += 6
        p, color, n, tex, el = np.asarray(p).reshape((-1, 3)) * self.scaling, np.array([self.color] * int(len(p) / 3)).reshape((-1, 3)), np.asarray(n).reshape((-1, 3)), np.asarray(tex).reshape((-1, 2)), np.asarray(el)
        return p, color, n, tex, el

    def Torus(self, outerRadius, innerRadius, nsides, nrings):
        faces = nsides * nrings
        nVerts = nsides * (nrings + 1) # One extra ring to duplicate first ring

        # Points
        p = np.zeros(3 * nVerts)
        # Normals
        n = np.zeros(3 * nVerts)
        # Tex coords
        tex = np.zeros(2 * nVerts)
        # Elements
        el = np.zeros(6 * faces, dtype=np.int32)

        # Generate the vertex data
        ringFactor = 2 * np.pi / nrings
        sideFactor = 2 * np.pi / nsides
        idx = 0
        tidx = 0
        for ring in range(0, nrings + 1):
            u = ring * ringFactor
            cu = np.cos(u)
            su = np.sin(u)
            for side in range(0, nsides):
                v = side * sideFactor
                cv = np.cos(v)
                sv = np.sin(v)
                r = outerRadius + innerRadius * cv
                p[idx] = r * cu; p[idx + 1] = r * su; p[idx + 2] = innerRadius * sv
                n[idx] = cv * cu * r; n[idx + 1] = cv * su * r; n[idx + 2] = sv * r
                tex[tidx] = u / (2 * np.pi); tex[tidx + 1] = v / (2 * np.pi)
                tidx += 2
                # Normalize
                lenn = np.sqrt(n[idx] * n[idx] + n[idx + 1] * n[idx + 1] + n[idx + 2] * n[idx + 2])
                n[idx] /= lenn; n[idx + 1] /= lenn; n[idx + 2] /= lenn
                idx += 3

        idx = 0
        for ring in range(0, nrings):
            ringStart = ring * nsides
            nextRingStart = (ring + 1) * nsides
            for side  in range(0, nsides):
                nextSide = (side+1) % nsides
                # The quad
                el[idx] = (ringStart + side); el[idx+1] = (nextRingStart + side); el[idx+2] = (nextRingStart + nextSide); el[idx+3] = ringStart + side; el[idx+4] = nextRingStart + nextSide; el[idx+5] = (ringStart + nextSide)
                idx += 6
        p, color, n, tex, el = np.asarray(p).reshape((-1, 3)), np.array([self.color] * int(len(p) / 3)).reshape((-1, 3)), np.asarray(n).reshape((-1, 3)), np.asarray(tex).reshape((-1, 2)), np.asarray(el)
        return p, color, n, tex, el

    def Yula(self, radius, nSlices):
        nVerts = (nSlices + 1) * 3
        elements = (nSlices * 2) * 3
        p = np.zeros(3 * nVerts)  # vertices
        n = np.zeros(3 * nVerts)  # normals
        tex = np.zeros(2 * nVerts)  # tex coords
        el = np.zeros(elements, dtype=np.int32)  # elements

        # Generate positions and normals
        theta, phi = 0, 0
        thetaFac = 2 * np.pi / nSlices
        phiFac = np.pi / 2
        nx, ny, nz, s, t = 0.0, 0.0, 0.0, 0.0, 0.0
        idx = 0
        tIdx = 0
        for i in range(0, nSlices + 1):
            theta = i * thetaFac
            s = i / nSlices
            for j in range(0, 2 + 1):
                phi = j * phiFac
                t = j / 2
                nx = np.sin(phi) * np.cos(theta)
                ny = np.sin(phi) * np.sin(theta)
                nz = np.cos(phi)
                p[idx] = radius * nx;
                p[idx + 1] = radius * ny;
                p[idx + 2] = radius * nz
                n[idx] = nx;
                n[idx + 1] = ny;
                n[idx + 2] = nz
                idx += 3

                tex[tIdx] = s;
                tex[tIdx + 1] = t
                tIdx += 2
        # Generate the element list
        idx = 0
        for i in range(0, nSlices):
            stackStart = i * 3
            nextStackStart = (i + 1) * 3
            for j in range(0, 2):
                if j == 0:
                    el[idx] = stackStart;
                    el[idx + 1] = stackStart + 1;
                    el[idx + 2] = nextStackStart + 1
                    idx += 3
                elif j == 1:
                    el[idx] = stackStart + j;
                    el[idx + 1] = stackStart + j + 1;
                    el[idx + 2] = nextStackStart + j
                    idx += 3
                else:
                    el[idx] = stackStart + j;
                    el[idx + 1] = stackStart + j + 1;
                    el[idx + 2] = nextStackStart + j + 1;
                    el[idx + 3] = nextStackStart + j;
                    el[idx + 4] = stackStart + j;
                    el[idx + 5] = nextStackStart + j + 1
                    idx += 6
        p, color, n, tex, el = np.asarray(p).reshape((-1, 3)) * self.scaling, np.array([self.color] * int(len(p) / 3)).reshape((-1, 3)), np.asarray(n).reshape((-1, 3)), np.asarray(tex).reshape((-1, 2)), np.asarray(el)
        return p, color, n, tex, el

    def Cylinder(self, radius, height, nSlices):
        p = np.zeros(6 * (nSlices + 1), dtype='f')

        p[3] = radius
        phi_factor = 2 * np.pi / nSlices
        for ind in range(2, nSlices + 1):
            ...

    def Tube(self, radius, height, nSlices):
        p = np.zeros(6 * (nSlices + 1), dtype='f')
        n = np.zeros(6 * (nSlices + 1), dtype='f')
        el = np.zeros(6 * (nSlices + 1), dtype='i')
        t = np.zeros(4 * (nSlices + 1), dtype='f')
        p[0] = radius * self.scaling
        p[3], p[5] = radius * self.scaling, height * self.scaling
        phi_factor = 2 * np.pi / nSlices
        n[0], n[1], n[3], n[4] = 1.0, 0.0, 1.0, 0.0
        el[0], el[1], el[2], el[3], el[4], el[5] = 0, 1, 2, 1, 2, 3
        tIdx = 2
        t[0], t[1], t[2], t[3] = 0, 0, 1, 0
        for ind in range(1, nSlices + 1):
            nx = np.cos(phi_factor * ind)
            ny = np.sin(phi_factor * ind)
            nz = 0
            px, py = radius * nx, radius * ny
            p[6 * ind] = px * self.scaling
            p[6 * ind + 1] = py * self.scaling

            p[6 * ind + 3] = px * self.scaling
            p[6 * ind + 4] = py * self.scaling
            p[6 * ind + 5] = height * self.scaling

            n[6 * ind], n[6 * ind + 1], n[6 * ind + 3], n[6 * ind + 4] = nx, ny, nx, ny

            el[6 * ind], el[6 * ind + 1], el[6 * ind + 2], el[6 * ind + 3], el[6 * ind + 4], el[6 * ind + 5] = 2 * ind, 2 * ind + 1, 2 * ind + 2, 2 * ind + 1, 2 * ind + 2, 2 * ind + 3

            tFactor = ind / nSlices
            t[4 * ind], t[4 * ind + 1], t[4 * ind + 2], t[4 * ind + 3] = 0, tFactor, 1, tFactor
            tIdx += 4
        el[-4], el[-2], el[-1] = 0, 0, 1
        p, n, t = p.reshape((-1, 3)), n.reshape((-1, 3)), t.reshape((-1, 2))
        color = np.array([self.color] * 2 * (nSlices + 1)).reshape((-1, 3))
        return p, color, n, t, el
