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
        reconstructed_imgs = np.sort(img_stack.T, axis=2).T[::-1].astype(np.float64)

        # debug 展示
        if self.debug:
            for i, img in enumerate(reconstructed_imgs):
                io.imsave(f"distortion_{i}.tif", img)

        distortions, bgs = [], []

        dark_img_nums = int(reconstructed_imgs.shape[0] * 0.1)
        for img in reconstructed_imgs[-dark_img_nums:]:
            bgs.append([img, self.LCoV_evaluate(img)])

        bgs.sort(key=lambda x: x[1])

        # 亮度阈值为：不超过当前最暗的合成图的最亮的像素值亮度的0.05%
        intensity_threshold = np.max(bgs[0][0]) * (1.0 + 0.005)

        valid_bgs = []
        for img, _ in bgs:
            if img.max() < intensity_threshold:
                valid_bgs.append(img)
            else:
                break

        bg = sum(valid_bgs) / len(valid_bgs)

        # print("intentisy threshold:", intensity_threshold)
        print("valid background numbers:", len(valid_bgs))

        bright_img_nums = int(reconstructed_imgs.shape[0] * 0.85)
        for img in reconstructed_imgs[:bright_img_nums]:  # 取前85张图，找其中最平滑的
            img -= bg
            distortions.append([img, self.LCoV_evaluate(img)])

        # 平滑度阈值不超过最低的 0.5%
        distortions.sort(key=lambda x: x[1])
        LCoV_threshold = distortions[0][1] * (1.0 + 0.005)

        valid_flat = []
        for img, LCoV_score in distortions:
            if LCoV_score < LCoV_threshold:
                valid_flat.append(img)
            else:
                break

        flat = sum(valid_flat) / len(valid_flat)

        print("valid flat numbers:", len(valid_flat))
        # io.imsave("flat.tif", distortions[0][0].astype(np.uint16))
        # TODO:数学推导模拟
        flat = gaussian_filter(flat, sigma=10, mode="nearest")
        bg = gaussian_filter(bg, sigma=10, mode="nearest")

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
