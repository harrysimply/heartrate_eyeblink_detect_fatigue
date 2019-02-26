#coding = utf-8
#https://www.cnblogs.com/jackadam/p/8302442.html

from intervene import Ui_Form
import sys
import cv2
import dlib
import numpy as np
import bluepy
import binascii
from eye_blink_detect import eye_aspect_ratio
#from wrist_bluetooth import MyDelegate
from tired import tired_warning,tired_playmusic,tired_finalcall,new_warning
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5.QtCore import QTimer,QThread,pyqtSignal
from PyQt5.QtGui import QImage,QPixmap
ble_conn = None
HRs=[]

class MyDelegate(bluepy.btle.DefaultDelegate):

    def __init__(self, conn):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.conn = conn

    def handleNotification(self, cHandle, data):
        data = binascii.b2a_hex(data)
        HR=int(data[-2:-1], 16)*16+int(data[-1:], 16)
        HRs.append(HR)
        #print("Notification:", str(cHandle), " data ", data)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            pass
        elif isNewData:
            print("\\nDiscovery:", "MAC:", dev.addr, " Rssi ", str(dev.rssi))

def ble_connect(devAddr):

    global ble_conn
    if not devAddr is None and ble_conn is None:
        ble_conn = bluepy.btle.Peripheral(devAddr, bluepy.btle.ADDR_TYPE_RANDOM)
        ble_conn.setDelegate(MyDelegate(ble_conn))
        print("connected")


def ble_disconnect():

    global ble_conn
    ble_conn = None
    print("disconnected")

class MyThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def setup(self, thread_no):
        self.thread_no = thread_no

    def run(self):
        self.trigger.emit(self.thread_no)
class BlueThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        # win=mainWindow()
        ble_mac = "FF:C1:28:73:E3:5C"

        print("搜索心率传感器>>>>>>>")
        # win.text_area.clear()
        ble_connect(ble_mac)
        print("传感器已连接！")
        # win.thread_txt.trigger.emit("传感器已连接！,正在传输心率信号……")
        snd_content_str = b'\x01\x00'
        handle = 0x0014
        ble_conn.writeCharacteristic(handle, snd_content_str, withResponse=True)
        print(">>>>>>>>>>>>")
        while True:
            if ble_conn.waitForNotifications(1.0):
                continue
            print(HRs[-1:])
            print("Waiting...")
        ble_disconnect()

class VoiceThread(QThread):
    def __init__(self):
        super().__init__()
    def run(self):
        tired_warning()

class CallThread(QThread):
    def __init__(self):
        super().__init__()
    def run(self):
        tired_finalcall()

class MusicThread(QThread):
    def __init__(self):
        super().__init__()
    def run(self):
        tired_playmusic()




class mainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui=Ui_Form()
        self.ui.setupUi(self)

        self.threads = MyThread(self)
        self.timer_1 = QTimer()
        self.timer_1.setInterval(1)

        self.timer_2 = QTimer()
        self.timer_2.setInterval(1)
        self.timer_2.timeout.connect(self.fatigue_warning)

        self.init_lib()

        btn_1 = self.ui.pushButton
        btn_1.clicked.connect(self.open_camera)
        btn_2 = self.ui.pushButton_3
        btn_2.clicked.connect(self.fatigue_intervene)
        btn_3 = self.ui.pushButton_4
        btn_3.clicked.connect(self.connect_bluetooth)


        self.warning_count=0





    def init_lib(self):
        self.detector = dlib.get_frontal_face_detector()  # 检测人脸
        predictor_path = "./shape_predictor_68_face_landmarks.dat"
        self.predictor = dlib.shape_predictor(predictor_path)  # 68个特征点提取器
        # 初始化dlib中的人脸特征点排号
        self.RIGHT_EYE_START = 37 - 1
        self.RIGHT_EYE_END = 42 - 1
        self.LEFT_EYE_START = 43 - 1
        self.LEFT_EYE_END = 48 - 1
        # 初始化瞳孔定位的一些初值
        self.l_points = []
        self.l_RECORD = []
        self.r_points = []
        self.r_RECORD = []
        self.left_eye_crop = []
        self.right_eye_crop = []

        #初始化眨眼的阈值
        self.EAR = []
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 4
        self.COUNT = 0
        self.fatigue_count=0

        #初始化心率的阈值
        self.hr=60

        self.thread=BlueThread()
        self.thread_voice= VoiceThread()
        self.thread_call = CallThread()

        #初始化文本框的值

        self.text_area=self.ui.textBrowser
        self.thread_txt=MyThread()
        self.thread_txt.trigger.connect(self.update_text)
        self.thread_no = 0

        # #初始化lcd框的值
        # self.hr_lcd = self.ui.lcdNumber_2
        # self.thread_lcd = MyThread()
        # self.thread_lcd.trigger.connect(self.update_text)
        # self.thread_no = 0

    def update_text(self,message):
        self.text_area.append(message)



    def connect_bluetooth(self):
        self.text_area.clear()
        self.thread_txt.trigger.emit("搜索蓝牙中……")
        import time
        time.sleep(2)
        self.thread.start()
        if len(HRs)!=[]:
            self.text_area.clear()

            time.sleep(2)
            self.thread_txt.trigger.emit("心率传感器已连接，数据传输中……")



    def open_camera(self):
        self.capture=cv2.VideoCapture(0)
        self.timer_1.timeout.connect(self.capture_picture)
        self.timer_1.start()

    def capture_picture(self):

        ret, img = self.capture.read()
        if ret:
            img = cv2.flip(img, 1, dst=None)#翻转图像，产生镜面效果
            self.height, self.width, bytesPerComponent = img.shape
            bytesPerLine = 3 * self.width
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转成灰度图像
            dets = self.detector(gray, 0)
            for i, d in enumerate(dets):
                shape = self.predictor(img, d)
                landmarks = np.matrix([[p.x, p.y] for p in shape.parts()])
                left_eye = landmarks[self.LEFT_EYE_START:self.LEFT_EYE_END + 1]
                right_eye = landmarks[self.RIGHT_EYE_START:self.LEFT_EYE_END + 1]

                l_ear = eye_aspect_ratio(left_eye)
                r_ear = eye_aspect_ratio(right_eye)
                ear = (l_ear + r_ear) / 2.0
                #print("当前的眼睛纵横比是{}5".format(ear))
                self.EAR.append(ear)






                if ear < self.EYE_AR_THRESH:
                    self.COUNT += 1
                    self.ui.lcdNumber.display(str(self.COUNT))
                    cv2.putText(img, "BLINK", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    if self.COUNT > self.EYE_AR_CONSEC_FRAMES:
                        self.fatigue_count+=2
                        self.ui.progressBar.setValue(self.fatigue_count)
                        #print("感到疲劳")
                    else:
                        self.fatigue_count-=2
                        self.ui.progressBar.setValue(self.fatigue_count)



                else:
                    self.COUNT = 0


                    pass

                if len(HRs)!=0:
                    self.ui.lcdNumber_2.display(str(HRs[-1]))
                    if HRs[-1]>100 or HRs[-1]<50:
                        self.fatigue_count += 2
                        self.ui.progressBar.setValue(self.fatigue_count)


                if self.fatigue_count > 100:
                    self.fatigue_count = 50
                    self.thread_voice.start()

                    self.warning_count +=1
                if self.warning_count >=3:
                    import time
                    time.sleep(10)
                    self.warning_count=0
                    self.thread_call.start()



                # for idx, point in enumerate(landmarks):
                #     pos = (point[0, 0], point[0, 1])
                #     cv2.circle(img, pos, 2, (0, 255, 0), -1)
                # for idx1, point1 in enumerate(left_eye):
                #     pos = (point1[0, 0], point1[0, 1])
                #     cv2.circle(img, pos, 2, (0, 0, 255), -1)
                # for idx2, point2 in enumerate(right_eye):
                #     pos = (point2[0, 0], point2[0, 1])
                #     cv2.circle(img, pos, 2, (0, 0, 255), -1)
                l_tracker, self.left_eye_crop, self.l_points, self.l_RECORD = self.pupil_location(left_eye, img, gray, self.l_points, self.l_RECORD)
                l_height, l_width = self.left_eye_crop.shape
                l_bytesPerLine = 1 * l_width
                l_QImg = QImage(bytes(self.left_eye_crop.data), l_width, l_height, l_bytesPerLine,
                                QImage.Format_Indexed8)
                l_pixmap = QPixmap.fromImage(l_QImg).scaled(self.ui.label_2.width(), self.ui.label_2.height())

                self.ui.label_2.setPixmap(l_pixmap)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            QImg = QImage(img.data, self.width, self.height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(QImg).scaled(self.ui.label.width(), self.ui.label.height())
            self.ui.label.setPixmap(pixmap)

    def pupil_location(self, eye, img, gray, points, RECORD):

        # 通过68个特征点寻找眼睛部位，并且将眼睛框起来
        l = abs(eye[3, 0] - eye[0, 0])  # 两只眼角的长度作为宽度
        # 确定topleft的坐标
        # tl = (eye[0, 0], eye[0, 1] - int(l / 2))
        # br = (eye[3, 0], eye[3, 1] + int(l / 2))
        tl = (
        int(eye[5, 0] + (eye[4, 0] - eye[5, 0]) / 2 - l / 2), int(eye[5, 1] - (eye[5, 1] - eye[1, 1]) / 2 - l / 2))
        crop = gray[tl[1]:(tl[1] + l), tl[0]:(tl[0] + l)]

        gb = cv2.GaussianBlur(crop, (5, 5), 15)
        ret, th1 = cv2.threshold(gb, 50, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        opening = cv2.morphologyEx(th1, cv2.MORPH_OPEN, kernel)
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel2)
        canny = cv2.Canny(closing, 60, 150)
        # cv2.imshow("canny", canny)
        circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 2, 40, param1=30, param2=30, minRadius=0, maxRadius=20)
        # print(circles)
        # if circles!=None:
        tracker = []
        if np.all(circles != None):
            # print("检测到瞳孔！")
            # return circles[0]
            for circle in circles[0]:

                x = int(circle[0])
                y = int(circle[1])
                r = int(circle[2])
                points.extend([(x, y)])
                # print(points)
                flag = 1
                if len(points) == flag:
                    # flag调整定位精度
                    xy = self.stabilize(points)
                    x = int(xy[0])
                    y = int(xy[1])
                    # 由于眼动采集时驾驶人来回的移动，导致像素框的大小在记录时不一致，因此坐标值都处于此时的眼睛框大长度做归一化处理
                    tracker = [float('%.3f' % (x / l - 0.5)), float('%.3f' % (1 - y / l - .5))]
                    RECORD.extend([[float('%.3f' % (x / l - .5)), float('%.3f' % (1 - y / l - .5))]])
                    crop = cv2.line(crop,(0,y),(l,y),(255,255,255),1)
                    crop = cv2.line(crop, (x, 0), (x, l), (255, 255, 255), 1)
                    crop = cv2.circle(crop, (x, y), 2, (0,0,255), -1)
                    xx = tl[0] + x
                    yy = tl[1] + y
                    img = cv2.circle(img, (xx, yy), 2, (0, 0, 255), -1)
                    points = []

        return tracker, crop, points, RECORD
    def stabilize(self,points):
        """
        因为houghCircle的结果一直变化所以我们需要计算瞳孔位置的平均值来稳定结果

        :return:
        """
        sumX = 0
        sumY = 0
        count = 0
        for i in range(len(points)):
            sumX += points[i][0]
            sumY += points[i][1]
            count += 1
        if count > 0:
            sumX /= count
            sumY /= count

        return (sumX, sumY)


    def blink_fatigue(self):

        if self.COUNT>10:
            pass

    def hr_fatigue(self):
        #self.ui.lcdNumber.display('60')
        if self.hr >100 or self.hr <50:
            pass

    def fatigue_intervene(self):
        self.text_area.clear()
        print("检测到疲劳状态，启动干预流程……")
        self.thread_txt.trigger.emit("检测到疲劳状态，启动干预流程……")

        # self.work = MyThread()
        # self.work.trigger.connect(new_warning)
        # self.work.start()
        self.thread_voice.start()



        #self.timer_2.start()



    def fatigue_warning(self):
        import os

        os.system("python3 tired.py")
        print("程序已经启动")

        self.timer_2.stop()








if __name__=='__main__':

    app=QApplication(sys.argv)
    print(sys.argv)
    window=mainWindow()
    window.show()



    sys.exit(app.exec_())