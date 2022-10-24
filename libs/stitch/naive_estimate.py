from scipy.ndimage import gaussian_filter
from skimage import io
import numpy as np


class NaiveEstimate:
    # windows size is recommended to be an odd number
    def __init__(self, debug=False, window_size=5) -> None:
        self.debug = debug
        self.window_size = window_size

    def __call__(self, img_stack):
        # pixel-wise sort, reverse order
        reconstructed_imgs = np.sort(img_stack.T, axis=2).T[::-1]

        # debug 展示
        if self.debug:
            for i, img in enumerate(reconstructed_imgs):
                io.imsave(f"distortion_{i}.tif", img)

        distortions, bgs = [], []

        for img in reconstructed_imgs[-10:]:
            bgs.append([img, self.LCoV_evaluate(img)])

        bgs.sort(key=lambda x: x[1])
        bg = bgs[0][0]

        for img in reconstructed_imgs[:10]:  # 只取前10张图，找其中最平滑的
            img -= bg
            distortions.append([img, self.LCoV_evaluate(img)])

        distortions.sort(key=lambda x: x[1])
        flat = distortions[0][0]

        io.imsave("flat.tif", distortions[0][0].astype(np.uint16))
        # TODO:数学推导模拟
        # flat, bg = gaussian_filter(flat, sigma=50, mode='nearest'), gaussian_filter(bg, sigma=50, mode='nearest')

        return flat, bg

    def LCoV_evaluate(self, distortion_img):
        cols = im2col(distortion_img, kernel_size=self.window_size, stride=1)
        LCoV_sum = np.sum(np.std(cols, axis=1) / np.mean(cols, axis=1))

        return LCoV_sum


def im2col(img, kernel_size, stride=1):
    pad = (kernel_size - 1) // 2  # 默认stride为1

    H, W = img.shape
    out_h = (H + 2 * pad - kernel_size) // stride + 1
    out_w = (W + 2 * pad - kernel_size) // stride + 1

    img = np.pad(
        img, [(pad, pad), (pad, pad)], "edge"
    )  # padding部分的mean、std是有影响的，是否需要单独拉出来算？
    col = np.zeros((kernel_size, kernel_size, out_h, out_w))

    for y in range(kernel_size):
        y_max = y + stride * out_h
        for x in range(kernel_size):
            x_max = x + stride * out_w
            col[y, x, :, :] = img[y:y_max:stride, x:x_max:stride]
    col = col.transpose(2, 3, 0, 1).reshape(out_h * out_w, -1)
    return col
