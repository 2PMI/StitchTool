import numpy as np


def get_normalization_info(img_in, max_per=None, min_per=None):
    '''
    :param img_in: Input image
    :param max_per: [0.0 ~ 1.0], percentage of maxinum pixel value
    :param min_per: [0.0 ~ 1.0], percentage of mininum pixel value
    :return:
    '''
    img_in = img_in.astype(np.float32)

    # Max and min
    img_in2list = list(img_in.flatten())
    img_in2list.sort()
    img_in2list_len = len(img_in2list) - 1

    max_value = img_in2list[int(img_in2list_len * (1.0 - max_per))] if max_per is not None else img_in2list[-1]
    min_value = img_in2list[int(img_in2list_len * min_per)] if min_per is not None else img_in2list[0]
    info = {'max':max_value, 'min':min_value}
    return info

def normalization(img_in, info):
    max_value, min_value = info['max'], info['min']


    if max_value - min_value:
        img_out = (img_in - min_value) / (max_value - min_value)
    else:
        img_out = img_in - min_value
    img_out = img_out.clip(0.0, 1.0)

    return img_out