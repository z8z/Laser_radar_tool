import serial
import numpy as np
import math
import matplotlib.pyplot as plt


'''
theta=np.arange(0,2*np.pi,0.02)              #角度数列值
ax1.plot(theta,2*np.ones_like(theta),lw=2)   #画图，参数：角度，半径，lw线宽

plt.show()

'''
Ser = serial.Serial("COM4", 115200, timeout=5)
# 检测串口是否成功打开
if Ser.isOpen():
    # 启动一个极坐标图
    ax1 = plt.subplot(projection='polar')   
    # 设置角度为顺时针
    ax1.set_theta_direction(-1)
    # 设置显示半径范围 6米 单位为cm
    ax1.set_rmax(600)
    plt.ion()     
    # 创建串口数据换缓存区
    Data_GetAll = []
    Data_AllLong = []
    Data_AllAngel = []
    Angle_endold = 360
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
                        # 对应角度数据
                        Data_Angle = []
                        for i in range(12):
                            Data_Long.append((int.from_bytes(Data_GetAll[Begin_N + 7 + i * 3], 'big') * 256
                                              + int.from_bytes(Data_GetAll[Begin_N + 6 + i * 3], 'big')) / 10.0)
                            Data_intensity.append(int.from_bytes(Data_GetAll[Begin_N + 8 + i * 3], 'big'))
                        # print(Data_Long)

                        if Angle_endold >= Angle_begin:
                            if Data_AllLong != []:
                                try:
                                    ax1.lines.remove(polars[0])
                                except Exception:
                                    pass
                                polars = ax1.plot(Data_AllAngel, Data_AllLong, lw = 1)
                                Data_AllAngel.clear()
                                Data_AllLong.clear()
                                plt.pause(0.0001)

                        if Angle_begin <= Angle_end:
                            Angle_increment = (Angle_end - Angle_begin) / 11.0
                            # 计算对应角度信息
                            for i in range(12):
                                #计算对应角度数据
                                Data_Angle.append((Angle_begin + Angle_increment * (i + 1)) / 180.0 * math.pi)
                            Data_AllAngel += Data_Angle
                            Data_AllLong += Data_Long
                        else:
                            Angle_increment = (360.0 + Angle_end - Angle_begin) / 11.0
                            # 计算对应角度信息
                            for i in range(12):
                                #计算对应角度数据
                                Data_Angle.append((Angle_begin + Angle_increment * (i + 1)) / 180.0 * math.pi)
                            #print(Data_Angle)
                            #print(Data_Angle[:Data_Angle.index(max(Data_Angle))+1])

                            Data_AllAngel += Data_Angle[:Data_Angle.index(max(Data_Angle))+1]
                            Data_AllLong += Data_Long[:Data_Angle.index(max(Data_Angle))+1]
                            #print(Data_AllAngel)
                            #print(Data_AllLong)

                            try:
                                ax1.lines.remove(polars[0])
                            except Exception:
                                pass
                            polars = ax1.plot(Data_AllAngel, Data_AllLong, lw = 1)
                            Data_AllAngel.clear()
                            Data_AllLong.clear()
                            plt.pause(0.0001)

                            Data_AllAngel += [i - 2*math.pi for i in Data_Angle[Data_Angle.index(max(Data_Angle))+1:]]
                            Data_AllLong += Data_Long[Data_Angle.index(max(Data_Angle))+1:]


                        Angle_endold = Angle_end
                        del Data_GetAll[:Begin_N + 47]
                    else:
                        del Data_GetAll[:Begin_N + 1]
