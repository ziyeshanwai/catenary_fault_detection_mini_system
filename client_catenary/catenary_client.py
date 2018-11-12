# -*- coding: utf-8 -*-

"""
Author:  Liyou Wang
Date: 2018.11.1
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QLineEdit, QGridLayout, QMessageBox, QFileDialog) 
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import struct
import datetime
import grpc

# import the generated classes
import detec_image_pb2
import detec_image_pb2_grpc

   
"""
软件使用说明：
1、首先开启服务器端,然后选择连接服务器输入服务器的IP和端口地址
2、软件支持两种分析模式：a.单张图片分析 b.批量分析 选择打开图片并点击单张图片上传分析再点击产看分析结果报告即可看到该张图片的分析结果
或者点击批量分析按钮，进入想要批量分析图片的目录，然后点击查看分析结果报告即可看到全部图片的分析结果
"""
"""
MainWindow类是接触网小目标检测的客户端程序的主界面，主要有四个功能
1. 连接服务器的IP和端口（按钮1）
2. 打开接触网图片展示，同窗口尺度按比例缩放 并可以显示经过检测后的程序结果（qpixel）
3. 上传分析按钮(按钮二2)，弹出目录并显示分析的结果
4. 批量上传分析按钮，此时上传整个目录的接触网图片，并将结果保存到本地txt中
5. 查看分析结果
"""
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.init_MainWindow()
        self.ipadress = ''
        self.port = ''
        self.csw = None # 连接服务器窗口
        self.Image = None
        self.irw = None # 查看结果窗口
        self.analysisresult = ''
        self.channel = None
        self.stub = None
        self.respose = None
    
    def init_MainWindow(self):
        
        self.setGeometry(100, 100, 1500, 900)
        self.setWindowTitle('接触网极小零部件顶紧检测分析工具')    
        self.setWindowIcon(QIcon('./icon/icon.jpg'))

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.Layout = QVBoxLayout(self.centralwidget)

        # 设置顶部四个按钮
        self.topwidget = QWidget()
        self.Layout.addWidget(self.topwidget) #纵向布局

        self.buttonLayout = QHBoxLayout(self.topwidget) # 横向布局

        self.pushButton1 = QPushButton()
        self.pushButton1.setText("连接服务器")
        self.buttonLayout.addWidget(self.pushButton1)
        

        self.pushButton2 = QPushButton()
        self.pushButton2.setText("打开图片")
        self.buttonLayout.addWidget(self.pushButton2)

        self.pushButton5 = QPushButton()
        self.pushButton5.setText("单张图片上传分析")
        self.buttonLayout.addWidget(self.pushButton5)

        self.pushButton3 = QPushButton()
        self.pushButton3.setText("批量上传分析")
        self.buttonLayout.addWidget(self.pushButton3)

        self.pushButton4 = QPushButton()
        self.pushButton4.setText("查看分析结果报告")
        self.buttonLayout.addWidget(self.pushButton4)

        self.pushButton6 = QPushButton()
        self.pushButton6.setText("保存分析结果")
        self.buttonLayout.addWidget(self.pushButton6)

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.label.setAlignment(Qt.AlignCenter)
        # self.label.setFont(QFont("Roman times", 50, QFont.Bold))
        self.Layout.addWidget(self.label)

        self.pushButton1.clicked.connect(self.button1_on_clicked)
        self.pushButton2.clicked.connect(self.button2_on_clicked)
        self.pushButton3.clicked.connect(self.button3_on_clicked)
        self.pushButton4.clicked.connect(self.button4_on_clicked)
        self.pushButton5.clicked.connect(self.button5_on_clicked)
        self.pushButton6.clicked.connect(self.button6_on_clicked)

        self.statusBar().showMessage('就绪')

        self.show()
    
    def connet_server(self, ip, port):

        self.channel = grpc.insecure_channel('{}:{}'.format(ip,port))

        # create a stub (client)
        self.stub = detec_image_pb2_grpc.GetdetectionresultStub(self.channel)

    """
    实例化连接服务器界面
    """
    def button1_on_clicked(self):
        self.csw = Connect_server_Window(self)
        self.csw.show()
        self.statusBar().showMessage('连接服务器')
        return None

    """
    打开打开文件对话框
    """
    def button2_on_clicked(self):
        self.statusBar().showMessage('打开图片')
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0].endswith('.jpg') or fname[0].endswith('.png'):
            img = cv2.imread(fname[0])
            self.Image = img # 要上传的图片
            qimg = self.get_qimage(img)
            self.label.setPixmap(QPixmap(qimg))
            self.label.show()
            

    """
    批量上传分析，label 显示检测结果 并更新状态栏
    """
    def button3_on_clicked(self):
        tmpDir = QFileDialog.getExistingDirectory() 
        if tmpDir != '':
            self.statusBar().showMessage('批量分析图片...')
            image_list=os.listdir(tmpDir)
            for imgpath in image_list:
                self.Image = cv2.imread(imgpath)
                img_width = self.Image.shape[1]
                img_height = self.Image.shape[0]
                img_channel = self.Image.shape[2]
                img = self.Image.reshape(self.Image.size)
                img_bytes = struct.pack('B'*self.Image.size, *img)
                clientImage = detec_image_pb2.image(width=img_width, height=img_height, channel=img_channel, image=img_bytes)
                if self.stub != None:
                    self.response = self.stub.Getdetres(clientImage)
                    self.analysisresult += self.response

    """
    加载保存的txt单独出现一个界面显示分析结果
    """
    def button4_on_clicked(self):
        self.irw = inspect_result_Window()
        self.analysisresult = "图片{}顶紧缺失,理论{}个, 实测{}个\n tests \ntest".format('JC2134',3,2)
        self.irw.reviewEdit.setText(self.analysisresult)
        # self.irw.reviewEdit.setAlignment(Qt.AlignTop)
        self.irw.show()
        self.statusBar().showMessage('显示分析结果')

        return None


    """
    单张图片上传分析,调用服务器端的grpc服务
    """
    def button5_on_clicked(self):
        self.statusBar().showMessage('上传分析中...')
         # create a valid request message
        if type(self.Image) == type(np.array(1)):
            img_width = self.Image.shape[1]
            img_height = self.Image.shape[0]
            img_channel = self.Image.shape[2]
            img = self.Image.reshape(self.Image.size)
            img_bytes = struct.pack('B'*self.Image.size, *img)
            clientImage = detec_image_pb2.image(width=img_width, height=img_height, channel=img_channel, image=img_bytes)
        # make the call
        if self.stub != None:
            self.response = self.stub.Getdetres(clientImage)
            self.analysisresult += self.response
            print(self.response.strofresult)
            self.statusBar().showMessage('上传分析完成')


    """
    保存分析结果
    """
    def button6_on_clicked(self):
        save_path = os.path.join('./result',datetime.datetime.now().strftime('%Y-%m-%d')+'_result.txt')
        f = open(save_path,'w')
        f.write(self.analysisresult)
        f.close()
        self.statusBar().showMessage('保存分析结果完成')
        return None

    """
    将cv2读取的图片转化为qimage
    """
    def get_qimage(self, image: np.ndarray):

        height, width, colors = image.shape
        bytesPerLine = 3 * width
        image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # image = image.rgbSwapped()
        return image
    
def singleton(cls,*args, **kwarg):
    instances = {}

    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton

"""
连接服务器界面
"""
@singleton
class Connect_server_Window(QWidget):
    
    def __init__(self, mainwindow):
        super().__init__()
        self.ipadress = ''
        self.portadress = ''
        self.init_connect_server_window()
        self.mainwindow = mainwindow
    
    def init_connect_server_window(self):

        # self.setGeometry(100, 100, 1500, 900)
        self.setWindowTitle('连接服务器')    
        self.setWindowIcon(QIcon('./icon/icon.jpg'))

        IP = QLabel('IP')
        Port = QLabel('Port')

        self.ipEdit = QLineEdit()
        self.portEdit = QLineEdit()

        self.ok = QPushButton('确定')
        self.cancel = QPushButton('取消')
       
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(IP, 1, 0)
        grid.addWidget(self.ipEdit, 1, 1)

        grid.addWidget(Port, 2, 0)
        grid.addWidget(self.portEdit, 2, 1)

        grid.addWidget(self.ok, 3, 0)
        grid.addWidget(self.cancel, 3, 1)

        self.ok.clicked.connect(self.ok_on_clicked)
        self.cancel.clicked.connect(self.cancel_on_cliced)
        self.setLayout(grid)

        # self.show()
    def ok_on_clicked(self):
        self.ipadress = self.ipEdit.text()
        self.portadress = self.portEdit.text()
        if self.ipadress == '127.0.0.1':
             self.mainwindow.ipadress = self.ipadress
        else:
            QMessageBox.warning(self, "警告",'ip 地址输入错误', QMessageBox.Cancel)
        
        if self.portadress == '50051':
             self.mainwindow.port = self.portadress
        else:
            QMessageBox.warning(self, "警告",'port 地址输入错误', QMessageBox.Cancel)
        if self.ipadress == '127.0.0.1' and self.portadress == '50051':
            self.mainwindow.connet_server(self.ipadress, self.portadress)


        self.close()
    
    def cancel_on_cliced(self):
        self.close()

@singleton
class inspect_result_Window(QWidget):
    """
    查看分析结果的分析报告
    """
    def __init__(self):
        super().__init__()
        self.reviewEdit = None # 用来显示结果的
        self.initUI()
        

    def initUI(self):
        title = QLabel('标题')
        title.setAlignment(Qt.AlignTop)
        author = QLabel('作者')
        author.setAlignment(Qt.AlignTop)
        review = QLabel('分析报告')
        review.setAlignment(Qt.AlignTop)

        titleEdit = QLabel('接触网极小部件顶紧缺失检测报告')
        titleEdit.setAlignment(Qt.AlignTop)
        authorEdit = QLabel('LiyouWang')
        authorEdit.setAlignment(Qt.AlignTop)
        self.reviewEdit = QLabel()
        self.reviewEdit.setAlignment(Qt.AlignTop)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(self.reviewEdit, 3, 1, 5, 1)


        self.setLayout(grid) 
        self.setWindowTitle('查看结果')    

    


if __name__ == '__main__':
    # open a gRPC channel
    # channel = grpc.insecure_channel('localhost:50051')

    # create a stub (client)
    # stub = detec_image_pb2_grpc.GetdetectionresultStub(channel)

    # create a valid request message
    # clientImage = detec_image_pb2.image(size=23, image=b'1234')

    # make the call
    # response = stub.Getdetres(clientImage)

    # et voilà
    # print(response.strofresult)

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())