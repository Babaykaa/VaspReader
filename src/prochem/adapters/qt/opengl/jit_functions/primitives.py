"""Jit functions for primitives creation."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from numba import jit
import numpy as np
import logging
logging.getLogger('numba').setLevel(logging.INFO)

__all__ = [
    "Quad",
    "Cube",
    "Parallelepiped",
    "Sphere",
    "Torus",
    "Yula",
    "Tube",
    "Cone"
]


@jit(fastmath=True, nopython=True, cache=True)
def Quad(scaling, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates quad."""
    vertex = np.array([[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [-1.0, 1.0, 0.0]]) * scaling
    normal = np.array([[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [-1.0, 1.0, 0.0]])
    texture_indexes = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    if draw_type == 'TRIANGLES':
        indexes = np.array([0, 1, 2, 0, 2, 3])
    elif draw_type == 'QUADS':
        indexes = np.array([0, 1, 2, 3])
    return vertex, normal, texture_indexes, indexes, draw_type


@jit(fastmath=True, nopython=True, cache=True)
def Cube(scaling, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates cube."""
    vertex = np.array([[-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, -1.0],
                       [1.0, 1.0, 1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0],
                       [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0],
                       [-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0],
                       [-1.0, -1.0, 1.0], [-1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, -1.0, 1.0],
                       [-1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [1.0, 1.0, -1.0], [1.0, -1.0, -1.0]]) * scaling
    normal = np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0],
                       [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                       [0.0, -1.0, 0.0], [0.0, -1.0, 0.0], [0.0, -1.0, 0.0], [0.0, -1.0, 0.0],
                       [-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0],
                       [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0],
                       [0.0, 0.0, -1.0], [0.0, 0.0, -1.0], [0.0, 0.0, -1.0], [0.0, 0.0, -1.0]])
    texture_indexes = np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0],
                                [1.0, 1.0], [1.0, 0.0], [0.0, 0.0], [0.0, 1.0],
                                [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0],
                                [1.0, 1.0], [1.0, 0.0], [0.0, 0.0], [0.0, 1.0],
                                [0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0],
                                [0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    if draw_type == 'TRIANGLES' or draw_type == 'TRIANGLE_STRIP':
        indexes = np.array([0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7, 8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15, 16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23])
    elif draw_type == 'LINES':
        indexes = np.array([0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 8, 9, 9, 10, 10, 11, 11, 8, 12, 13, 13, 14, 14, 15, 15, 12, 16, 17, 17, 18, 18, 19, 19, 16, 20, 21, 21, 22, 22, 23, 23, 20])
    elif draw_type == 'QUADS':
        indexes = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
    return vertex, normal, texture_indexes, indexes, draw_type


@jit(fastmath=True, nopython=True, cache=True)
def Parallelepiped(vec_x, vec_y, vec_z, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates parallelepiped."""
    vec_x = np.array(vec_x, dtype=np.float32)
    vec_y = np.array(vec_y, dtype=np.float32)
    vec_z = np.array(vec_z, dtype=np.float32)
    vertex = np.array([[(-vec_x[0] + vec_y[0] - vec_z[0]) / 2, (-vec_x[1] + vec_y[1] - vec_z[1]) / 2, (-vec_x[2] + vec_y[2] - vec_z[2]) / 2],
                       [(-vec_x[0] + vec_y[0] + vec_z[0]) / 2, (-vec_x[1] + vec_y[1] + vec_z[1]) / 2, (-vec_x[2] + vec_y[2] + vec_z[2]) / 2],
                       [(vec_x[0] + vec_y[0] + vec_z[0]) / 2, (vec_x[1] + vec_y[1] + vec_z[1]) / 2, (vec_x[2] + vec_y[2] + vec_z[2]) / 2],
                       [(vec_x[0] + vec_y[0] - vec_z[0]) / 2, (vec_x[1] + vec_y[1] - vec_z[1]) / 2, (vec_x[2] + vec_y[2] - vec_z[2]) / 2],
                       [(vec_x[0] + vec_y[0] + vec_z[0]) / 2, (vec_x[1] + vec_y[1] + vec_z[1]) / 2, (vec_x[2] + vec_y[2] + vec_z[2]) / 2],
                       [(vec_x[0] + vec_y[0] - vec_z[0]) / 2, (vec_x[1] + vec_y[1] - vec_z[1]) / 2, (vec_x[2] + vec_y[2] - vec_z[2]) / 2],
                       [(vec_x[0] - vec_y[0] - vec_z[0]) / 2, (vec_x[1] - vec_y[1] - vec_z[1]) / 2, (vec_x[2] - vec_y[2] - vec_z[2]) / 2],
                       [(vec_x[0] - vec_y[0] + vec_z[0]) / 2, (vec_x[1] - vec_y[1] + vec_z[1]) / 2, (vec_x[2] - vec_y[2] + vec_z[2]) / 2],
                       [(vec_x[0] - vec_y[0] - vec_z[0]) / 2, (vec_x[1] - vec_y[1] - vec_z[1]) / 2, (vec_x[2] - vec_y[2] - vec_z[2]) / 2],
                       [(vec_x[0] - vec_y[0] + vec_z[0]) / 2, (vec_x[1] - vec_y[1] + vec_z[1]) / 2, (vec_x[2] - vec_y[2] + vec_z[2]) / 2],
                       [(-vec_x[0] - vec_y[0] + vec_z[0]) / 2, (-vec_x[1] - vec_y[1] + vec_z[1]) / 2, (-vec_x[2] - vec_y[2] + vec_z[2]) / 2],
                       [(-vec_x[0] - vec_y[0] - vec_z[0]) / 2, (-vec_x[1] - vec_y[1] - vec_z[1]) / 2, (-vec_x[2] - vec_y[2] - vec_z[2]) / 2],
                       [(-vec_x[0] - vec_y[0] + vec_z[0]) / 2, (-vec_x[1] - vec_y[1] + vec_z[1]) / 2, (-vec_x[2] - vec_y[2] + vec_z[2]) / 2],
                       [(-vec_x[0] - vec_y[0] - vec_z[0]) / 2, (-vec_x[1] - vec_y[1] - vec_z[1]) / 2, (-vec_x[2] - vec_y[2] - vec_z[2]) / 2],
                       [(-vec_x[0] + vec_y[0] - vec_z[0]) / 2, (-vec_x[1] + vec_y[1] - vec_z[1]) / 2, (-vec_x[2] + vec_y[2] - vec_z[2]) / 2],
                       [(-vec_x[0] + vec_y[0] + vec_z[0]) / 2, (-vec_x[1] + vec_y[1] + vec_z[1]) / 2, (-vec_x[2] + vec_y[2] + vec_z[2]) / 2],
                       [(-vec_x[0] - vec_y[0] + vec_z[0]) / 2, (-vec_x[1] - vec_y[1] + vec_z[1]) / 2, (-vec_x[2] - vec_y[2] + vec_z[2]) / 2],
                       [(-vec_x[0] + vec_y[0] + vec_z[0]) / 2, (-vec_x[1] + vec_y[1] + vec_z[1]) / 2, (-vec_x[2] + vec_y[2] + vec_z[2]) / 2],
                       [(vec_x[0] + vec_y[0] + vec_z[0]) / 2, (vec_x[1] + vec_y[1] + vec_z[1]) / 2, (vec_x[2] + vec_y[2] + vec_z[2]) / 2],
                       [(vec_x[0] - vec_y[0] + vec_z[0]) / 2, (vec_x[1] - vec_y[1] + vec_z[1]) / 2, (vec_x[2] - vec_y[2] + vec_z[2]) / 2], 
                       [(-vec_x[0] - vec_y[0] - vec_z[0]) / 2, (-vec_x[1] - vec_y[1] - vec_z[1]) / 2, (-vec_x[2] - vec_y[2] - vec_z[2]) / 2],
                       [(-vec_x[0] + vec_y[0] - vec_z[0]) / 2, (-vec_x[1] + vec_y[1] - vec_z[1]) / 2, (-vec_x[2] + vec_y[2] - vec_z[2]) / 2],
                       [(vec_x[0] + vec_y[0] - vec_z[0]) / 2, (vec_x[1] + vec_y[1] - vec_z[1]) / 2, (vec_x[2] + vec_y[2] - vec_z[2]) / 2],
                       [(vec_x[0] - vec_y[0] - vec_z[0]) / 2, (vec_x[1] - vec_y[1] - vec_z[1]) / 2, (vec_x[2] - vec_y[2] - vec_z[2]) / 2]], dtype=np.float32)
    vec_x = vec_x / np.linalg.norm(vec_x)
    vec_y = vec_y / np.linalg.norm(vec_y)
    vec_z = vec_z / np.linalg.norm(vec_z)
    normal = np.array([[vec_y[0], vec_y[1], vec_y[2]], [vec_y[0], vec_y[1], vec_y[2]], [vec_y[0], vec_y[1], vec_y[2]], [vec_y[0], vec_y[1], vec_y[2]],
                       [vec_x[0], vec_x[1], vec_x[2]], [vec_x[0], vec_x[1], vec_x[2]], [vec_x[0], vec_x[1], vec_x[2]], [vec_x[0], vec_x[1], vec_x[2]],
                       [-vec_y[0], -vec_y[1], -vec_y[2]], [-vec_y[0], -vec_y[1], -vec_y[2]], [-vec_y[0], -vec_y[1], -vec_y[2]], [-vec_y[0], -vec_y[1], -vec_y[2]],
                       [-vec_x[0], -vec_x[1], -vec_x[2]], [-vec_x[0], -vec_x[1], -vec_x[2]], [-vec_x[0], -vec_x[1], -vec_x[2]], [-vec_x[0], -vec_x[1], -vec_x[2]],
                       [vec_z[0], vec_z[1], vec_z[2]], [vec_z[0], vec_z[1], vec_z[2]], [vec_z[0], vec_z[1], vec_z[2]], [vec_z[0], vec_z[1], vec_z[2]],
                       [-vec_z[0], -vec_z[1], -vec_z[2]], [-vec_z[0], -vec_z[1], -vec_z[2]], [-vec_z[0], -vec_z[1], -vec_z[2]], [-vec_z[0], -vec_z[1], -vec_z[2]]])
    texture_indexes = np.array([[1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0],
                                [1.0, 1.0], [1.0, 0.0], [0.0, 0.0], [0.0, 1.0],
                                [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0],
                                [1.0, 1.0], [1.0, 0.0], [0.0, 0.0], [0.0, 1.0],
                                [0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0],
                                [0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    if draw_type == 'TRIANGLES' or draw_type == 'TRIANGLE_STRIP':
        indexes = np.array([0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7, 8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15, 16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23])
    elif draw_type == 'LINES':
        indexes = np.array([0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 8, 9, 9, 10, 10, 11, 11, 8, 12, 13, 13, 14, 14, 15, 15, 12, 16, 17, 17, 18, 18, 19, 19, 16, 20, 21, 21, 22, 22, 23, 23, 20])
    elif draw_type == 'QUADS':
        indexes = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
    return vertex, normal, texture_indexes, indexes, draw_type


@jit(fastmath=True, nopython=True, cache=True)
def Sphere(scaling, n_slices, n_stacks, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates sphere."""
    verts_number = (n_slices + 1) * (n_stacks + 1)
    elements = (n_slices * 2 * (n_stacks - 1)) * 3
    vertex = np.zeros(3 * verts_number)
    normal = np.zeros(3 * verts_number)
    texture_indexes = np.zeros(2 * verts_number)
    indexes = np.zeros(elements, dtype=np.int32)

    # Generate positions and normals
    theta, phi = 0, 0
    theta_fac = 2 * np.pi / n_slices
    phi_fac = np.pi / n_stacks
    nx, ny, nz, s, t = 0.0, 0.0, 0.0, 0.0, 0.0
    idx = 0
    t_idx = 0
    for i in range(0, n_slices + 1):
        theta = i * theta_fac
        s = i / n_slices
        for j in range(0, n_stacks + 1):
            phi = j * phi_fac
            t = j / n_stacks
            nx = np.sin(phi) * np.cos(theta)
            ny = np.sin(phi) * np.sin(theta)
            nz = np.cos(phi)
            
            vertex[idx] = scaling * nx
            vertex[idx + 1] = scaling * ny 
            vertex[idx + 2] = scaling * nz
            
            normal[idx] = nx
            normal[idx + 1] = ny
            normal[idx + 2] = nz
            
            idx += 3

            texture_indexes[t_idx] = s
            texture_indexes[t_idx + 1] = t
            
            t_idx += 2
    
    # Generate the element list
    idx = 0
    for i in range(0, n_slices):
        stack_start = i * (n_stacks + 1)
        next_stack_start = (i + 1) * (n_stacks + 1)
        for j in range(0, n_stacks):
            if j == 0:
                indexes[idx] = stack_start
                indexes[idx + 1] = stack_start + 1
                indexes[idx + 2] = next_stack_start + 1
                idx += 3
            elif j == n_stacks - 1:
                indexes[idx] = stack_start + j
                indexes[idx + 1] = stack_start + j + 1
                indexes[idx + 2] = next_stack_start + j
                idx += 3
            else:
                indexes[idx] = stack_start + j
                indexes[idx + 1] = stack_start + j + 1
                indexes[idx + 2] = next_stack_start + j + 1; 
                indexes[idx + 3] = next_stack_start + j
                indexes[idx + 4] = stack_start + j
                indexes[idx + 5] = next_stack_start + j + 1
                idx += 6
    vertex = vertex.reshape((-1, 3))
    normal = normal.reshape((-1, 3))
    texture_indexes = texture_indexes.reshape((-1, 2))
    return vertex, normal, texture_indexes, indexes, draw_type

@jit(fastmath=True, nopython=True, cache=True)
def Torus(scaling, outer_radius, inner_radius, n_slices, n_rings, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates torus."""
    faces = n_slices * n_rings
    verts_number = n_slices * (n_rings + 1) # One extra ring to duplicate first ring

    vertex = np.zeros(3 * verts_number)
    normal = np.zeros(3 * verts_number)
    texture_indexes = np.zeros(2 * verts_number)
    indexes = np.zeros(6 * faces, dtype=np.int32)

    # Generate the vertex data
    ring_factor = 2 * np.pi / n_rings
    side_factor = 2 * np.pi / n_slices
    idx = 0
    tidx = 0
    for ring in range(0, n_rings + 1):
        u = ring * ring_factor
        cu = np.cos(u)
        su = np.sin(u)
        for side in range(0, n_slices):
            v = side * side_factor
            cv = np.cos(v)
            sv = np.sin(v)
            r = outer_radius + inner_radius * cv
            
            vertex[idx] = r * cu
            vertex[idx + 1] = r * su
            vertex[idx + 2] = inner_radius * sv
            normal[idx] = cv * cu * r
            normal[idx + 1] = cv * su * r
            normal[idx + 2] = sv * r
            texture_indexes[tidx] = u / (2 * np.pi)
            texture_indexes[tidx + 1] = v / (2 * np.pi)
            tidx += 2
            # Normalize
            lenn = np.sqrt(normal[idx] ** 2 + normal[idx + 1] ** 2 + normal[idx + 2] ** 2)
            normal[idx] /= lenn; normal[idx + 1] /= lenn; normal[idx + 2] /= lenn
            idx += 3

    idx = 0
    for ring in range(0, n_rings):
        ring_start = ring * n_slices
        next_ring_start = (ring + 1) * n_slices
        for side in range(0, n_slices):
            next_side = (side + 1) % n_slices
            # The quad
            indexes[idx] = ring_start + side
            indexes[idx + 1] = next_ring_start + side
            indexes[idx + 2] = next_ring_start + next_side
            indexes[idx + 3] = ring_start + side
            indexes[idx + 4] = next_ring_start + next_side
            indexes[idx + 5] = ring_start + next_side
            idx += 6
    vertex = vertex.reshape((-1, 3))
    normal = normal.reshape((-1, 3))
    texture_indexes = texture_indexes.reshape((-1, 2))
    return vertex, normal, texture_indexes, indexes, draw_type


@jit(fastmath=True, nopython=True, cache=True)
def Yula(scaling, n_slices, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates yula."""
    verts_number = (n_slices + 1) * 3
    elements = (n_slices * 2) * 3
    vertex = np.zeros(3 * verts_number)
    normal = np.zeros(3 * verts_number)
    texture_indexes = np.zeros(2 * verts_number)
    indexes = np.zeros(elements, dtype=np.int32)

    # Generate positions and normals
    theta, phi = 0, 0
    theta_fac = 2 * np.pi / n_slices
    phi_fac = np.pi / 2
    nx, ny, nz, s, t = 0.0, 0.0, 0.0, 0.0, 0.0
    idx = 0
    t_idx = 0
    for i in range(0, n_slices + 1):
        theta = i * theta_fac
        s = i / n_slices
        for j in range(0, 2 + 1):
            phi = j * phi_fac
            t = j / 2
            nx = np.sin(phi) * np.cos(theta)
            ny = np.sin(phi) * np.sin(theta)
            nz = np.cos(phi)

            vertex[idx] = scaling * nx
            vertex[idx + 1] = scaling * ny
            vertex[idx + 2] = scaling * nz
            normal[idx] = nx
            normal[idx + 1] = ny
            normal[idx + 2] = nz
            idx += 3

            texture_indexes[t_idx] = s
            texture_indexes[t_idx + 1] = t
            t_idx += 2
    # Generate the element list
    idx = 0
    for i in range(0, n_slices):
        stack_start = i * 3
        next_stack_start = (i + 1) * 3
        for j in range(0, 2):
            if j == 0:
                indexes[idx] = stack_start
                indexes[idx + 1] = stack_start + 1
                indexes[idx + 2] = next_stack_start + 1
                idx += 3
            elif j == 1:
                indexes[idx] = stack_start + j
                indexes[idx + 1] = stack_start + j + 1
                indexes[idx + 2] = next_stack_start + j
                idx += 3
            else:
                indexes[idx] = stack_start + j
                indexes[idx + 1] = stack_start + j + 1
                indexes[idx + 2] = next_stack_start + j + 1
                indexes[idx + 3] = next_stack_start + j
                indexes[idx + 4] = stack_start + j
                indexes[idx + 5] = next_stack_start + j + 1
                idx += 6
    vertex = vertex.reshape((-1, 3))
    normal = normal.reshape((-1, 3))
    texture_indexes = texture_indexes.reshape((-1, 2))
    return vertex, normal, texture_indexes, indexes, draw_type


@jit(fastmath=True, nopython=True, cache=True)
def Tube(radius, height, n_slices, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates tube."""
    vertex = np.zeros(6 * (n_slices + 1))
    normal = np.zeros(6 * (n_slices + 1))
    indexes = np.zeros(6 * (n_slices + 1), dtype=np.int32)
    texture_indexes = np.zeros(4 * (n_slices + 1))
    vertex[0] = radius
    vertex[3], vertex[5] = radius, height
    phi_factor = 2 * np.pi / n_slices
    normal[0], normal[1], normal[3], normal[4] = 1.0, 0.0, 1.0, 0.0
    indexes[0], indexes[1], indexes[2], indexes[3], indexes[4], indexes[5] = 0, 1, 2, 1, 2, 3
    t_idx = 2
    texture_indexes[0], texture_indexes[1], texture_indexes[2], texture_indexes[3] = 0, 0, 1, 0
    for ind in range(1, n_slices + 1):
        nx = np.cos(phi_factor * ind)
        ny = np.sin(phi_factor * ind)
        nz = 0
        px, py = radius * nx, radius * ny
        vertex[6 * ind] = px
        vertex[6 * ind + 1] = py

        vertex[6 * ind + 3] = px
        vertex[6 * ind + 4] = py
        vertex[6 * ind + 5] = height

        normal[6 * ind], normal[6 * ind + 1], normal[6 * ind + 3], normal[6 * ind + 4] = nx, ny, nx, ny

        indexes[6 * ind], indexes[6 * ind + 1], indexes[6 * ind + 2], indexes[6 * ind + 3], indexes[6 * ind + 4], indexes[6 * ind + 5] = 2 * ind, 2 * ind + 1, 2 * ind + 2, 2 * ind + 1, 2 * ind + 2, 2 * ind + 3

        t_factor = ind / n_slices
        texture_indexes[4 * ind], texture_indexes[4 * ind + 1], texture_indexes[4 * ind + 2], texture_indexes[4 * ind + 3] = 0, t_factor, 1, t_factor
        t_idx += 4
    indexes[-4], indexes[-2], indexes[-1] = 0, 0, 1
    vertex = vertex.reshape((-1, 3))
    normal = normal.reshape((-1, 3))
    texture_indexes = texture_indexes.reshape((-1, 2))
    return vertex, normal, texture_indexes, indexes, draw_type


@jit(fastmath=True, nopython=True, cache=True)
def Cone(radius, height, n_slices, draw_type='TRIANGLES') -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    """Creates cone."""
    vertex = np.zeros(6 * (n_slices + 1))
    normal = np.zeros(6 * (n_slices + 1))
    indexes = np.zeros(6 * (n_slices + 1), dtype=np.int32)
    texture_indexes = np.zeros(4 * (n_slices + 1))
    vertex[0] = radius
    vertex[5] = height
    phi_factor = 2 * np.pi / n_slices
    normal[0], normal[1], normal[3], normal[4] = 1.0, 0.0, 1.0, 0.0
    indexes[0], indexes[1], indexes[2], indexes[3], indexes[4], indexes[5] = 0, 1, 2, 1, 2, 3
    t_idx = 2
    texture_indexes[0], texture_indexes[1], texture_indexes[2], texture_indexes[3] = 0, 0, 1, 0
    for ind in range(1, n_slices + 1):
        nx = np.cos(phi_factor * ind)
        ny = np.sin(phi_factor * ind)
        nz = 0
        px, py = radius * nx, radius * ny
        vertex[6 * ind] = px
        vertex[6 * ind + 1] = py
        vertex[6 * ind + 5] = height

        normal[6 * ind], normal[6 * ind + 1], normal[6 * ind + 3], normal[6 * ind + 4] = nx, ny, nx, ny

        indexes[6 * ind], indexes[6 * ind + 1], indexes[6 * ind + 2], indexes[6 * ind + 3], indexes[6 * ind + 4], indexes[6 * ind + 5] = 2 * ind, 2 * ind + 1, 2 * ind + 2, 2 * ind + 1, 2 * ind + 2, 2 * ind + 3

        t_factor = ind / n_slices
        texture_indexes[4 * ind], texture_indexes[4 * ind + 1], texture_indexes[4 * ind + 2], texture_indexes[4 * ind + 3] = 0, t_factor, 1, t_factor
        t_idx += 4
    indexes[-4], indexes[-2], indexes[-1] = 0, 0, 1
    vertex = vertex.reshape((-1, 3))
    normal = normal.reshape((-1, 3))
    texture_indexes = texture_indexes.reshape((-1, 2))
    return vertex, normal, texture_indexes, indexes, draw_type
