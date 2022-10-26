from skimage import io
from scipy.ndimage import gaussian_filter
import numpy as np


class FlatEstimate:
    def __init__(self, debug=False):
        self.debug = debug

    def __call__(self, img_stack, bias):
        # 高斯模糊并按亮度从大到小排序
        res = []
        for i in range(img_stack.shape[0]):
            patch = img_stack[i]
            result = gaussian_filter(patch, sigma=50)
            value = result.sum()
            res.append([result, value, i])
        res.sort(key=lambda x: x[1], reverse=True)

        # 取后5%的图，计算背景
        bg_res = res[-len(res) // 20 :] if len(res) >= 20 else res[-1:]
        if self.debug:
            for i in range(len(bg_res)):
                io.imsave("bg_" + str(i) + ".tif", bg_res[i][0].astype(np.uint16))
        bg = np.zeros((len(bg_res), 512, 512), dtype=np.float32)
        for i in range(len(bg_res)):
            bg[i] = bg_res[i][0]
        bg = np.mean(bg, axis=0).astype(np.float32)
        # io.imsave('bg.tif',bg)

        # res 是排好序的经过高斯模糊的图9p
        # 取亮度前25%的图，按方差从小到大排序
        res = res[: len(res) // 4]
        for i in range(len(res)):
            img_id = res[i][2]
            patch = img_stack[img_id]
            value = patch.std()
            res[i] = res[i] + [value]
        res.sort(key=lambda x: x[3], reverse=False)

        # 取亮度前25%中方差前50%小的图，计算光场
        res = res[: len(res) // 2]
        if self.debug:
            for i in range(len(res)):
                io.imsave("flat_" + str(i) + ".tif", res[i][0].astype(np.float32))
        flat = np.zeros((len(res), 512, 512), dtype=np.float32)
        for i in range(len(res)):
            flat[i] = res[i][0]
        flat = np.median(flat, axis=0).astype(np.float32)  # median? why not mean?
        # flat = io.imread(r'D:\stitch/flat.tif')
        # io.imsave('flat111.tif',flat)

        if bias != 0:
            bg = flat.min() - bias - 10

        flat -= bg

        return flat, bg
