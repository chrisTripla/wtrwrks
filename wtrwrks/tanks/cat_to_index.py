"""CatToIndex tank definition."""
import wtrwrks.waterworks.waterwork_part as wp
import wtrwrks.waterworks.tank as ta
import wtrwrks.tanks.utils as ut
import wtrwrks.utils.array_functions as af
import numpy as np


class CatToIndex(ta.Tank):
  """The CatToIndex class where the cats input is an numpy array. Handles any rank for 'cats'

  Attributes
  ----------
  slot_keys : list of str
    The tank's (operation's) argument keys. They define the names of the inputs to the tank.
  tube_keys : dict(
    keys - strs. The tank's (operation's) output keys. THey define the names of the outputs of the tank
    values - types. The types of the arguments outputs.
  )
    The tank's (operation's) output keys and their corresponding types.

  """
  slot_keys = ['cats', 'cat_to_index_map']
  tube_keys = ['target', 'cat_to_index_map', 'missing_vals', 'input_dtype']

  def _pour(self, cats, cat_to_index_map):
    """Execute the mapping in the pour (forward) direction .

    Parameters
    ----------
    cats : np.ndarray
      The categorical values to be mapped to indices
    cat_to_index_map : dict
      The map from categorical values to indices.

    Returns
    -------
    dict(
      'target': int, float, other non array type
        The result of the sum of 'a' and 'b'.
      'missing_vals': list
        The list of all the cats that were not found in cat_to_index_map.
      'cat_to_index_map' : dict
        The map from categorical values to indices.
    )

    """
    cats = np.array(cats, copy=True)
    shape = cats.shape
    is_float = cats.dtype in (np.float64, np.float32)
    nan_val = -1
    if is_float:
      for key, value in cat_to_index_map.iteritems():
        if np.isnan(key):
          nan_val = value
          break
    # Pull out all the cats which are not in the cat_to_index_map.
    # If you have a nan not in a float, you're going to get
    # unexpected results, so here we force nans not to show up in
    # missing vals if they are in the cat_to_index_map.
    missing_vals = af.empty_array_like(cats)
    if is_float:
      isnan = np.array([True if str(v) == 'nan' else False for v in cats.flatten()]).reshape(cats.shape)
      mask = (~np.isin(cats, cat_to_index_map.keys())) & (~isnan)
      missing_vals[mask] = cats[mask]
    else:
      mask = ~np.isin(cats, cat_to_index_map.keys())
      missing_vals[mask] = cats[mask]

    # Map all the categorical values to indices, setting an index of -1
    # every time an unsupported category is encoutered.
    def safe_map(cat):
      if cat in cat_to_index_map:
        return cat_to_index_map[cat]
      elif is_float and np.isnan(cat):
        return nan_val
      else:
        return -1
    target = np.vectorize(safe_map)(cats)
    target = target.reshape(shape)

    return {'target': target, 'missing_vals': missing_vals, 'cat_to_index_map': cat_to_index_map, 'input_dtype': cats.dtype}

  def _pump(self, target, missing_vals, cat_to_index_map, input_dtype):
    """Execute the mapping in the pump (backward) direction .

    Parameters
    ----------
    target: np.ndarray
      The result of the sum of 'a' and 'b'.
    missing_vals: list
      The list of all the cats that were not found in cat_to_index_map.
    cat_to_index_map : dict
      The map from categorical values to indices.


    Returns
    -------
    dict(
      'cats' : np.ndarray
        The categorical values to be mapped to indices
      'cat_to_index_map' : dict
        The map from categorical values to indices.
    )

    """
    missing_vals = np.array(missing_vals)
    # Convert the cat_to_index_map into an index_to_cat_map, while making
    # sure it is one-to-one. Otherwise it isn't reversible.
    index_to_cat_map = {}
    for k, v in cat_to_index_map.iteritems():
      if v in index_to_cat_map:
        raise ValueError("cat_to_index_map must be one-to-one. " + str(v) + " appears twice.")
      index_to_cat_map[v] = k

    # Need to set the otypes variable for np.vectorize, otherwise it runs
    # it once to figure out the output type of map_back. This screws up
    # missing_vals.pop
    # otype = str if not len(cat_to_index_map) else type(cat_to_index_map.keys()[0])
    cats = np.array([index_to_cat_map[i] if i != -1 else index_to_cat_map[0] for i in target.flatten()])
    cats = cats.reshape(target.shape)

    mask = target == -1
    cats[mask] = missing_vals[mask]

    return {'cats': cats, 'cat_to_index_map': cat_to_index_map}
