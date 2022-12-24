#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, os, sys, cv2, qdarkstyle

from libs.stitch import StitchTool
from libs.show.show_tool import SingleShowWindow

sys.path.append("libs/Stitch")
import numpy as np
from PIL import Image

# import QMutex
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets

from libs import *


Denoise_func = {"gaussian": gaussianBlur, "mean": meanBlur, "median": medianBlur}


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi("./assets/main.ui", self)  # 以文件形式加载ui界面

        self.img_list = []
        # self.openImg.triggered.connect(self.open_image)
        self.button_openimg_stitch.clicked.connect(self.open_image_stitch)

        self.button_stitch.clicked.connect(self.stitch)
        self.button_stitch_batch.clicked.connect(self.stitch_batch)

        self.denoise_func = "gaussian"
        self.Denoise_size = {
            "gaussian": self.slider_gaussian,
            "mean": self.slider_mean,
            "median": self.slider_median,
        }
        self.overlay = int(self.line_overlay.text())

        self.button_merge.clicked.connect(self.open_merge_gui)

        self.button_gaussian.clicked.connect(self.set_gaussion)
        self.button_mean.clicked.connect(self.set_mean)
        self.button_median.clicked.connect(self.set_median)
        self.frame_slider.valueChanged.connect(self.frame_change)
        self.slider_gaussian.valueChanged.connect(self.frame_change)
        self.slider_mean.valueChanged.connect(self.frame_change)
        self.slider_median.valueChanged.connect(self.frame_change)

        self.stitch_tool = StitchTool(
            flat="assets/flat/400/flat.tif", bg="assets/flat/400/bg.tif"
        )
        self.load_flat()

    def open_merge_gui(self):
        openfile = QFileDialog.getExistingDirectory(None, "选择文件夹", ".")
        if openfile:
            self.merge_gui = MergeTool(
                project_path=openfile, ui_path="assets/channel_merge.ui"
            )
            self.merge_gui.show()
            app.installEventFilter(self.merge_gui)

    def open_image(self):
        openfile = QFileDialog.getOpenFileNames(self, "选择文件", "", "image files(*.tif)")[
            0
        ]
        if openfile:
            ret, images = cv2.imreadmulti(openfile[0], [], cv2.IMREAD_ANYCOLOR)
            if ret:
                self.img_list = images
                self.plot(images[0])
                self.frame_slider.setMaximum(len(images) - 1)
                self.frame_slider.setValue(0)

    def open_image_stitch(self):
        default_text = self.line_imgpath_stitch.text()
        if default_text != "":
            openfile = QFileDialog.getExistingDirectory(
                None, "选择文件夹", default_text + "/.."
            )
        else:
            openfile = QFileDialog.getExistingDirectory(None, "选择文件夹", "../")

        if openfile:
            self.line_imgpath_stitch.setText(openfile)

    def stitch(self, no_show=False):
        # try:
        base_dir = self.line_imgpath_stitch.text()
        print(base_dir)
        src_path = os.path.join(base_dir, "CellVideo/CellVideo 0.tif")
        if not os.path.exists(src_path):
            print("--- 【ERROR】 没有找到tif图像！")
            return
        img_avg_num = int(self.line_avg_num.text())
        grid_shape = [int(self.line_grid1.text()), int(self.line_grid2.text())]
        bias = float(self.line_correct_bias.text())

        # 读取光场图像
        flat_info = self.flat_folder[self.combo_flat_name.currentText()]
        if flat_info == "flat":
            flat_info = "None"
        self.stitch_tool.set_flat(flat_info)
        print("使用光场:", flat_info)
        save_path = os.path.join(
            base_dir, "CellVideo/CellVideo 0_{}_stitch.tif".format(list(flat_info)[0])
        )

        # try:
        img_out = self.stitch_tool.stitch(
            src_path,
            save_path,
            grid_shape,
            average_num=img_avg_num,
            overlay=float(self.line_overlay.text()) / 100.0,
            bias=bias,
            is_registration=self.reg_box.isChecked(),
        )
        if not no_show:
            self.single_show_window = SingleShowWindow(
                img=img_out, ui_path="./assets/single_show.ui"
            )
            self.single_show_window.show()
            app.installEventFilter(self.single_show_window)
        # except:
        #     msg_box = QMessageBox(QMessageBox.Warning, 'Warning', '发生未知错误，请检查参数是否正确！')
        #     msg_box.exec_()
        #     return

    def load_txt(self, txt):
        info = {}
        with open(txt, "r") as f:
            lines = f.readlines()
            for line in lines:
                [name, value] = line.split()
                info[name] = value
        return info

    def stitch_batch(self):
        base_dir = self.line_imgpath_stitch.text()
        target_dirs = os.listdir(base_dir)
        print("【BATCH】", base_dir)
        for target_dir in target_dirs:
            target_dir = os.path.join(base_dir, target_dir)
            if not os.path.isdir(target_dir):
                continue
            src_path = os.path.join(target_dir, "CellVideo/CellVideo 0.tif")

            if not os.path.exists(src_path):
                print("--- 【ERROR】:", src_path, " NOT FOUND!")
                continue
            print(">>>> Processing ", src_path)
            try:
                info = self.load_txt(os.path.join(target_dir, "Information.txt"))
                img_avg_num = int(info["Frames_per_slice"])
                grid_shape = [
                    int(info["Vertical_Pages"]),
                    int(info["Horizontal_Pages"]),
                ]
                bias = float(self.line_correct_bias.text())
            except:
                print("No enough info, skip...")
                continue

            # 读取光场图像
            flat_info = self.flat_folder[self.combo_flat_name.currentText()]
            self.stitch_tool.set_flat(flat_info)
            save_path = os.path.join(
                target_dir,
                "CellVideo/CellVideo 0_{}_stitch.tif".format(list(flat_info)[0]),
            )
            try:
                self.stitch_tool.stitch(
                    src_path,
                    save_path,
                    grid_shape,
                    average_num=img_avg_num,
                    overlay=float(self.line_overlay.text()) / 100.0,
                    bias=bias,
                    is_registration=self.reg_box.isChecked(),
                )
            except:
                msg_box = QMessageBox(
                    QMessageBox.Warning, "Warning", "发生未知错误，请检查参数是否正确！"
                )
                msg_box.exec_()
                return
        QMessageBox.information(self, "Result", src_path + "\n拼接批处理完毕！")

    def frame_change(self):
        if self.img_list:
            id = self.frame_slider.value()
            self.plot(self.img_list[id])

    def load_flat(self):
        root = "assets/flat"
        folder_names = os.listdir(root)
        self.flat_folder = {
            "None": {"flat": None, "bg": None},
            "Estimate": {"estimate"},
            "NaiveEstimate": {"NaiveEstimate"},
            "BaSic": {"BaSic"},
            "Bagging": {"Bagging"},
        }
        for folder_name in folder_names:
            folder_path = os.path.join(root, folder_name)
            flat_path = os.path.join(folder_path, "flat.tif")
            bg_path = os.path.join(folder_path, "bg.tif")
            if os.path.isfile(flat_path) and os.path.exists(bg_path):
                self.flat_folder[folder_name] = {"flat": flat_path, "bg": bg_path}
                self.combo_flat_name.addItem(folder_name)

        self.combo_flat_name.addItem("NaiveEstimate")
        self.combo_flat_name.addItem("BaSic")
        self.combo_flat_name.addItem("Bagging")

    def set_gaussion(self):
        self.denoise_func = "gaussian"
        self.frame_change()

    def set_mean(self):
        self.denoise_func = "mean"
        self.frame_change()

    def set_median(self):
        self.denoise_func = "median"
        self.frame_change()

    def plot(self, img):
        """
        将图像显示在QLabel上
        """

        img = cv2.resize(img.astype(np.uint8), (512, 512))
        img_denoise = Denoise_func[self.denoise_func](
            img, self.Denoise_size[self.denoise_func].value()
        )

        if self.tabWidget.currentIndex() == 0:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            self.curve_origin.setPixmap(QPixmap.fromImage(img))

            img_denoise = cv2.cvtColor(img_denoise, cv2.COLOR_RGB2BGR)
            img_denoise = QImage(
                img_denoise.data,
                img_denoise.shape[1],
                img_denoise.shape[0],
                QImage.Format_RGB888,
            )
            self.curve_denoise.setPixmap(QPixmap.fromImage(img_denoise))

        elif self.tabWidget.currentIndex() == 1:
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            img = QImage(img.data, 860, 640, QImage.Format_RGB888)
            self.label_stitch.setPixmap(QPixmap.fromImage(img))

    # 单击“检测图片按钮”的槽函数
    def detect_img(self):
        if self.cap_thread.is_running():
            self.cap_thread.stop()
        file = QFileDialog.getOpenFileName(self, "选择图片", "", "images(*.png; *.jpg);;*")[
            0
        ]
        if not file:
            return
        img = cv2.imread(file)
        # 检测图片
        r_image = self.model.detect_image(Image.fromarray(np.uint8(img)))
        img = np.array(r_image)
        # 显示图片
        self.plot(img)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setFont(QFont("微软雅黑", 9))
    app.setWindowIcon(QIcon("icon.ico"))
    app.setStyleSheet(stylesheet)
    w = GUI()
    w.show()
    app.installEventFilter(w)
    sys.exit(app.exec_())
