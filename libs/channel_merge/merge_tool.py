


#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets

import time,os,sys,qdarkstyle,cv2
import numpy as np
from skimage import io

from .balance import *
def read_image(img_path):
    img = io.imread(img_path)
    return img


class ROI_BOX():
    box = None
    state = 0
    # TODO: 模式2结束后，get_box返回的是None，虽然不会绘图但是也无法提取roi。改成不会绘图但仍旧能读取roi
    def update(self,x,y,type):
        #print(x,y,type)
        if self.state==0 or self.state == 3:   
            if type=='click':   # 初始点
                self.box = [x,y,x+1,y+1]
                self.state = 1
        elif self.state==1:     # 已经点了初始点，鼠标移动或松开（松开的话就固定，进入下一个状态）
            if type=='release':
                self.state = 2
            self.box[2] = x
            self.box[3] = y
        elif self.state==2:
            if type=='click':
                self.state = 0
                #self.box = [x,y,x+1,y+1]


    def get_box(self):
        if self.state!=0:
            return self.box
        else:
            return None


class MergeTool(QMainWindow):
    def __init__(self, project_path = r'F:\PMJ\python\data\肠子实验\A1-新鲜样本\拼接2D/', ui_path = "../../assets/channel_merge.ui"):
        super(MergeTool, self).__init__()
        uic.loadUi(ui_path, self)   # 以文件形式加载ui界面

        self.img_channel = {}
        self.img_roi = None
        self.roi_box = ROI_BOX()

        self.root = project_path
        self.channels = os.listdir(self.root)
        self.folders = {}
        for channel_name in self.channels:
            folders = os.listdir(os.path.join(self.root,channel_name))
            for folder in folders:
                if folder in self.folders:
                    self.folders[folder].append(channel_name)
                else:
                    self.folders[folder] = [channel_name]
        for folder in self.folders:
            self.folder.addItem(folder)
        # exit()
        self.load_channels()
        
        self.button_merge.clicked.connect(self.merge)
        self.channel_0.currentIndexChanged.connect(self.merge)
        self.channel_1.currentIndexChanged.connect(self.merge)
        self.channel_2.currentIndexChanged.connect(self.merge)
        self.folder.currentIndexChanged.connect(self.load_channels)
        # self.button_mean.clicked.connect(self.set_mean)

    def load_channels(self):
        folder = self.folder.currentText()  # 当前所选的文件
        
        for i in range(3):
            eval('self.channel_'+str(i)).clear()
        for channel_name in self.folders[folder]:
            if os.path.exists(os.path.join(self.root,channel_name ,folder, 'CellVideo/stitch.tif')):
                channle_img = io.imread(os.path.join(self.root,channel_name ,folder, 'CellVideo/stitch.tif'))/256.0
                self.img_channel[channel_name] = cv2.resize(channle_img, (640,640))
                for i in range(3):
                    eval('self.channel_'+str(i)).addItem(channel_name)
        for i in range(3):
            eval('self.channel_'+str(i)).addItem('None')

        # 显示图像
        self.merge()

    def plot(self):
        image = self.img_merge.copy()
        roi_box = self.roi_box.get_box()
        if roi_box:
            [x0,y0,x1,y1] = roi_box
            [x_0, y_0, x_1, y_1] = [min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)]
            if x_0!=x_1 and y_0!=y_1:
                self.img_roi = [x_0, y_0, x_1, y_1]
                cv2.rectangle(image, (x_0,y_0), (x_1,y_1), color=(0,0,255))
            else:
                self.img_roi = None
        else:
            self.img_roi = None
        img = QImage(image.data, 640, 640, QImage.Format_RGB888)
        self.curve.setPixmap(QPixmap.fromImage(img))
        
  

    def merge(self):
        
        #print(channle_2.min(), channle_2.max())
        if self.img_roi is not None:
            roi = self.img_roi
        else:
            roi = [0,0,-1,-1]
        [x0,y0,x1,y1] = roi
        channle_1 = self.img_channel['AF']
        img_merge = np.zeros((channle_1.shape[0], channle_1.shape[1], 3), dtype=np.uint8)
        del channle_1
        for i in range(3):
            channel_name = eval('self.channel_'+str(i)).currentText()
            if channel_name not in self.img_channel:
                continue
            image = self.img_channel[channel_name]
          
            info = get_normalization_info(image[y0:y1, x0:x1], 0.1, 0.1)
            image = normalization(image, info)*255


    
            
      


    
            img_merge[:,:,i] = image
        # img_merge[:,:,1] = channle_2
        # img_merge[:,:,2] = channle_3

        self.img_merge = img_merge

        #print(channle_1.shape, channle_2.shape)
        self.plot()
    

    # 鼠标点击事件
    def eventFilter(self,source, event):
        # 标注图鼠标响应
        if source == self.curve:
            if event.type()==QEvent.MouseButtonPress:
                [x, y] = [event.pos().x(), event.pos().y()]
                if event.button() == Qt.LeftButton:
                    self.roi_box.update(x,y,'click')
                    self.plot()

            if event.type()==QEvent.MouseButtonRelease:
                [x, y] = [event.pos().x(), event.pos().y()]
                if event.button() == Qt.LeftButton:
                    self.roi_box.update(x,y,'release')
                    self.plot()
                    


            if event.type()==QEvent.MouseMove:
                [x, y] = [event.pos().x(), event.pos().y()]
                self.roi_box.update(x,y,'move')
                self.plot()

        return QMainWindow.eventFilter(self, source, event)

  

   
if  __name__ == "__main__":                                 # main函数
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QFont("微软雅黑", 9))
    app.setWindowIcon(QIcon("icon.ico"))
    stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(stylesheet)
    gui = MergeTool()
    gui.show()
    app.installEventFilter(gui)
    sys.exit(app.exec_())