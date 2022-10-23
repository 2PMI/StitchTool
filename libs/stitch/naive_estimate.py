from email.errors import StartBoundaryNotFoundDefect
from skimage import io
import numpy as np


class NaiveEstimate:
    # windows size is recommended to be an odd number
    def __init__(self, debug=False, window_size=5) -> None:
        self.debug = debug
        self.window_radius = window_size // 2

    def __call__(self, img_stack):
        # pixel-wise sort
        distortions = np.zeros(img_stack.shape, dtype=np.uint16)
        for i in range(img_stack.shape[1]):
            for j in range(img_stack.shape[2]):
                pixels = img_stack[:, i, j]
                pixels = np.sort(pixels)[::-1]
                distortions[:, i, j] = pixels

        # debug 展示
        if self.debug:
            for i, distortion_img in enumerate(distortions):
                io.imsave(f"distortion_{i}.tif", distortion_img)

        res = [(img, self.LCoV_evaluate(img)) for img in distortions]
        res.sort(key=lambda x: x[1])

        flat, bg = res[0][0], 0
        return flat, bg

    def LCoV_evaluate(distortion_img: np.ndarray, radius: int):
        LCoV_sum = 0
        for i in range(distortion_img.shape[0]):
            for j in range(distortion_img.shape[1]):
                startX = max(0, i - radius)
                endX = min(distortion_img.shape[0], i + radius + 1)
                startY = max(0, j - radius)
                endY = min(distortion_img.shape[1], j + radius + 1)
                sub_img = distortion_img[startX:endX, startY:endY]
                LCoV_sum += sub_img.std() / sub_img.mean()

        return LCoV_sum
