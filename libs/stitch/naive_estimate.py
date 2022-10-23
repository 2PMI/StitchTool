from scipy.ndimage import gaussian_filter
from skimage import io
import numpy as np


class NaiveEstimate:
    # windows size is recommended to be an odd number
    def __init__(self, debug=False, window_size=5) -> None:
        self.debug = debug
        self.window_radius = window_size // 2

    def __call__(self, img_stack):
        # pixel-wise sort, reverse order
        rearanged_imgs = np.sort(img_stack.T, axis=2).T[::-1]

        # debug 展示
        if self.debug:
            for i, img in enumerate(rearanged_imgs):
                io.imsave(f"distortion_{i}.tif", img)

        distortions, bgs = [], []
        for img in rearanged_imgs[:10]:  # 只取前10张图，找其中最平滑的
            distortions.append([img, self.LCoV_evaluate(img)])

        for img in rearanged_imgs[-10:]:
            bgs.append([img, self.LCoV_evaluate(img)])

        distortions.sort(key=lambda x: x[1])
        bgs.sort(key=lambda x: x[1])

        io.imsave("flat.tif", distortions[0][0].astype(np.uint16))
        flat, bg = gaussian_filter(distortions[0][0], sigma=10), gaussian_filter(
            bgs[0][0], sigma=10
        )
        return flat, bg

    def LCoV_evaluate(self, distortion_img):
        LCoV_sum = 0
        radius = self.window_radius
        # print(distortion_img)
        for i in range(distortion_img.shape[0]):
            for j in range(distortion_img.shape[1]):
                startX = max(0, i - radius)
                endX = min(distortion_img.shape[0], i + radius + 1)
                startY = max(0, j - radius)
                endY = min(distortion_img.shape[1], j + radius + 1)
                sub_img = distortion_img[startX:endX, startY:endY]
                LCoV_sum += sub_img.std() / sub_img.mean()

        return LCoV_sum
