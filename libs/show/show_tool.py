#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets

import time, os, sys, qdarkstyle, cv2
import numpy as np
from skimage import io
from skimage.transform import resize


from .balance import *


def read_image(img_path):
    img = io.imread(img_path)
    return img


class ROI_BOX:
    box = None
    state = 0
    # TODO: 模式2结束后，get_box返回的是None，虽然不会绘图但是也无法提取roi。改成不会绘图但仍旧能读取roi
    def update(self, x, y, type):
        # print(x,y,type)
        if self.state == 0 or self.state == 3:
            if type == "click":  # 初始点
                self.box = [x, y, x + 1, y + 1]
                self.state = 1
        elif self.state == 1:  # 已经点了初始点，鼠标移动或松开（松开的话就固定，进入下一个状态）
            if type == "release":
                self.state = 2
            self.box[2] = x
            self.box[3] = y
        elif self.state == 2:
            if type == "click":
                self.state = 0
                # self.box = [x,y,x+1,y+1]

    def get_box(self):
        if self.state != 0:
            return self.box
        else:
            return None


class SingleShowWindow(QMainWindow):
    def __init__(self, img=None, ui_path="../../assets/single_show.ui"):
        super(SingleShowWindow, self).__init__()
        uic.loadUi(ui_path, self)  # 以文件形式加载ui界面

        self.img_roi = None
        self.roi_box = ROI_BOX()

        self.button_merge.clicked.connect(self.normalization)
        self.button_export.clicked.connect(self.export)
        # self.channel_0.currentIndexChanged.connect(self.plot)

        # self.button_mean.clicked.connect(self.set_mean)
        if img is not None:
            print(img.dtype)
            self.feed_img(img)
            self.normalization()

    def feed_img(self, img):
        if type(img) is str:
            img = io.imread(img)
        self.img_origin = img
        self.img_resize = img

        print(self.img_origin.shape, self.img_origin.dtype)
        self.w, self.h = self.img_resize.shape[1], self.img_resize.shape[0]
        if self.w > 1280:
            # self.img_resize = resize(self.img_resize,(self.h//8,self.w//8))
            self.img_resize = resize(self.img_resize, (1280, 1280))

    def plot(self):
        image = cv2.resize(self.img_normalization, (640, 640))
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        roi_box = self.roi_box.get_box()
        if roi_box:
            [x0, y0, x1, y1] = roi_box
            [x_0, y_0, x_1, y_1] = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
            if x_0 != x_1 and y_0 != y_1:
                self.img_roi = [x_0, y_0, x_1, y_1]
                cv2.rectangle(image, (x_0, y_0), (x_1, y_1), color=(0, 0, 255))
            else:
                self.img_roi = None
        else:
            self.img_roi = None
        img = QImage(image.data, 640, 640, QImage.Format_RGB888)
        self.curve.setPixmap(QPixmap.fromImage(img))

    def export(self):
        fname, _ = QFileDialog.getSaveFileName(self, "save file", "./", "ALL (*.tif)")
        if fname:
            # image = normalization(self.img_origin, self.info)*10000
            # image = image.astype(np.uint16)
            io.imsave(fname, self.img_normalization)

    def normalization(self):

        # print(channle_2.min(), channle_2.max())
        if self.img_roi is not None:
            roi = self.img_roi
        else:
            roi = [0, 0, -1, -1]
        [x0, y0, x1, y1] = roi

        image = self.img_resize

        self.info = get_normalization_info(image[y0:y1, x0:x1], 0.05, 0.05)
        image = normalization(image, self.info) * 255
        image = image.astype(np.uint8)

        # img_merge[:,:,1] = channle_2
        # img_merge[:,:,2] = channle_3

        self.img_normalization = image

        # print(channle_1.shape, channle_2.shape)
        self.plot()

    # 鼠标点击事件
    def eventFilter(self, source, event):
        # 标注图鼠标响应
        if source == self.curve:
            if event.type() == QEvent.MouseButtonPress:
                [x, y] = [event.pos().x(), event.pos().y()]
                if event.button() == Qt.LeftButton:
                    self.roi_box.update(x, y, "click")
                    self.plot()

            if event.type() == QEvent.MouseButtonRelease:
                [x, y] = [event.pos().x(), event.pos().y()]
                if event.button() == Qt.LeftButton:
                    self.roi_box.update(x, y, "release")
                    self.plot()

            if event.type() == QEvent.MouseMove:
                [x, y] = [event.pos().x(), event.pos().y()]
                self.roi_box.update(x, y, "move")
                self.plot()

        return QMainWindow.eventFilter(self, source, event)


if __name__ == "__main__":  # main函数
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QFont("微软雅黑", 9))
    app.setWindowIcon(QIcon("icon.ico"))
    stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(stylesheet)
    gui = SingleShowWindow("../../stitch.tif")
    gui.show()
    app.installEventFilter(gui)
    sys.exit(app.exec_())
