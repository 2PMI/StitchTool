import pybasic
import numpy as np
from .naive_estimate import NaiveEstimate
from .utils import reverse_with_flat_bg


def Bagging(src, bias=0.8):
    naive_estimate = NaiveEstimate()
    flat_new, bg_new = naive_estimate(src, 1)
    flat_BaSiC, bg_BaSiC = pybasic.basic(src, darkfield=True)

    src_new = reverse_with_flat_bg(src, flat_new, bg_new)
    src_BaSiC = reverse_with_flat_bg(src, flat_BaSiC, bg_BaSiC)

    src = bias * src_new + (1 - bias) * src_BaSiC
    src = src.astype(np.uint16)
    return src
