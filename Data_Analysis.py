# -*- coding: utf-8 -*-
# @Time   : 2019/11/26 7:43
# @Author : Gang
# @File   : Data_Analysis.py

import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt5.QtCore import  pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication ,QWidget
from PyQt5.QtWidgets import QSizePolicy
import numpy as np
import pandas as pd
from nptdms import TdmsFile
import math
import time
import copy

class Data_Analysis(QObject):
    sbar = pyqtSignal(str)
    pbar = pyqtSignal(int)
    tbrow= pyqtSignal(str)
    run_end=pyqtSignal()


    def __init__(self,key_para):
        super().__init__()
        self.key_para=key_para

    def run(self):
        self.data=self.loadDataFromFile()
        # self.xx, self.yy, self.ll, self.trace, self.select_trace, self.mean_trigger1_len, self.mean_trigger2_len = self.cutPlot()
        self.cutPlot()
        self.run_end.emit()


    def loadDataFromFile(self):
        start_time1=time.perf_counter()
        self.sbar.emit('Loading data from file ...')
        key_para=self.key_para
        samp_v=self.getSampv(key_para)
        print('Total data points: ', len(samp_v))
        self.tbrow.emit('Total data points: {}'.format(len(samp_v)))
        # data = pd.DataFrame(samp_v, columns=['sampling_voltage'])
        time_used1 = round((time.perf_counter() - start_time1), 2)
        print("load data time used: ", str(time_used1))
        self.sbar.emit('Loading data finished, start calculating current ang logG...')

        start_time2 = time.perf_counter()
        self.sbar.emit('Calculating current data ...')
        if self.key_para['fit_model'] == 'Fit1':
            # data['currentPre'] = data['sampling_voltage'].apply(self.getCurrentFit1)
            self.getCurrentFit1_v=np.vectorize(self.getCurrentFit1)
            currentPre = self.getCurrentFit1_v(samp_v)
        elif self.key_para['fit_model'] == 'Fit2':
            # data['currentPre'] = data['sampling_voltage'].apply(self.getCurrentFit2)
            self.getCurrentFit2_v=np.vectorize(self.getCurrentFit2)
            currentPre = self.getCurrentFit2_v(samp_v)
        elif self.key_para['fit_model'] == 'Fit3':
            # data['currentPre'] = data['sampling_voltage'].apply(self.getCurrentFit3)
            self.getCurrentFit3_v=np.vectorize(self.getCurrentFit3)
            currentPre = self.getCurrentFit3_v(samp_v)

        # currentPre=data['currentPre'].values
        self.background=self.calBg(currentPre)

        # data['current']=data['currentPre'].apply(self.removeBg)
        current=currentPre-self.background

        time_used2 = round((time.perf_counter() - start_time2), 2)
        print("calculate current time used: ", str(time_used2))

        start_time3 = time.perf_counter()
        self.sbar.emit('Calculating logG data ...')
        # data['log_G'] = data['current'].apply(self.getLogG)
        self.getLogG_v=np.vectorize(self.getLogG)
        log_G=self.getLogG_v(current)
        time_used3 = round((time.perf_counter() - start_time3), 2)
        print("calculate log_G time used: ", str(time_used3))
        self.sbar.emit('Calculat finished ...')
        data=pd.DataFrame({'log_G':log_G,
                           'sampling_voltage':samp_v,
                           'currentPre':currentPre,
                           'current':current,
                           })
        return data

    def getSampv(self,key_para):
        file_paths=key_para['file_path']
        model=key_para['fit_model']
        if model == 'Fit3':
            samp_v=self.loadTDMSFit3(file_paths)
        else:
            samp_v=self.loadTMDS(file_paths)
        return samp_v

    def loadTMDS(self,file_paths):
        samp_v = []
        for file_path in file_paths:
            print(str(file_path), '加载中...')
            tdms_file = TdmsFile.read(file_path)
            channel_object = tdms_file.groups()[0].channels()[0][:]
            samp_v.extend(channel_object)
        samp_v = np.array(samp_v)
        return samp_v

    def loadTDMSFit3(self,file_paths):
        samp_v=[]
        for file_path in file_paths:
            print(str(file_path), '加载中...')
            tdms_file = TdmsFile.read(file_path)
            channel_object = tdms_file.groups()[-1].channels()[0][:]
            samp_v.extend(channel_object)
        samp_v=np.array(samp_v)
        return samp_v

    def getCurrentFit1(self,sv):    #sv sampling voltage
        p = self.key_para
        offset=p["f1_offset"]
        sv=sv-offset
        if sv >= 0:
            currentPre = math.exp(p['f1_a2'] * sv + p['f1_b2']) + p['f1_c2'] * sv + p['f1_d2']
        else:
            currentPre = math.exp(p['f1_a1'] * sv + p['f1_b1']) + p['f1_c1'] * sv + p['f1_d1']

        return currentPre

    def getCurrentFit2(self,sv):
        p = self.key_para
        offset = p["f2_offset"]
        sv = sv - offset
        if sv >= 0:
            currentPre = p['f2_a2'] + p['f2_b2'] * np.log(p['f2_c2'] - sv) + p['f2_d2'] * np.power(-sv, 0.68) + p['f2_e2'] / (
                        sv - p['f2_f2'])
        else:
            currentPre = p['f2_a1'] + p['f2_b1'] * np.log(p['f2_c1'] - sv) + p['f2_d1'] * np.power(-sv, 0.68) + p['f2_e1'] / (
                        sv - p['f2_f1'])

        return currentPre

    def getCurrentFit3(self,sv):
        p = self.key_para
        offset = p["f3_offset"]
        sv = sv - offset
        if  sv>=0:
            currentPre=math.pow(10,p['f3_a1']*sv+p['f3_b1'])
        else:
            currentPre = math.pow(10, p['f3_a2'] * sv + p['f3_b2'])

        return currentPre

    def calBg(self,cp):
        length = len(cp)
        index = length // 3
        hist, bin_edges = np.histogram(cp[index:2*index], bins=50, range=(0, 7.76e-11))
        if max(hist) == 0:
            background = 1e-12
        else:
            max_index = np.argmax(hist)
            background = (bin_edges[max_index] + bin_edges[max_index + 1]) / 2
        return background

    def removeBg(self,cp):
        current=cp-self.background
        return current

    def getLogG(self, current):
        biasV = self.key_para['biasV']
        #if self.key_para['fit_model'] == 'Fit3':
        #    G1 = 1 / self.key_para['f3_r1']
        #    log_G = math.log10(abs((current * 10 - G1) * 12887))
        #else:
        log_G = math.log10(abs(current * 12886.6/biasV))

        return log_G

    def cutPlot(self):
        self.sbar.emit('Start to cut single trace...')
        if self.key_para['process_open']:
            self.cut_trigger, self.len_cut_trigger, self.select_index = self.cutOpenTraces()
        else:
            self.cut_trigger, self.len_cut_trigger, self.select_index = self.cutCloseTraces()


        # xx, yy, ll, select_cut_trigger, mean_trigger1_len, mean_trigger2_len = self.cal2DConductance()
        # return xx, yy, ll, self.cut_trigger, select_cut_trigger, mean_trigger1_len, mean_trigger2_len

    def cutOpenTraces(self):
        start_time=time.perf_counter()

        log_G = self.data['log_G'].values
        #==========================================#
        start, end, zero, len_high, len_low = {}, {}, {}, {}, {}
        start1, end1, start2, end2 = {}, {}, {}, {}
        cut_trigger, len_cut_trigger, select_index = [], [], []
        n = 0
        STEP = 30  # -1.2 +7
        # SET_ZERO_POINT = -0.3
        SET_ZERO_POINT=self.key_para['zero_set']
        HIGH_CUT_TRIGGER = self.key_para['high_cut']
        LOW_CUT_TRIGGER = self.key_para['low_cut']
        LEN_HIGH_CUT = self.key_para['high_len_cut']
        LEN_LOW_CUT = self.key_para['low_len_cut']
        START1 = self.key_para['start1']
        END1 = self.key_para['end1']
        START2 = self.key_para['start2']
        END2 = self.key_para['end2']
        all_len = len(log_G)
        index_list = [x for x in range(STEP * 10, all_len - STEP * 10, STEP)]
        self.pbar.emit(int(0))

        for i in index_list:
            self.pbar.emit(int(i / all_len * 100))
            m1 = np.mean(log_G[i - STEP:i])
            m2 = np.mean(log_G[i:i + STEP])

            if np.mean(log_G[i - STEP * 10:i]) > np.mean(log_G[i:i + STEP * 10]):
                if m1 - HIGH_CUT_TRIGGER >= 0 and m2 - HIGH_CUT_TRIGGER <= 0:
                    start[n] = i
                if m1 - SET_ZERO_POINT >= 0 and m2 - SET_ZERO_POINT <= 0:
                    zero[n] = i
                if m1 - LEN_HIGH_CUT >= 0 and m2 - LEN_HIGH_CUT <= 0:
                    len_high[n] = i
                if m1 - LOW_CUT_TRIGGER >= 0 and m2 - LOW_CUT_TRIGGER <= 0:
                    end[n] = i
                if m1 - LEN_LOW_CUT >= 0 and m2 - LEN_LOW_CUT <= 0:
                    len_low[n] = i
                if m1 - START1 >= 0 and m2 - START1 <= 0:
                    start1[n] = i
                if m1 - END1 >= 0 and m2 - END1 <= 0:
                    end1[n] = i
                if m1 - START2 >= 0 and m2 - START2 <= 0:
                    start2[n] = i
                if m1 - END2 >= 0 and m2 - END2 <= 0:
                    end2[n] = i
            elif m1 - LOW_CUT_TRIGGER <= 0 and m2 - LOW_CUT_TRIGGER >= 0:
                n += 1

        for i in range(n):
            if i in start.keys() and i in end.keys() and i in zero.keys() and i in len_high.keys() and i in len_low.keys() and i in start1.keys() and i in end1.keys() and i in start2.keys() and i in end2.keys():
                select1 = abs(start1[i] - end1[i])
                select2 = abs(start2[i] - end2[i])
                cut_trigger.append([start[i], end[i], zero[i]])
                len_cut_trigger.append([len_high[i], len_low[i]])
                select_index.append([select1, select2])

        print("The number of single_trace is: ", len(cut_trigger))
        self.sbar.emit("The number of single trace is: " + str(len(cut_trigger)))

        time_used = round((time.perf_counter() - start_time), 2)
        print("cut trace time used: ", str(time_used))
        cut_trigger = np.array(cut_trigger)
        len_cut_trigger = np.array(len_cut_trigger)
        select_index = np.array(select_index)
        return cut_trigger, len_cut_trigger, select_index

    def cutCloseTraces(self):
        log_G = self.data['log_G'].values
        start, end, zero, len_high, len_low = {}, {}, {}, {}, {}
        start1, end1, start2, end2 = {}, {}, {}, {}
        cut_trigger, len_cut_trigger, select_index = [], [], []
        n = 0
        STEP = 100  # -1.2 +7
        SET_ZERO_POINT = -0.3
        HIGH_CUT_TRIGGER = self.key_para['high_cut']
        LOW_CUT_TRIGGER = self.key_para['low_cut']
        LEN_HIGH_CUT = self.key_para['high_len_cut']
        LEN_LOW_CUT = self.key_para['low_len_cut']
        START1 = self.key_para['start1']
        END1 = self.key_para['end1']
        START2 = self.key_para['start2']
        END2 = self.key_para['end2']
        all_len = len(log_G)
        index_list = [x for x in range(STEP * 10, all_len - STEP * 10, STEP)]
        self.pbar.emit(int(0))

        for i in index_list:
            self.pbar.emit(int(i / all_len * 100))
            m1 = np.mean(log_G[i - STEP:i])
            m2 = np.mean(log_G[i:i + STEP])
            if np.mean(log_G[i - STEP * 10:i]) < np.mean(log_G[i:i + STEP * 10]):
                if m1 - HIGH_CUT_TRIGGER <= 0 and m2 - HIGH_CUT_TRIGGER >= 0:
                    start[n] = i
                if m1 - SET_ZERO_POINT <= 0 and m2 - SET_ZERO_POINT >= 0:
                    zero[n] = i
                if m1 - LEN_HIGH_CUT <= 0 and m2 - LEN_HIGH_CUT >= 0:
                    len_high[n] = i
                if m1 - LOW_CUT_TRIGGER <= 0 and m2 - LOW_CUT_TRIGGER >= 0:
                    end[n] = i
                if m1 - LEN_LOW_CUT <= 0 and m2 - LEN_LOW_CUT >= 0:
                    len_low[n] = i
                if m1 - START1 <= 0 and m2 - START1 >= 0:
                    start1[n] = i
                if m1 - END1 <= 0 and m2 - END1 >= 0:
                    end1[n] = i
                if m1 - START2 <= 0 and m2 - START2 >= 0:
                    start2[n] = i
                if m1 - END2 <= 0 and m2 - END2 >= 0:
                    end2[n] = i
            elif m1 - HIGH_CUT_TRIGGER >= 0 and m2 - HIGH_CUT_TRIGGER <= 0:
                n += 1

            QApplication.processEvents()

        for i in range(n):
            if i in start.keys() and i in end.keys() and i in zero.keys() and i in len_high.keys() and i in len_low.keys() and i in start1.keys() and i in end1.keys() and i in start2.keys() and i in end2.keys():
                select1 = abs(start1[i] - end1[i])
                select2 = abs(start2[i] - end2[i])
                cut_trigger.append([start[i], end[i], zero[i]])
                len_cut_trigger.append([len_high[i], len_low[i]])
                select_index.append([select1, select2])
        print("The number of single_trace is: ", len(cut_trigger))
        self.sbar.emit("The number of single trace is: " + str(len(cut_trigger)))

        return cut_trigger, len_cut_trigger, select_index

    # def cal2DConductance(self):
    #     start_time=time.perf_counter()
    #     self.sbar.emit('Data calculation completed ...')
    #     cut_trigger = self.cut_trigger      #起始点，零点，终止点
    #     len_cut_trigger = self.len_cut_trigger      #长度统计对应的点
    #     select_index = self.select_index        #[select1, select2]
    #
    #     # 针对新盒子的逆向数据
    #     if self.key_para['fit_model'] == 'Fit3':
    #         log_G = self.data['log_G'].values[::-1]
    #     else:
    #         log_G = self.data['log_G'].values
    #     # ==========================================#
    #
    #     streching_rate = self.key_para['stretching_rate']
    #     sampling_rate = self.key_para['sampling_rate']
    #     lower_limit1 = self.key_para['lower_limit1']
    #     upper_limit1 = self.key_para['upper_limit1']
    #     lower_limit2 = self.key_para['lower_limit2']
    #     upper_limit2 = self.key_para['upper_limit2']
    #     r = sampling_rate / streching_rate
    #     select_cut_trigger, select_len_cut_trigger = [], []
    #     xx, yy, ll = [], [], []
    #     trigger1_len, trigger2_len = [], []
    #
    #     for i, j, h in zip(select_index, cut_trigger, len_cut_trigger):
    #         trigger1 = i[0]/r
    #         trigger2 = i[1]/r
    #         trigger1_len.append(trigger1)
    #         trigger2_len.append(trigger2)
    #         if lower_limit1 <= trigger1 <= upper_limit1 and lower_limit2 <= trigger2 <= upper_limit2:
    #             select_cut_trigger.append(j)
    #             select_len_cut_trigger.append(h)
    #
    #     if self.key_para['process_open']:
    #         for i in select_cut_trigger:
    #             for ii in range(i[0], i[1]):
    #                 xx.append((ii - i[2]) / r)
    #                 yy.append(log_G[ii])
    #     else:
    #         for i in select_cut_trigger:
    #             for ii in range(i[1], i[0]):
    #                 xx.append((i[2]-ii) / r)
    #                 yy.append(log_G[ii])
    #
    #     for j in select_len_cut_trigger:
    #         ll.append(abs((j[1] - j[0]) / r))
    #
    #     all_trace_n = len(len_cut_trigger)
    #     selected_trace_n = len(select_len_cut_trigger)
    #     mean_trigger1_len = np.mean(trigger1_len)
    #     mean_trigger2_len = np.mean(trigger2_len)
    #     print('mean_trigger1_len: ', mean_trigger1_len, '  mean_trigger2_len: ', mean_trigger2_len)
    #     print('all_trace:', all_trace_n, '  selected_trace: ', selected_trace_n)
    #     self.sbar.emit('Show figure.')
    #     self.pbar.emit(int(100))
    #     time_used = round((time.perf_counter()- start_time),2)
    #     print("calculate figure data time used: ", str(time_used))
    #
    #     return xx, yy, ll, select_cut_trigger, mean_trigger1_len, mean_trigger2_len

class CalDrawData(QObject):
    run_end=pyqtSignal()
    sbar = pyqtSignal(str)
    pbar = pyqtSignal(int)

    def __init__(self,key_para,cut_trigger,len_cut_trigger,select_index,data):
        super().__init__()
        self.key_para=key_para
        self.cut_trigger=cut_trigger
        self.len_cut_trigger=len_cut_trigger
        self.select_index=select_index
        self.data=data
    def run(self):
        # print('进入run函数')
        self.start_time = time.perf_counter()
        self.addPoint()  # 增加additional length
        self.sbar.emit('Start calculating the data required for the drawing ...')
        self.calData()
        self.run_end.emit()

    def calData(self):
        cut_trigger = self.cut_trigger_add  # 起始点，终止点，零点
        len_cut_trigger = self.len_cut_trigger  # 长度统计对应的点
        select_index = self.select_index  # [select1, select2]
        log_G = self.data['log_G'].values

        streching_rate = self.key_para['stretching_rate']
        sampling_rate = self.key_para['sampling_rate']
        lower_limit1 = self.key_para['lower_limit1']
        upper_limit1 = self.key_para['upper_limit1']
        lower_limit2 = self.key_para['lower_limit2']
        upper_limit2 = self.key_para['upper_limit2']

        r = sampling_rate / streching_rate
        select_cut_trigger, select_len_cut_trigger = [], []
        xx, yy, ll = [], [], []
        trigger1_len, trigger2_len = [], []

        for i, j, h in zip(select_index, cut_trigger, len_cut_trigger):
            trigger1 = i[0] / r
            trigger2 = i[1] / r
            trigger1_len.append(trigger1)
            trigger2_len.append(trigger2)
            if lower_limit1 <= trigger1 <= upper_limit1 and lower_limit2 <= trigger2 <= upper_limit2:
                select_cut_trigger.append(j)
                select_len_cut_trigger.append(h)

        if self.key_para['process_open']:
            for i in select_cut_trigger:
                for ii in range(i[0], i[1]):
                    xx.append((ii - i[2]) / r)
                    yy.append(log_G[ii])
        else:
            for i in select_cut_trigger:
                for ii in range(i[1], i[0]):
                    xx.append((i[2] - ii) / r)
                    yy.append(log_G[ii])

        for j in select_len_cut_trigger:
            ll.append(abs((j[1] - j[0]) / r))

        all_trace_n = len(len_cut_trigger)
        selected_trace_n = len(select_len_cut_trigger)
        mean_trigger1_len = np.mean(trigger1_len)
        mean_trigger2_len = np.mean(trigger2_len)
        print('mean_trigger1_len: ', mean_trigger1_len, '  mean_trigger2_len: ', mean_trigger2_len)
        print('all_trace:', all_trace_n, '  selected_trace: ', selected_trace_n)
        self.sbar.emit('Show figure.')
        self.pbar.emit(int(100))
        time_used = round((time.perf_counter() - self.start_time), 2)
        print("calculate figure data time used: ", str(time_used))
        self.xx, self.yy, self.ll, self.select_cut_trigger, self.mean_trigger1_len, \
        self.mean_trigger2_len = xx, yy, ll, select_cut_trigger, mean_trigger1_len, mean_trigger2_len

    def addPoint(self):
        add_length = self.key_para['add_length']
        self.cut_trigger_add = copy.deepcopy(self.cut_trigger)
        self.cut_trigger_add[:, 1] = self.cut_trigger_add[:, 1] + add_length

class Conductance_Figure(FigureCanvas):  # 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键
    def __init__(self, width=4, height=6, dpi=75, ):
        self.main_frame = QWidget()
        #self.fig = Figure(figsize=(width, height),dpi=dpi)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure
        self.fig=plt.figure(figsize=(width, height),dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)  # 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        self.canvas.setParent(self.main_frame)
        FigureCanvas.__init__(self, self.fig)  # 初始化父类

        super(Conductance_Figure, self).__init__(self.fig)  # 在父类中激活Figure窗口，此句必不可少，否则不能显示图形
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)