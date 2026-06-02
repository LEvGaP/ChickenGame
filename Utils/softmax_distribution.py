import numpy as np


def softmax(x):
    """Compute softmax values for a set of scores."""
    e_x = np.exp(x)
    return e_x / e_x.sum()