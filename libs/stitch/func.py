# coding: utf-8
from os import path

import numpy as np
from scipy import ndimage

from skimage import io

from pystackreg import StackReg

import time
from .flat_estimate import FlatEstimate

class StitchTool:
    def __init__(self,flat=None,bg=None) -> None:
        self.flat = flat
        self.bg = bg
        self.sr = StackReg(StackReg.RIGID_BODY)
        self.flat_estimate = FlatEstimate()

    def set_flat(self,flat_info):
        self.flat_info = flat_info



    def correct(self,src,bias):
        if 'estimate' in self.flat_info:
            flat, bg = self.flat_estimate(src)
        elif self.flat_info['flat'] is None:
            return src
        else:
            flat = io.imread(self.flat_info['flat']) 
            bg = io.imread(self.flat_info['bg'])
        
        if bias!=0:
            bg = flat.min() -10 - bias   
        print('---- bg max/min:',bg.max(),bg.min())
        print('---- flat max/min:',flat.max(),flat.min())

        flat = flat.astype(np.float32)
        src = src.astype(np.float32)

        # bg = 7000
        for i in range(src.shape[0]):
            raw = src[i,:,:]
            raw = 50*((raw-bg)/(flat-bg))
            src[i,:,:] = raw
           

        src = src-src.min()
        src = src/(src.max()/65535.0)*0.8
        src = src.astype(np.uint16)
        return src
    
    def average_img(self,images,average_num,is_registration=False):
        img_avg = np.zeros((images.shape[0]//average_num,images.shape[1],images.shape[2]),dtype=np.uint16)
        for i in range(images.shape[0]//average_num):
            img_stack = images[i*average_num:(i+1)*average_num]
            if is_registration:
                out_mean_af = self.sr.register_stack(img_stack, axis=0, reference = 'previous' ) #输出的是形变矩阵
                img_stack = self.sr.transform_stack(img_stack)
            img_avg[i] = np.mean(img_stack,axis=0)
        return img_avg

    def stitch(self,img_path,save_path,grid_shape, average_num=1, bias=-1500, overlay=0.1, fill=True, is_registration=False):
        if is_registration:
            print('开启配准,耗时很长请等待...')
        [row_num,col_num] = grid_shape
        images = io.imread(img_path).astype(np.float32)
        if images.shape[0] != grid_shape[0]*grid_shape[1]*average_num:
            new_img = np.zeros((grid_shape[0]*grid_shape[1]*average_num, images.shape[1], images.shape[2]), dtype=np.uint16)
            if fill:
                print('图片缺帧,已在尾部补帧')
                new_img[:images.shape[0]] = images
            else:
                print('图片缺帧,已在头部补帧')
                new_img[-images.shape[0]:] = images

            images = new_img
        images = self.average_img(images,average_num,is_registration)
        images = self.correct(images, bias)


    
        images = images.astype(np.uint16)
        rows,cols = [],[]
        for row in range(row_num):
            rows += [row]*col_num
            if row%2==0:
                cols += list(range(col_num))
            else:
                cols += list(range(col_num-1,-1,-1))
    

        zzz = images
        output = np.zeros((zzz.shape[1]*row_num,zzz.shape[2]*col_num),dtype=images.dtype)

        h,w = images.shape[1], images.shape[2]
        hide = int(overlay*images.shape[1])
        # print('重叠量：',overlay)
        step = zzz.shape[1] - hide

        overlay_map = np.zeros_like(output,dtype=np.uint8)

        for i in range(zzz.shape[0]):
            row,col = rows[i], cols[i]
            x0,x1 = step*col, step*col+w
            y0,y1 = step*row, step*row+h

            image = zzz[i,:,:]
            patch = output[y0:y1,x0:x1]
            overlay_patch = overlay_map[y0:y1,x0:x1]

            if overlay_patch.sum() != 0:
                weight_overlay = ndimage.morphology.distance_transform_edt(overlay_patch).astype(np.float64)
                max_value = np.partition(weight_overlay.flatten(), -2)[-2]
                weight_overlay /= max_value
                weight_overlay = np.clip(weight_overlay,0,1)
            else:
                weight_overlay = np.zeros_like(patch,dtype=np.float64)
            
            weight_no_overlay =np.ones_like(weight_overlay,dtype=np.float64)-weight_overlay
            patch = patch*weight_overlay + image*weight_no_overlay
            
        
            overlay_map[y0:y1,x0:x1] = 1
            output[y0:y1,x0:x1] = patch     # patch是float型而output是整型。请确保灰度级够大（不够大就乘个系数），否则这零点几的精度损失会带来明显的视觉差异
        print('>>>>  finish',save_path)
        io.imsave(save_path,output)
        return output

if __name__=='__main__':
    aaa = np.zeros((10,512,512))
    aaa = reg_img_stack(aaa)
    print(aaa.shape)
    # stitch_tool = StitchTool()
    # stitch_tool.stitch(img_path='CellVideo.tif', save_path='CellVideo_stitch.tif', grid_shape=[20,22])
