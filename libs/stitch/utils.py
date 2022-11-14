import numpy as np


def reverse_with_flat_bg(src, flat, bg):
    print("---- bg max/min: {:.2f}, {:.2f}".format(bg.max(), bg.min()))
    print("---- flat max/min: {:.2f}, {:.2f}".format(flat.max(), flat.min()))
    flat = flat.astype(np.float32)
    src = src.astype(np.float32)
    bg = bg.astype(np.float32)

    src = 50 * ((src - bg) / (flat))
    src = src - src.min()
    src = src / (src.max() / 65535.0) * 0.8
    return src
