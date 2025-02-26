"""Partition tank definition."""
import wtrwrks.waterworks.waterwork_part as wp
import wtrwrks.waterworks.tank as ta
import wtrwrks.tanks.utils as ut
import numpy as np

class Partition(ta.Tank):
  """The defintion of the Partition tank. Contains the implementations of the _pour and _pump methods, as well as which slots and tubes the waterwork objects will look for.

  Attributes
  ----------
  slot_keys: list of strs
    The names off all the tank's slots, i.e. inputs in the pour (forward) direction, or outputs in the pump (backward) direction
  tubes: list of strs
    The names off all the tank's tubes, i.e. outputs in the pour (forward) direction,

  """

  slot_keys = ['a', 'indices']
  tube_keys = ['target', 'indices', 'missing_cols', 'missing_array']

  def _pour(self, a, indices):
    """Execute the Partition tank (operation) in the pour (forward) direction.

    Parameters
    ----------
    a: np.ndarray
      The array to take slices from.
    indices: np.ndarray
      The index ranges of each slice. The first dimension can be of any size and the second dimension must be two.

    Returns
    -------
    dict(
      target: list of arrays
        The list of array slices. The length of the list is equal to the size of the first dimension of 'indices'.
      indices: np.ndarray of ints
        The index ranges of each slice. The first dimension can be of any size and the second dimension must be two.
      missing_cols: np.ndarray of ints
        The columns of the array that were not selected by the slices defined by 'indices'
      missing_array: np.ndarray
        The slices of array that were not selected by the slices defined by 'indices'.
    )

    """
    # Cast everything to a numpy array.
    a = np.array(a)
    indices = np.array(indices)
    full_cols = np.arange(a.shape[0], dtype=int)

    target = []
    all_ranges = []
    # Go through each col range which defines a slice.
    for col_range in indices:
      target.append(a[col_range[0]: col_range[1]])

      # Add all the column numbers in the slice to an array.
      all_ranges.append(np.arange(col_range[0], col_range[1]))

    # Find all the columns which did not appear in some slice. Save those
    # columns and extract the corresponding slices from the array 'a'
    all_ranges = np.concatenate(all_ranges, axis=0)
    missing_cols = np.setdiff1d(full_cols, all_ranges)
    missing_array = a[missing_cols]

    return {'target': target, 'indices': indices, 'missing_cols': missing_cols, 'missing_array': missing_array}

  def _pump(self, target, indices, missing_cols, missing_array):
    """Execute the Partition tank (operation) in the pump (backward) direction.

    Parameters
    ----------
    target: list of arrays
      The list of array slices. The length of the list is equal to the size of the first dimension of 'indices'.
    indices: np.ndarray of ints
      The index ranges of each slice. The first dimension can be of any size and the second dimension must be two.
    missing_cols: np.ndarray of ints
      The columns of the array that were not selected by the slices defined by 'indices'
    missing_array: np.ndarray
      The slices of array that were not selected by the slices defined by 'indices'.

    Returns
    -------
    dict(
      a: np.ndarray
        The array to take slices from.
      indices: np.ndarray
        The index ranges of each slice. The first dimension can be of any size and the second dimension must be two.
    )

    """
    # Get the total length of the partitioned dimension. Handling the empty
    # array case.
    if target or missing_cols:
      max_index = np.max(np.concatenate([indices[:, 1] - 1, missing_cols.flatten()]))
    else:
      max_index = -1

    # If the target list isn't empty then take the sizes of the dimensions not
    # involved in the partition. Otherwise, use the missing array to get the
    # shape.
    if target:
      inner_dims = target[0].shape[1:]
    else:
      inner_dims = missing_array.shape[1:]

    # Create the empty array
    a = np.zeros([max_index + 1] + list(inner_dims), dtype=missing_array.dtype)

    # Go through each of the partitions to fill the array a back up with
    # the slices.
    for subarray, col_range in zip(target, indices):
      a[col_range[0]: col_range[1]] = subarray

    # Add any of the missing columns back in as well.
    for col_num, col in enumerate(missing_cols):
      a[col] = missing_array[col_num]

    return {'a': a, 'indices': indices}
