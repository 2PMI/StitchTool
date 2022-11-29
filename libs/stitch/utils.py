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
    out = []
    for img in src:
        imgs_fft = np.fft.fft2(img)
        imgs_fft = np.fft.fftshift(imgs_fft)
        mask = adaptive_mask(imgs_fft)
        imgs_fft = imgs_fft * mask
        imgs_new = np.fft.ifft2(imgs_fft)
        imgs_new = np.abs(imgs_new)
        out.append(imgs_new)

    return np.array(out)


# @jit(nopython=True)
def cut_light(src, min_num=0.5, max_num=99.5):
    out = []
    for img in src:
        max_threshold = np.percentile(img, max_num)
        min_threshold = np.percentile(img, min_num)
        img = np.clip(img, min_threshold, max_threshold)
        out.append(img)

    return np.array(out)


# 注意adaptive mask的输入是频域值
@jit(nopython=True)
def adaptive_mask(src):
    mask = np.ones(src.shape, dtype=np.uint8)
    window_width = 10
    window_length = 170

    intensity = []
    intensity_sum = 0
    for i in range(0, src.shape[0] + 1 - window_width, window_width):
        box = src[i : i + window_width, 0:window_length]
        intensity.append([i, np.abs(box).sum()])
        intensity_sum += np.abs(box).sum()

    intensity.sort(key=lambda x: x[1], reverse=True)
    threshold = 1.5 * intensity_sum / len(intensity)
    # for index, value in intensity:
    #     print("index:", index, "value:", value)

    for index, value in intensity[:4]:
        # print("value:", value, "threshold:", threshold, "index:", index)
        if value > threshold:
            mask[index : index + window_width, :window_length] = 0
            mask[index : index + window_width, -window_length:] = 0

    return mask
