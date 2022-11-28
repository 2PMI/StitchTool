import numpy as np
import numba
from numba import jit


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


def grid_noise_filter(src):
    mask = np.ones(src[0].shape, dtype=np.uint8)
    mask[:, 0:80] = 0
    mask[:, -80:] = 0

    imgs_fft = np.fft.fft2(src)
    imgs_fft = np.fft.fftshift(imgs_fft, axes=(-2, -1))
    imgs_fft = imgs_fft * mask
    imgs_new = np.fft.ifft2(imgs_fft, axes=(-2, -1))
    imgs_new = np.abs(imgs_new)

    return imgs_new


# @jit(nopython=True)
def cut_light(src, min_num=0.5, max_num=99.5):
    out = []
    for img in src:
        max_threshold = np.percentile(img, max_num)
        min_threshold = np.percentile(img, min_num)
        img = np.clip(img, min_threshold, max_threshold)
        out.append(img)

    return np.array(out)
