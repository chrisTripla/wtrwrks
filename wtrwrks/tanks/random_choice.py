"""RandomChoice tank definition."""
import wtrwrks.waterworks.waterwork_part as wp
import wtrwrks.waterworks.tank as ta
import numpy as np
import wtrwrks.tanks.utils as ut


class RandomChoice(ta.Tank):
  """Randomly select values from a list to fill some array.

  Attributes
  ----------
  slot_keys: list of strs
    The names off all the tank's slots, i.e. inputs in the pour (forward) direction, or outputs in the pump (backward) direction
  tubes: list of strs
    The names off all the tank's tubes, i.e. outputs in the pour (forward) direction,

  """

  slot_keys = ['a', 'shape']
  tube_keys = ['target', 'a']

  def _pour(self, a, shape, p):
    """

    Parameters
    ----------
    a: 1D np.ndarray or int
      The allowed values for to randomly select from
    shape: list of ints
      The shape of the outputted array of random values.
    p: 1D np.ndarray of numbers 0 <= 0 <=1 that sum to one or None
      The probability with which to select each value from 'a'

    Returns
    -------
    dict(
      target: np.ndarray
        The randomly selected values
      a: 1D np.ndarray or int
        The allowed values for to randomly select from
      p: 1D np.ndarray of numbers 0 <= 0 <=1 that sum to one or None
        The probability with which to select each value from 'a'
    )

    """
    target = np.random_choice(a, shape=shape, p=p)

    return {'target': target, 'a': ut.maybe_coppy(a), 'p': ut.maybe_coppy(p)}

  def _pump(self, target, a, p):
    """Execute the random_choice tank (operation) in the pump (backward) direction.

    Parameters
    ----------
    target: np.ndarray
      The randomly selected values
    a: 1D np.ndarray or int
      The allowed values for to randomly select from
    p: 1D np.ndarray of numbers 0 <= 0 <=1 that sum to one or None
      The probability with which to select each value from 'a'

    Returns
    -------
    dict(
      a: 1D np.ndarray or int
        The allowed values for to randomly select from
      shape: list of ints
        The shape of the outputted array of random values.
      p: 1D np.ndarray of numbers 0 <= 0 <=1 that sum to one or None
        The probability with which to select each value from 'a'
    )

    """
    shape = target.shape
    return {'a': a, 'shape': shape, 'p': p}
