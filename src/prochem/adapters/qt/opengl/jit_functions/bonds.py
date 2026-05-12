"""Jit functions for bonds detection."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from numba import jit
from numba.core.types import int64
import numpy as np
import logging
logging.getLogger('numba').setLevel(logging.INFO)

__all__ = [
    "nonoptimal_dimension_search",
    "neighbours_search_body",
    "neighbours_search",
    "neighbours_search_between_types_body",
    "neighbours_search_between_types"
]


@jit(fastmath=True, nopython=True, cache=True)
def nonoptimal_dimension_search(positions, number_of_dividings):
    """
    Calculates the index of the second largest dimension based on position data.
    
    This method analyzes a set of positions, divides the space into segments,
    and determines the dimension with the second largest range after considering
    these divisions.
    
    Args:
        positions: A sequence of positions.
        number_of_dividings: The number of divisions to use when analyzing the positions.
    
    Returns:
        int: The index (0, 1, or 2) of the dimension with the second largest range.
    """
    length = len(positions) - 1
    size_array = np.zeros((3, number_of_dividings + 1))
    delta_dim = np.zeros(3)
    for iteration in range(number_of_dividings + 1):
        step = iteration * length // number_of_dividings
        pos = positions[step].transpose()
        size_array[0] = pos[0].max() - pos[0].min()
        size_array[1] = pos[1].max() - pos[1].min()
        size_array[2] = pos[2].max() - pos[2].min()
    size_array = np.asarray(sizeArray)
    for index in range(3):
        delta_dim[index] = size_array[index].max() - size_array[index].min()
    return delta_dim.argsort()[-2]


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search_body(num, index, positions, indexes, dimension, bond_length):
    """
    Searches for neighboring indices within a specified bond length.
    
    This method performs a binary search to efficiently find indices in the `indexes`
    array that are within a given `bond_length` of a reference index `index`
    along a specific `dimension`.
    
    Args:
        num: An integer representing a lower bound for the search.
        index: The index of the reference atom.
        positions: A list of positions for each atom.
        indexes: A list of indices to search through.
        dimension: The dimension along which to search for neighbors.
        bond_length: The maximum distance allowed for a neighbor.
    
    Returns:
        A NumPy array containing the indices of neighboring atoms within the bond length.
    """
    highest_index = max_index = len(indexes) - num
    min_index = 0
    now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
    pos = positions[index][dimension]
    while True:
        index_comp = indexes[now_index - 1 + num]
        index_comp_next = indexes[now_index + num]
        statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
        statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
        if statement1 and not statement2:
            break
        elif now_index == highest_index - 1 and statement1 and statement2:
            now_index = highest_index
            break
        elif now_index == 0 and not statement1:
            break
        elif statement1 and statement2:
            min_index = now_index
            summary = now_index + max_index
            now_index = summary // 2 if not summary % 2 else summary // 2 + 1
        else:
            max_index = now_index
            summary = now_index + min_index
            now_index = summary // 2 if not summary % 2 else summary // 2 + 1
    tracking_pos = positions[index]
    returning_indexes = []
    for another_index in indexes[num + 1:now_index + num]:
        target_pos = positions[another_index]
        length = np.linalg.norm(tracking_pos - target_pos)
        if length <= bond_length:
            returning_indexes.append(another_index)
    return np.array(returning_indexes)


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search(search_algorithm, positions, indexes, dimension, bond_length):
    """
    Searches for neighbours based on a given algorithm and criteria.
    
    Args:
        search_algorithm: The function used to determine neighbours.
        positions: The positions of the items.
        indexes: The indexes of the items.
        dimension: The dimension of the space.
        bond_length: The bond length used as a criterion for neighbour search.
    
    Returns:
        A dictionary where keys are item indexes and values are their neighbours.
    """
    neighbours = dict()
    indexes_cp = indexes[:-1]
    for num, index in enumerate(indexes_cp):
        neighbours[int(index)] = search_algorithm(num, index, positions, indexes, dimension, bond_length)
    return neighbours


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search_between_types_body(index, positions, indexes, dimension, bond_length):
    """
    Searches for neighboring indices within a specified bond length.
    
    This method performs a binary search to efficiently find indices in the `indexes` list
    that are within a given `bond_length` of the index specified by `index` in the
    `positions` array, along a specific `dimension`.
    
    Args:
        index: The index of the central atom.
        positions: A NumPy array containing the positions of all atoms.
        indexes: A list of indices to search through.
        dimension: The dimension along which to search for neighbors.
        bond_length: The maximum distance allowed between atoms to be considered neighbors.
    
    Returns:
        A NumPy array containing the indices of neighboring atoms within the bond length.
    """
    highest_index = max_index = len(indexes)
    min_index = 0
    now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
    pos = positions[index][dimension]
    while True:
        index_comp = indexes[now_index - 1]
        index_comp_next = indexes[now_index]
        statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
        statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
        if statement1 and not statement2:
            break
        elif now_index == highest_index - 1 and statement1 and statement2:
            now_index = highest_index
            break
        elif now_index == 0 and not statement1:
            break
        elif statement1 and statement2:
            min_index = now_index
            summary = now_index + max_index
            now_index = summary // 2 if not summary % 2 else summary // 2 + 1
        else:
            max_index = now_index
            summary = now_index + min_index
            now_index = summary // 2
    tracking_pos = positions[index]
    returning_indexes = []
    for another_index in indexes[:now_index]:
        target_pos = positions[another_index]
        length = np.linalg.norm(tracking_pos - target_pos)
        if length <= bond_length:
            returning_indexes.append(another_index)
    return np.array(returning_indexes)


@jit(fastmath=True, nopython=True, cache=True)
def neighbours_search_between_types(search_algorithm, positions, indexes_type1, indexes_type2, dimension, bond_length):
    """
    Searches for neighbours between two types of items.
    
    Args:
        search_algorithm: The algorithm used to search for neighbours.
        positions: The positions of all items.
        indexes_type1: The indexes of the first type of items.
        indexes_type2: The indexes of the second type of items.
        dimension: The dimension of the space.
        bond_length: The bond length.
    
    Returns:
        A dictionary where keys are the indexes of the first type of items and values are their neighbours.
    """
    neighbours = dict()
    for _, index in enumerate(indexes_type1):
        neighbours[int64(index)] = search_algorithm(index, positions, indexes_type2, dimension, bond_length)
    return neighbours

