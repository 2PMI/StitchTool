import cv2
from scipy.signal import wiener as wienerBlur
import numpy as np

def wiener(img,size=3):
    # 维纳滤波
    img = img.astype('float64')
    result = wienerBlur(img, [size, size])
    print(result.max())
    #result = np.uint8(result / result.max() * 255)
    return result

def meanBlur(img, size=5):
    result = cv2.blur(img,(size,size))
    return result

def medianBlur(img, size=5):
    if size%2==0:
        size += 1
    result = cv2.medianBlur(img,size)
    return result

def gaussianBlur(img, size=5):
    print(size)
    if size%2==0:
        size += 1
    result = cv2.GaussianBlur(img,(size,size),0)
    return result
