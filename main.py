import serial
import cv2
import numpy
import math
import matplotlib.pyplot as plt

Ser = serial.Serial("COM4", 115200, timeout=5)
# 检测串口是否成功打开
if Ser.isOpen():
    # 创建串口数据换缓存区
    Data_GetAll = []
    # 创建显示区域
    PicShow = numpy.zeros((1000, 1000, 3), dtype=numpy.uint8)
    PicCenter = (500, 500)
    Angle_EndOld = 360.0

    cv2.namedWindow('OUT', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    while True:
        # 将串口数据存入缓存区
        Data_GetAll.append(Ser.read())
        # 判断数据是否到达一帧
        if len(Data_GetAll) >= 47:
            # 寻找帧头
            if b'\x54' in Data_GetAll:
                Begin_N = Data_GetAll.index(b'\x54')
                if len(Data_GetAll) - Begin_N >= 47:
                    if Data_GetAll[Begin_N + 1] == b'\x2c':
                        # 找到帧头后打印这一组数据
                        # print(" ".join(hex(ord(n)) for n in Data_GetAll[Begin_N:Begin_N + 47]))
                        # print(Data_GetAll[Begin_N:Begin_N + 22])
                        # 计算这一帧的信息
                        RunSpeed = (int.from_bytes(Data_GetAll[Begin_N + 3], 'big') * 256
                                    + int.from_bytes(Data_GetAll[Begin_N + 2], 'big')) / 600.0
                        Angle_begin = (int.from_bytes(Data_GetAll[Begin_N + 5], 'big') * 256
                                       + int.from_bytes(Data_GetAll[Begin_N + 4], 'big')) / 100.0
                        Angle_end = (int.from_bytes(Data_GetAll[Begin_N + 43], 'big') * 256
                                     + int.from_bytes(Data_GetAll[Begin_N + 42], 'big')) / 100.0
                        # print(RunSpeed)
                        # print([RunSpeed, Angle_begin, Angle_end])

                        # 距离数据
                        Data_Long = []
                        # 信号质量数据
                        Data_intensity = []
                        for i in range(12):
                            Data_Long.append((int.from_bytes(Data_GetAll[Begin_N + 7 + i * 3], 'big') * 256
                                              + int.from_bytes(Data_GetAll[Begin_N + 6 + i * 3], 'big')) / 20.0)
                            Data_intensity.append(int.from_bytes(Data_GetAll[Begin_N + 8 + i * 3], 'big'))
                        # print(Data_Long)

                        # 判断是否一圈结束并进行显示
                        if Angle_begin <= Angle_EndOld:
                            cv2.circle(PicShow, PicCenter, 3, (0, 0, 255), thickness=3)
                            cv2.imshow("OUT", PicShow)
                            cv2.waitKey(2)
                            PicShow = numpy.zeros((1000, 1000, 3), dtype=numpy.uint8)

                        Angle_EndOld = Angle_end

                        if Angle_begin <= Angle_end:
                            Angle_increment = (Angle_end - Angle_begin) / 11.0
                        else:
                            Angle_increment = (360.0 + Angle_end - Angle_begin) / 11.0

                        # 将对应点画在图像上
                        for i in range(12):
                            # 画线
                            End_Point = (PicCenter[0] + int(Data_Long[i] * math.sin(
                                            (Angle_begin + Angle_increment * (i + 1)) / 180.0 * math.pi)),
                                         PicCenter[1] + int(Data_Long[i] * math.cos(
                                             (Angle_begin + Angle_increment * (i + 1)) / 180.0 * math.pi)))

                            if True:
                                cv2.line(PicShow, PicCenter, End_Point, (255, 0, 0), thickness=1)

                            # 画点
                            if True:
                                cv2.circle(PicShow, End_Point, 2, (0, Data_intensity[i], 0), thickness=2)

                        if Angle_begin >= Angle_end:
                            cv2.circle(PicShow, PicCenter, 3, (0, 0, 255), thickness=3)
                            cv2.imshow("OUT", PicShow)
                            cv2.waitKey(2)
                            PicShow = numpy.zeros((1000, 1000, 3), dtype=numpy.uint8)

                        del Data_GetAll[:Begin_N + 47]
                        Data_Long.clear()

                    else:
                        del Data_GetAll[:Begin_N + 1]
