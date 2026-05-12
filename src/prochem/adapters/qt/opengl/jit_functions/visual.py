"""Jit functions for matrix calculations."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from numba import jit
import numpy as np
import logging
logging.getLogger('numba').setLevel(logging.INFO)

__all__ = [
    "rotate",
    "transform_vec3",
    "perspective",
    "ortho",
    "look_at",
    "perspective_choose",
    "orthographic_choose"
]


@jit(fastmath=True, nopython=True, cache=True)
def rotate(old_matrix, dx, dy, dz, limit_rotations=True) -> np.ndarray:
    """Defines new rotation matrix."""
    if limit_rotations:
        dx, dy, dz = dx % 360, dy % 360, dz % 360
    rotate_x = np.array([[1.0, 0.0, 0.0, 0.0],
                         [0.0, np.cos(np.radians(dx)), -np.sin(np.radians(dx)), 0.0],
                         [0.0, np.sin(np.radians(dx)), np.cos(np.radians(dx)), 0.0],
                         [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
    rotate_y = np.array([[np.cos(np.radians(dy)), 0.0, np.sin(np.radians(dy)), 0.0],
                           [0.0, 1.0, 0.0, 0.0],
                           [-np.sin(np.radians(dy)), 0.0, np.cos(np.radians(dy)), 0.0],
                           [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
    rotate_z = np.array([[np.cos(np.radians(dz)), -np.sin(np.radians(dz)), 0.0, 0.0],
                           [np.sin(np.radians(dz)), np.cos(np.radians(dz)), 0.0, 0.0],
                           [0.0, 0.0, 1.0, 0.0],
                           [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
    matrix = np.dot(rotate_z, np.dot(rotate_y, rotate_x))
    return np.dot(old_matrix, matrix)


@jit(fastmath=True, nopython=True, cache=True)
def transform_vec3(vec_a, mat44) -> tuple[list[float], int]:
    """Transform 3d vector to 2d projection."""
    vec_b = [0, 0, 0, 0]
    for i in range(0, 4):
        vec_b[i] = vec_a[0] * mat44[0 * 4 + i] + vec_a[1] * mat44[1 * 4 + i] + vec_a[2] * mat44[2 * 4 + i] + mat44[3 * 4 + i]
    return [vec_b[0] / vec_b[3], vec_b[1] / vec_b[3], vec_b[2] / vec_b[3]], vec_b[3]


@jit(fastmath=True, nopython=True, cache=True)
def perspective(fovy, aspect, znear, zfar) -> np.ndarray:
    """Defines new perspective matrix."""
    f = 1.0 / np.tan(np.radians(fovy) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (zfar + znear) / (znear - zfar)
    m[2, 3] = (2 * zfar * znear) / (znear - zfar)
    m[3, 2] = -1.0
    return m


@jit(fastmath=True, nopython=True, cache=True)
def ortho(left, right, top, bottom, near, far) -> np.ndarray:
    """Build the orthographic matrix according to the formula:
    2 / (r - l)      , 0.0               , 0.0                 , 0.0
    0.0              , 2 / (t - b)       , 0.0                 , 0.0
    0.0              , 0.0               , 1 / (near - far)    , 0.0
    (l + r) / (l - r), (t + b) / (b - t) , near / (near - far) , 1.0
    """
    pMatrix = np.array([[2 / (right - left), 0.0, 0.0, 0.0],
                        [0.0, 2 / (top - bottom), 0.0, 0.0],
                        [0.0, 0.0, 1 / (near - far), 0.0],
                        [(left + right) / (left - right), (top + bottom) / (bottom - top), near / (near - far), 1.0]], np.float32)
    return pMatrix


@jit(fastmath=True, nopython=True, cache=True)
def look_at(eye, center, up) -> np.ndarray:
    """Defines new view matrix."""
    f = center - eye
    f = f / np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    trans = np.identity(4, dtype=np.float32)
    trans[0, 3] = -eye[0]
    trans[1, 3] = -eye[1]
    trans[2, 3] = -eye[2]
    return m @ trans


@jit(fastmath=True, nopython=True)
def perspective_choose(prj_mat, mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with perspective view.
       prjMat - projection matrix, mpos - mouse position at the screen,
       ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    ll_ndc = [[0.0 for i in range(3)] for m in range(len(ll))]
    in_rect_counter = 0  # atoms in sphere counter
    depth = list()  # atoms in sphere list
    mult = [0.0 for _ in range(len(ll))]  # коэффициенты масштабирования пространства
    for num in range(len(ll)):
        ll_ndc[num], mult[num] = transform_vec3(ll[num], prj_mat)  # координаты в мировом пространстве???
    radii = [parameter[i] / mult[i] * 1.0 for i in range(len(ll))]  # radius of projected sphere
    ndc = [2.0 * mpos[0] / dis[0] - 1.0, 1.0 - 2.0 * mpos[1] / dis[1]]
    in_rect = [0 for _ in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll_ndc[num][0] - radii[num] <= ndc[0] <= ll_ndc[num][0] + radii[num] and ll_ndc[num][1] - radii[num] <= ndc[1] <= ll_ndc[num][1] + radii[num]:
            in_rect[num] = 1
        else:
            in_rect[num] = 0
    for num in range(len(ll)):
        if in_rect[num] == 1:
            in_rect_counter += 1  # число попаданий
            depth.append(ll_ndc[num][2])  # координаты по глубине
    if in_rect_counter > 1:
        right_vec = min(depth)
        for num in range(len(ll)):
            if ll_ndc[num][2] != right_vec:
                in_rect[num] = 0
    return in_rect


@jit(fastmath=True, nopython=True)
def orthographic_choose(mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with orthographic view.
    mpos - mouse position at the screen, ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    ortho_size = (12, 9)
    coordinate = [(1.0 - 2.0 * mpos[0] / dis[0]) * ortho_size[0], (1.0 - 2.0 * mpos[1] / dis[1]) * ortho_size[1]]
    in_rect_counter = 0  # atoms in sphere counter
    depth = []  # atoms in sphere list
    in_rect = [0 for m in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll[num][0] - parameter[num] <= coordinate[0] <= ll[num][0] + parameter[num] and ll[num][2] - parameter[num] <= coordinate[1] <= ll[num][2] + parameter[num]:
            in_rect[num] = 1
        else:
            in_rect[num] = 0
    for num in range(len(ll)):
        if in_rect[num] == 1:
            in_rect_counter += 1  # число попаданий
            depth.append(ll[num][1])  # координаты по глубине
    if in_rect_counter > 1:
        right_vec = max(depth)
        for num in range(len(ll)):
            if ll[num][1] != right_vec:
                in_rect[num] = 0
    return in_rect
