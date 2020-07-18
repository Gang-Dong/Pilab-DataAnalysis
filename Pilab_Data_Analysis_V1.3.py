# -*- coding: utf-8 -*-
# @Time   : 2019/11/22 21:27
# @Author : Gang
# @File   : Pilab_Data_Analysis_V1.3.py

import sys

from untitled_V13_3 import *
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import Cursor
from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QStyleFactory, QMainWindow,QMessageBox
from PyQt5.QtCore import QDateTime,QThread
from Data_Analysis import *
from scipy.stats import norm
import configparser
import os
import time
import sip



class XMewindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.key_para = {}

        self.setupUi(self)
        self.run_first = True
        self.draw_first=True
        self.single_run_first = True
        self.initUI()
    def initUI(self):
        self.progressBar.setValue(int(0))

        self.CB_style.addItems(QStyleFactory.keys())  # 下拉框combobox，用来设置样式
        index = self.CB_style.findText(QApplication.style().objectName(), QtCore.Qt.MatchFixedString)
        self.CB_style.setCurrentIndex(index)
        self.CB_style.activated[str].connect(self.handleStyleChanged)  # handleStyleChanged用来修改样式

        self.QRB_open.setChecked(True)

        self.FitMode_box.currentIndexChanged.connect(self.fitModeChanged)

        self.conductance_length_layout = QVBoxLayout(self)
        self.conductance_count_layout = QVBoxLayout(self)
        self.length_layout = QVBoxLayout(self)
        self.single_trace_layout = QVBoxLayout(self)
        self.Run_btn.setEnabled(False)
        self.QPB_save_all.setEnabled(False)
        self.QPB_save_goodtrace.setEnabled(False)
        self.QPB_redraw.setEnabled(False)
        self.QPB_update.setEnabled(False)
        self.getInitParaValue(self)

        self.textBrowser.setPlainText('Please load file firstly, then press run button to analysis.')
        self.Load_btn.clicked.connect(self.getFilepathList)
        self.Run_btn.clicked.connect(self.runButton)
        self.QPB_redraw.clicked.connect(self.reDrawBtn)
        self.QPB_save_all.clicked.connect(self.saveDataAndFig)
        self.QPB_save_goodtrace.clicked.connect(self.saveGoodTrace)
        self.QPB_reset.clicked.connect(self.resetBtn)
        self.QPB_update.clicked.connect(self.updateAdd)

        self.QRB_open.toggled.connect(lambda: self.processState(self.QRB_open))
        self.QRB_close.toggled.connect(lambda: self.processState(self.QRB_close))


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'message', "Sure to quit ?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.saveKeyPara()
            time.sleep(0.5)
            self.showStatusbarMessage('key parameter saved. ')
            print('save key parameter...')
            event.accept()
        else:
            event.ignore()

    def processState(self,btn):
        if btn.text()=='open':
            if btn.isChecked()==True:
                self.key_para['process_open']=True
                self.QRB_close.setChecked(False)
            else:
                self.key_para['process_open']=False
                self.QRB_close.setChecked(True)

        if btn.text()=='close':
            if btn.isChecked() ==True:
                self.key_para['process_open'] = False
                self.QRB_open.setChecked(False)
            else:
                self.key_para['process_open'] = True
                self.QRB_open.setChecked(True)
        print('open: ', str(self.QRB_open.isChecked()), '   close: ', str(self.QRB_close.isChecked()))

    def fitModeChanged(self):
        if self.FitMode_box.currentIndex()==0:
            self.key_para['fit_model']='Fit1'
        elif self.FitMode_box.currentIndex()==1:
            self.key_para['fit_model']='Fit2'
        elif self.FitMode_box.currentIndex()==2:
            self.key_para['fit_model']='Fit3'
        print('fit_mode: ', str(self.FitMode_box.currentText()))

    def handleStyleChanged(self, style):
        QApplication.setStyle(style)

    def getInitParaValue(self, MainWindow):
        if os.path.exists('config'):
            _translate = QtCore.QCoreApplication.translate
            config = configparser.ConfigParser()
            config.read('config', encoding='utf-8')
            self.QPT_sampling_rate.setPlainText(_translate("MainWindow", config.get('key_para', 'sampling_rate')))
            self.QPT_strecting_rate.setPlainText(_translate("MainWindow", config.get('key_para', 'stretching_rate')))
            self.QPT_high_cut.setPlainText(_translate("MainWindow", config.get('key_para', 'high_cut')))
            self.QPT_low_cut.setPlainText(_translate("MainWindow", config.get('key_para', 'low_cut')))
            self.QPT_high_length.setPlainText(_translate("MainWindow", config.get('key_para', 'high_len_cut')))
            self.QPT_low_length.setPlainText(_translate("MainWindow", config.get('key_para', 'low_len_cut')))
            self.QPT_add_length.setPlainText(_translate("MainWindow", config.get('key_para', 'add_length')))
            self.QPT_biasV.setPlainText(_translate("MainWindow", config.get('key_para', 'biasV')))
            self.QPT_zero_set.setPlainText(_translate("MainWindow", config.get('key_para', 'zero_set')))

            self.QPT_2D_binsx.setPlainText(_translate("MainWindow", config.get('key_para', '2D_bins_x')))
            self.QPT_2D_binsy.setPlainText(_translate("MainWindow", config.get('key_para', '2D_bins_y')))
            self.QPT_2D_xlim_l.setPlainText(_translate("MainWindow", config.get('key_para', '2D_xlim_l')))
            self.QPT_2D_xlim_r.setPlainText(_translate("MainWindow", config.get('key_para', '2D_xlim_r')))
            self.QPT_2D_ylim_l.setPlainText(_translate("MainWindow", config.get('key_para', '2D_ylim_l')))
            self.QPT_2D_ylim_r.setPlainText(_translate("MainWindow", config.get('key_para', '2D_ylim_r')))

            self.QPT_1D_bins.setPlainText(_translate("MainWindow", config.get('key_para', '1D_bins')))

            self.QPT_leng_xlim_l.setPlainText(_translate("MainWindow", config.get('key_para', 'leng_xlim_l')))
            self.QPT_leng_xlim_r.setPlainText(_translate("MainWindow", config.get('key_para', 'leng_xlim_r')))
            self.QPT_leng_bins.setPlainText(_translate("MainWindow", config.get('key_para', 'leng_bins')))


            self.QPT_start1.setPlainText(_translate("MainWindow", config.get('key_para', 'start1')))
            self.QPT_end1.setPlainText(_translate("MainWindow", config.get('key_para', 'end1')))
            self.QPT_start2.setPlainText(_translate("MainWindow", config.get('key_para', 'start2')))
            self.QPT_end2.setPlainText(_translate("MainWindow", config.get('key_para', 'end2')))
            self.QPT_lower_limit1.setPlainText(_translate("MainWindow", config.get('key_para', 'lower_limit1')))
            self.QPT_upper_limit1.setPlainText(_translate("MainWindow", config.get('key_para', 'upper_limit1')))
            self.QPT_lower_limit2.setPlainText(_translate("MainWindow", config.get('key_para', 'lower_limit2')))
            self.QPT_upper_limit2.setPlainText(_translate("MainWindow", config.get('key_para', 'upper_limit2')))

            self.QPT_f1_a1.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_a1')))
            self.QPT_f1_b1.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_b1')))
            self.QPT_f1_c1.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_c1')))
            self.QPT_f1_d1.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_d1')))
            self.QPT_f1_a2.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_a2')))
            self.QPT_f1_b2.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_b2')))
            self.QPT_f1_c2.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_c2')))
            self.QPT_f1_d2.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_d2')))
            self.QPT_f1_offset.setPlainText(_translate("MainWindow", config.get('key_para', 'f1_offset')))

            self.QPT_f2_a1.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_a1')))
            self.QPT_f2_a2.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_a2')))
            self.QPT_f2_b1.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_b1')))
            self.QPT_f2_b2.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_b2')))
            self.QPT_f2_c1.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_c1')))
            self.QPT_f2_c2.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_c2')))
            self.QPT_f2_d1.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_d1')))
            self.QPT_f2_d2.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_d2')))
            self.QPT_f2_e1.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_e1')))
            self.QPT_f2_e2.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_e2')))
            self.QPT_f2_f1.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_f1')))
            self.QPT_f2_f2.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_f2')))
            self.QPT_f2_offset.setPlainText(_translate("MainWindow", config.get('key_para', 'f2_offset')))

            self.QPT_f3_a1.setPlainText(_translate("MainWindow", config.get('key_para', 'f3_a1')))
            self.QPT_f3_b1.setPlainText(_translate("MainWindow", config.get('key_para', 'f3_b1')))
            self.QPT_f3_a2.setPlainText(_translate("MainWindow", config.get('key_para', 'f3_a2')))
            self.QPT_f3_b2.setPlainText(_translate("MainWindow", config.get('key_para', 'f3_b2')))
            self.QPT_f3_r1.setPlainText(_translate("MainWindow", config.get('key_para', 'f3_r1')))
            self.QPT_f3_offset.setPlainText(_translate("MainWindow", config.get('key_para', 'f3_offset')))

            self.showStatusbarMessage('get key parameter value from config file.')
            print('get_config_value...')

    def getPanelValue(self):
        self.key_para['sampling_rate'] = int(self.QPT_sampling_rate.toPlainText())
        self.key_para['stretching_rate'] = float(self.QPT_strecting_rate.toPlainText())
        self.key_para['high_cut'] = float(self.QPT_high_cut.toPlainText())
        self.key_para['low_cut'] = float(self.QPT_low_cut.toPlainText())
        self.key_para['high_len_cut'] = float(self.QPT_high_length.toPlainText())
        self.key_para['low_len_cut'] = float(self.QPT_low_length.toPlainText())
        self.key_para['add_length']=float(self.QPT_add_length.toPlainText())
        self.key_para['biasV']=float(self.QPT_biasV.toPlainText())
        self.key_para['zero_set']=float(self.QPT_zero_set.toPlainText())

        self.key_para['fit_model'] = str(self.FitMode_box.currentText())

        self.key_para['process_open'] = bool(self.QRB_open.isChecked())

        self.key_para['2D_bins_x']=int(self.QPT_2D_binsx.toPlainText())
        self.key_para['2D_bins_y'] = int(self.QPT_2D_binsy.toPlainText())
        self.key_para['2D_xlim_l']= float(self.QPT_2D_xlim_l.toPlainText())
        self.key_para['2D_xlim_r'] = float(self.QPT_2D_xlim_r.toPlainText())
        self.key_para['2D_ylim_l'] = float(self.QPT_2D_ylim_l.toPlainText())
        self.key_para['2D_ylim_r'] = float(self.QPT_2D_ylim_r.toPlainText())

        self.key_para['1D_xlim_l'] =float(self.QPT_1D_xlim_l.toPlainText())
        self.key_para['1D_xlim_r'] = float(self.QPT_1D_xlim_r.toPlainText())
        self.key_para['1D_bins'] = int(self.QPT_1D_bins.toPlainText())

        self.key_para['leng_xlim_l'] = float(self.QPT_leng_xlim_l.toPlainText())
        self.key_para['leng_xlim_r'] = float(self.QPT_leng_xlim_r.toPlainText())
        self.key_para['leng_bins'] = int(self.QPT_leng_bins.toPlainText())

        self.key_para['start1'] = float(self.QPT_start1.toPlainText())
        self.key_para['end1'] = float(self.QPT_end1.toPlainText())
        self.key_para['start2'] = float(self.QPT_start2.toPlainText())
        self.key_para['end2'] = float(self.QPT_end2.toPlainText())
        self.key_para['lower_limit1'] = float(self.QPT_lower_limit1.toPlainText())
        self.key_para['upper_limit1'] = float(self.QPT_upper_limit1.toPlainText())
        self.key_para['lower_limit2'] = float(self.QPT_lower_limit2.toPlainText())
        self.key_para['upper_limit2'] = float(self.QPT_upper_limit2.toPlainText())

        self.key_para['f1_a1'] = float(self.QPT_f1_a1.toPlainText())
        self.key_para['f1_a2'] = float(self.QPT_f1_a2.toPlainText())
        self.key_para['f1_b1'] = float(self.QPT_f1_b1.toPlainText())
        self.key_para['f1_b2'] = float(self.QPT_f1_b2.toPlainText())
        self.key_para['f1_c1'] = float(self.QPT_f1_c1.toPlainText())
        self.key_para['f1_c2'] = float(self.QPT_f1_c2.toPlainText())
        self.key_para['f1_d1'] = float(self.QPT_f1_d1.toPlainText())
        self.key_para['f1_d2'] = float(self.QPT_f1_d2.toPlainText())
        self.key_para['f1_offset'] = float(self.QPT_f1_offset.toPlainText())

        self.key_para['f2_a1'] = float(self.QPT_f2_a1.toPlainText())
        self.key_para['f2_b1'] = float(self.QPT_f2_b1.toPlainText())
        self.key_para['f2_c1'] = float(self.QPT_f2_c1.toPlainText())
        self.key_para['f2_d1'] = float(self.QPT_f2_d1.toPlainText())
        self.key_para['f2_e1'] = float(self.QPT_f2_e1.toPlainText())
        self.key_para['f2_f1'] = float(self.QPT_f2_f1.toPlainText())
        self.key_para['f2_a2'] = float(self.QPT_f2_a2.toPlainText())
        self.key_para['f2_b2'] = float(self.QPT_f2_b2.toPlainText())
        self.key_para['f2_c2'] = float(self.QPT_f2_c2.toPlainText())
        self.key_para['f2_d2'] = float(self.QPT_f2_d2.toPlainText())
        self.key_para['f2_e2'] = float(self.QPT_f2_e2.toPlainText())
        self.key_para['f2_f2'] = float(self.QPT_f2_f2.toPlainText())
        self.key_para['f2_offset'] = float(self.QPT_f2_offset.toPlainText())

        self.key_para['f3_a1'] = float(self.QPT_f3_a1.toPlainText())
        self.key_para['f3_b1'] = float(self.QPT_f3_b1.toPlainText())
        self.key_para['f3_a2'] = float(self.QPT_f3_a2.toPlainText())
        self.key_para['f3_b2'] = float(self.QPT_f3_b2.toPlainText())
        self.key_para['f3_r1']=float(self.QPT_f3_r1.toPlainText())
        self.key_para['f3_offset'] = float(self.QPT_f3_offset.toPlainText())

        self.showStatusbarMessage('Loading panel parameters...')
        print('get_panel_value: ', self.key_para)

    def saveKeyPara(self):
        config = configparser.ConfigParser()
        config.add_section('key_para')
        config.set('key_para', 'sampling_rate', str(self.QPT_sampling_rate.toPlainText()))
        config.set('key_para', 'stretching_rate', str(self.QPT_strecting_rate.toPlainText()))
        config.set('key_para', 'high_cut', str(self.QPT_high_cut.toPlainText()))
        config.set('key_para', 'low_cut', str(self.QPT_low_cut.toPlainText()))
        config.set('key_para', 'high_len_cut', str(self.QPT_high_length.toPlainText()))
        config.set('key_para', 'low_len_cut', str(self.QPT_low_length.toPlainText()))
        config.set('key_para', 'add_length', str(self.QPT_add_length.toPlainText()))
        config.set('key_para', 'biasV', str(self.QPT_biasV.toPlainText()))
        config.set('key_para', 'zero_set', str(self.QPT_zero_set.toPlainText()))

        config.set('key_para','2D_bins_x',str(self.QPT_2D_binsx.toPlainText()))
        config.set('key_para', '2D_bins_y', str(self.QPT_2D_binsy.toPlainText()))
        config.set('key_para','2D_xlim_l',str(self.QPT_2D_xlim_l.toPlainText()))
        config.set('key_para', '2D_xlim_r', str(self.QPT_2D_xlim_r.toPlainText()))
        config.set('key_para', '2D_ylim_l', str(self.QPT_2D_ylim_l.toPlainText()))
        config.set('key_para', '2D_ylim_r', str(self.QPT_2D_ylim_r.toPlainText()))

        config.set('key_para', '1D_xlim_l', str(self.QPT_1D_xlim_l.toPlainText()))
        config.set('key_para', '1D_xlim_r', str(self.QPT_1D_xlim_r.toPlainText()))
        config.set('key_para', '1D_bins', str(self.QPT_1D_bins.toPlainText()))

        config.set('key_para', 'leng_xlim_l', str(self.QPT_leng_xlim_l.toPlainText()))
        config.set('key_para', 'leng_xlim_r', str(self.QPT_leng_xlim_r.toPlainText()))
        config.set('key_para', 'leng_bins', str(self.QPT_leng_bins.toPlainText()))

        config.set('key_para', 'start1', str(self.QPT_start1.toPlainText()))
        config.set('key_para', 'end1', str(self.QPT_end1.toPlainText()))
        config.set('key_para', 'start2', str(self.QPT_start2.toPlainText()))
        config.set('key_para', 'end2', str(self.QPT_end2.toPlainText()))
        config.set('key_para', 'lower_limit1', str(self.QPT_lower_limit1.toPlainText()))
        config.set('key_para', 'upper_limit1', str(self.QPT_upper_limit1.toPlainText()))
        config.set('key_para', 'lower_limit2', str(self.QPT_lower_limit2.toPlainText()))
        config.set('key_para', 'upper_limit2', str(self.QPT_upper_limit2.toPlainText()))

        config.set('key_para', 'f1_a1', str(self.QPT_f1_a1.toPlainText()))
        config.set('key_para', 'f1_b1', str(self.QPT_f1_b1.toPlainText()))
        config.set('key_para', 'f1_c1', str(self.QPT_f1_c1.toPlainText()))
        config.set('key_para', 'f1_d1', str(self.QPT_f1_d1.toPlainText()))
        config.set('key_para', 'f1_a2', str(self.QPT_f1_a2.toPlainText()))
        config.set('key_para', 'f1_b2', str(self.QPT_f1_b2.toPlainText()))
        config.set('key_para', 'f1_c2', str(self.QPT_f1_c2.toPlainText()))
        config.set('key_para', 'f1_d2', str(self.QPT_f1_d2.toPlainText()))
        config.set('key_para', 'f1_offset', str(self.QPT_f1_offset.toPlainText()))

        config.set('key_para', 'f2_a1', str(self.QPT_f2_a1.toPlainText()))
        config.set('key_para', 'f2_b1', str(self.QPT_f2_b1.toPlainText()))
        config.set('key_para', 'f2_c1', str(self.QPT_f2_c1.toPlainText()))
        config.set('key_para', 'f2_d1', str(self.QPT_f2_d1.toPlainText()))
        config.set('key_para', 'f2_e1', str(self.QPT_f2_e1.toPlainText()))
        config.set('key_para', 'f2_f1', str(self.QPT_f2_f1.toPlainText()))
        config.set('key_para', 'f2_a2', str(self.QPT_f2_a2.toPlainText()))
        config.set('key_para', 'f2_b2', str(self.QPT_f2_b2.toPlainText()))
        config.set('key_para', 'f2_c2', str(self.QPT_f2_c2.toPlainText()))
        config.set('key_para', 'f2_d2', str(self.QPT_f2_d2.toPlainText()))
        config.set('key_para', 'f2_e2', str(self.QPT_f2_e2.toPlainText()))
        config.set('key_para', 'f2_f2', str(self.QPT_f2_f2.toPlainText()))
        config.set('key_para', 'f2_offset', str(self.QPT_f2_offset.toPlainText()))

        config.set('key_para', 'f3_a1', str(self.QPT_f3_a1.toPlainText()))
        config.set('key_para', 'f3_b1', str(self.QPT_f3_b1.toPlainText()))
        config.set('key_para', 'f3_a2', str(self.QPT_f3_a2.toPlainText()))
        config.set('key_para', 'f3_b2', str(self.QPT_f3_b2.toPlainText()))
        config.set('key_para', 'f3_r1', str(self.QPT_f3_r1.toPlainText()))
        config.set('key_para', 'f3_offset', str(self.QPT_f3_offset.toPlainText()))

        config.write(open('config', 'w'))
        self.showStatusbarMessage('key parameters saved!')

    def showStatusbarMessage(self, sbar):
        date = QDateTime.currentDateTime()
        currentTime = date.toString('yyyy-MM-dd hh:mm:ss')
        self.statusBar().showMessage('['+currentTime+']   '+sbar)

    def showProgressBar(self,pbar):
        self.progressBar.setValue(pbar)

    def showTextBroswer(self,text):
        date = QDateTime.currentDateTime()
        currentTime = date.toString('yyyy-MM-dd hh:mm:ss')
        self.textBrowser.append('[' + currentTime + ']  ' + text)


    def getFilepathList(self):
        date = QDateTime.currentDateTime()
        currentTime = date.toString('yyyy-MM-dd hh:mm:ss')
        openfile_name = QFileDialog.getOpenFileNames(self, '选择文件',"./","TDMS Files(*.tdms)")

        self.key_para['file_path'] = openfile_name[0]

        if len(self.key_para['file_path'])>1:
            self.textBrowser.append('[' + currentTime + ']  ' + 'File list:')
            for i in self.key_para['file_path']:
                p=i.split('/')[-1]
                self.textBrowser.append(p)
            self.key_para['img_path'] = 'stack_file'
        elif not self.key_para['file_path']:
            QMessageBox.warning(self, 'Warning', 'Please select at least one data file !',QMessageBox.Ok )
            self.textBrowser.append('[' + currentTime + ']  ' +'Data file not selected, please re-select')
            self.showStatusbarMessage('Please select at least one data file. ')
        else:
            self.key_para['img_path'] = self.key_para['file_path'][0].split('/')[-1][:-5]
            self.textBrowser.append('[' + currentTime + ']  ' + 'File list:')
            self.textBrowser.append(self.key_para['file_path'][0].split('/')[-1])

        if self.key_para['file_path']:
            self.showStatusbarMessage('Analysis file selected. ')
            self.key_para['load_file_bool'] = True
            self.Run_btn.setEnabled(True)
            print(self.key_para['img_path'])

    def runButton(self):
        self.Run_btn.setEnabled(False)
        self.QPB_save_all.setEnabled(False)
        self.QPB_save_goodtrace.setEnabled(False)
        self.QPB_update.setEnabled(False)

        # if self.run_first:
        #     self.run_first=False
        # else:
        #     self.conductance_length_layout.removeWidget(self.fig1)
        #     self.conductance_length_layout.removeWidget(self.toolbar_c2D)
        #     self.conductance_count_layout.removeWidget(self.fig2)
        #     self.conductance_count_layout.removeWidget(self.toolbar_cc)
        #     self.length_layout.removeWidget(self.fig3)
        #     self.length_layout.removeWidget(self.toolbar_length)
        #     sip.delete(self.fig1)  # sip用来从布局中删除控件
        #     sip.delete(self.toolbar_c2D)
        #     sip.delete(self.fig2)
        #     sip.delete(self.toolbar_cc)
        #     sip.delete(self.fig3)
        #     sip.delete(self.toolbar_length)
        #     print('figure refresh!')
        self.calThread()

    def calThread(self):

        self.start_time = time.perf_counter()
        self.getPanelValue()

        self.showProgressBar(int(0))    # 开始画图前应该去重置进度条

        self._dataThread=QThread()
        self.dataThread=Data_Analysis(self.key_para)  # 计算对象
        self.dataThread.sbar.connect(self.showStatusbarMessage)
        self.dataThread.pbar.connect(self.showProgressBar)
        self.dataThread.tbrow.connect(self.showTextBroswer)
        self.dataThread.run_end.connect(self.stopThread)  # 此信号标志着线程中run函数的结束,再将线程结束

        self.dataThread.moveToThread(self._dataThread)
        self._dataThread.started.connect(self.dataThread.run)
        self._dataThread.finished.connect(self.DrawPre)

        self.startThread()  # 执行计算线程

    def startThread(self):
        #   此处开启线程计算
        if self.key_para['load_file_bool'] :
            if self.key_para['file_path']:
                self._dataThread.start()
                print('开启计算线程，现在线程状态 ：', self._dataThread.isRunning())
        else:
            QMessageBox.warning(self,'Warning','No File!')

    def stopThread(self):
        self._dataThread.quit()
        self._dataThread.wait()
        print('退出计算线程，现在线程状态 ：', self._dataThread.isRunning())
        '''
        quit()函数是用来停止QThread的，但是由于Qt本身是事件循环机制，所以在调用完quit()后，QThread可能还没有完全停止.
        此时如果执行delete channel，程序就会报错。在执行quit()后，调用wait()来等待QThread子线程的结束（即从run()函数的返回），
        这样就能保证在清除QThread时，其子线程是停止运行的。

        '''

    def DrawPre(self):
        # if self.dataThread.isFinished():
        # print(self._dataThread.isRunning())
        print('计算进程安全退出，开始计算绘图数据..........')
        self.data = self.dataThread.data
        self.cut_trigger, self.len_cut_trigger, self.select_index=self.dataThread.cut_trigger,\
                                                                  self.dataThread.len_cut_trigger,self.dataThread.select_index
        # print(self.cut_trigger)
        res=self.checkState(self.cut_trigger)
        if not res:
            return

        self.cal2DConductance()

    def checkState(self,cut_trigger):
        if len(cut_trigger)<=1:
            QMessageBox.warning(self, 'Warning', 'Please select appropriate range of segmentation',QMessageBox.Ok)
            self.Run_btn.setEnabled(True)
            return False
        return True


    def updateAdd(self):
        print('additional length长度改变，重新计算绘图数据.......')
        self.getPanelValue()
        self.cal2DConductance()


    def cal2DConductance(self):
        self._drawDataThread=QThread()
        self.drawDataThread=CalDrawData(self.key_para,self.cut_trigger,self.len_cut_trigger
                                        ,self.select_index,self.data) # 此处是计算绘图所需数据的进程

        self.drawDataThread.run_end.connect(self.stopDrawThread)
        self.drawDataThread.sbar.connect(self.showStatusbarMessage)
        self.drawDataThread.pbar.connect(self.showProgressBar)

        self.drawDataThread.moveToThread(self._drawDataThread)
        self._drawDataThread.started.connect(self.drawDataThread.run)
        self._drawDataThread.finished.connect(self.startDraw)

        self.startDrawThread()

    def startDrawThread(self):
        self._drawDataThread.start()
        # if not self.cut_trigger:
        #     QMessageBox.warning(self,"Warning","Please select appropriate range")
        #     self.cleanData()
        #     self.Run_btn.setEnabled(True)
        #     '''
        #     因为在函数runButton中，所有按钮都变成了不可用状态，这里当选择的切分范围或者是原始数据
        #     有问题的时候，需要重新选择合适的切分范围。
        #     '''
        # else:
        #     self._drawDataThread.start()
        #     print('开启线程计算绘图所需数据，现在线程状态 ：',self._drawDataThread.isRunning())  这里暂时有问题，目前未解决

    def stopDrawThread(self):
        self._drawDataThread.quit()
        self._drawDataThread.wait()
        print('退出绘图所需数据线程，现在线程状态 ：', self._drawDataThread.isRunning())

    def cleanData(self):
        pass

    def startDraw(self):
        self.xx, self.yy, self.ll, self.select_cut_trigger, self.mean_trigger1_len,self.mean_trigger2_len=self.drawDataThread.xx,\
                                                                                                          self.drawDataThread.yy,self.drawDataThread.ll,\
                                                                                                          self.drawDataThread.select_cut_trigger,\
                                                                                                          self.drawDataThread.mean_trigger1_len,\
                                                                                                          self.drawDataThread.mean_trigger2_len

        self.QPB_redraw.setEnabled(True)
        self.Draw()

        self.QPB_save_all.setEnabled(True)
        self.QPB_save_goodtrace.setEnabled(True)
        self.QPB_redraw.setEnabled(True)
        self.QPB_update.setEnabled(True)

        time_used = round((time.perf_counter() - self.start_time), 2)
        print("total time used: ", str(time_used))
        self.textBrowser.append('mean_trigger1_length: ' + str(round(self.mean_trigger1_len, 3)) + ' nm')
        self.textBrowser.append('mean_trigger2_length: ' + str(round(self.mean_trigger2_len, 3)) + ' nm')
        self.textBrowser.append('Data analysis time used: ' + str(time_used) + ' s')

        self.Run_btn.setEnabled(True)


    def Draw(self):
        if self.draw_first:
            self.draw_first = False
        else:
            self.conductance_length_layout.removeWidget(self.fig1)
            self.conductance_length_layout.removeWidget(self.toolbar_c2D)
            self.conductance_count_layout.removeWidget(self.fig2)
            self.conductance_count_layout.removeWidget(self.toolbar_cc)
            self.length_layout.removeWidget(self.fig3)
            self.length_layout.removeWidget(self.toolbar_length)
            sip.delete(self.fig1)  # sip用来从布局中删除控件
            sip.delete(self.toolbar_c2D)
            sip.delete(self.fig2)
            sip.delete(self.toolbar_cc)
            sip.delete(self.fig3)
            sip.delete(self.toolbar_length)
            plt.close('all')# 此句非常重要，matplotlib能够同时管理的figure是有限的，每次重新绘图之前应该对之前创建的figure进行清除，不然内存会占满甚至出现莫名的bug
            print('figure refresh!')

        size = 14
        fontsize = '14'
        cm = plt.cm.coolwarm

        _2D_bins_x = self.key_para['2D_bins_x']
        _2D_bins_y = self.key_para['2D_bins_y']
        _2D_xlim_l = self.key_para['2D_xlim_l']
        _2D_xlim_r = self.key_para['2D_xlim_r']
        _2D_ylim_l = self.key_para['2D_ylim_l']
        _2D_ylim_r = self.key_para['2D_ylim_r']
        _1D_xlim_l = self.key_para['1D_xlim_l']
        _1D_xlim_r = self.key_para['1D_xlim_r']
        _1D_bins = self.key_para['1D_bins']
        _leng_xlim_l = self.key_para['leng_xlim_l']
        _leng_xlim_r = self.key_para['leng_xlim_r']
        _leng_bins = self.key_para['leng_bins']


        trace_n = len(self.cut_trigger)
        select_trace_n = len(self.select_cut_trigger)
        select_ratio = trace_n / select_trace_n * 100
        print('select_ratio : ',select_ratio)
        self.QTB_all_trace.setText(str(trace_n))
        self.QTB_selected_trace.setText(str(select_trace_n))
        self.QTB_ratio.setText(str(round(select_ratio, 2)))
        self.textBrowser.append('Number of individual curves: ' + str(trace_n))
        # print(select_trace_n)

        self.fig1 = Conductance_Figure()
        self.hist_3D,self.x_3D,self.y_3D,image=self.fig1.axes.hist2d(self.xx, self.yy, bins=[_2D_bins_x, _2D_bins_y], range=[[_2D_xlim_l, _2D_xlim_r],
                                                                                      [_2D_ylim_l, _2D_ylim_r]], density=1, vmin=0,vmax=1, cmap=cm)
        self.H_3D,self.x_3Dedges,self.y_3Dedges=np.histogram2d(self.xx,self.yy,bins=[500, 1000],range=[[-0.5, 3],[-10, 1]])
        self.fig1.fig.colorbar(image,pad=0.03,aspect=50)
        self.fig1.cursor = Cursor(self.fig1.axes, useblit=False, color='red', linewidth=1)
        self.fig1.fig.canvas.mpl_connect('motion_notify_event',lambda event:self.fig1.cursor.onmove(event))
        self.fig1.axes.set_xlabel('Length / nm', fontsize=fontsize)
        self.fig1.axes.set_ylabel('Conductance', fontsize=fontsize)
        self.fig1.fig.tight_layout()
        self.toolbar_c2D = MyNavigationToolbar(self.fig1, self.fig1.main_frame)  # 这里需要指定父类
        self.conductance_length_layout.addWidget(self.fig1)
        self.conductance_length_layout.addWidget(self.toolbar_c2D)
        self.Conduct_Length_fig.setLayout(self.conductance_length_layout)

        self.fig2 = Conductance_Figure()
        self.fig2.axes.set_xlabel('Conductance', fontsize=fontsize)
        self.fig2.axes.set_ylabel('Counts', fontsize=fontsize)
        self.fig2.axes.set_xlim((_1D_xlim_l, _1D_xlim_r))
        #self.fig2.axes.set_yticks([])
        self.fig2.axes.grid(True)
        self.count_1D,self.bins_1D,patches=self.fig2.axes.hist(self.yy, bins=_1D_bins, color='green', alpha=0.8,range=[_1D_xlim_l,_1D_xlim_r])
        self.hist_1D,self.bin_edges_1D=np.histogram(self.yy,bins=1100,range=[-10,1])
        ax2=plt.gca()
        ax2.yaxis.get_major_formatter().set_powerlimits((0, 1))

        self.fig2.cursor = Cursor(self.fig2.axes, useblit=False, color='red', linewidth=1)
        self.fig2.fig.canvas.mpl_connect('motion_notify_event',lambda event:self.fig2.cursor.onmove(event))
        self.fig2.fig.tight_layout()
        self.toolbar_cc = MyNavigationToolbar(self.fig2, self.fig2.main_frame)
        self.conductance_count_layout.addWidget(self.fig2)
        self.conductance_count_layout.addWidget(self.toolbar_cc)
        self.Conductance_fig.setLayout(self.conductance_count_layout)

        self.fig3 = Conductance_Figure()
        length_c = np.array(self.ll).reshape(-1)
        mean_ll = np.mean(length_c)
        mu = round(mean_ll, 2)
        sigma = np.std(length_c)
        self.count_len, self.bins_len, patchs = self.fig3.axes.hist(length_c, density=True, bins=_leng_bins,range=[_leng_xlim_l,_leng_xlim_r])
        self.hist_len,self.bin_edges_len=np.histogram(length_c,bins=100,range=[0,3])
        ax3 = plt.gca()
        ax3.yaxis.get_major_formatter().set_powerlimits((0, 1))

        self.fig3.cursor = Cursor(self.fig3.axes, useblit=False, color='red', linewidth=1)
        self.fig3.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.fig3.cursor.onmove(event))
        y = norm.pdf(self.bins_len, mu, sigma)
        self.fig3.axes.set_xlabel('Length / nm', fontsize=fontsize)
        self.fig3.axes.set_ylabel('counts', fontsize=fontsize)
        self.fig3.axes.set_xlim((_leng_xlim_l, _leng_xlim_r))
        #self.fig3.axes.set_yticks([])
        self.fig3.axes.grid(True)
        self.fig3.axes.plot(self.bins_len, y, 'r--', label='length: ' + str(mu))
        self.fig3.axes.legend(loc=1)
        self.fig3.fig.tight_layout()
        self.toolbar_length = MyNavigationToolbar(self.fig3, self.fig3.main_frame)
        self.length_layout.addWidget(self.fig3)
        self.length_layout.addWidget(self.toolbar_length)
        self.Length_fig.setLayout(self.length_layout)

    def reDrawBtn(self):
        reply = QMessageBox.question(self, 'Redraw?', 'Have you updated the parameters and decided to redraw?',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.reDraw()
        elif reply==QMessageBox.No:
            pass

    def reDraw(self):
        if self.key_para['load_file_bool']:
            if self.key_para['file_path']:
                self.getPanelValue()
                self.Draw()
                QMessageBox.information(self, 'Information', 'The graph has been update')
        else:
            QMessageBox.warning(self,'Warning','No File!')


    def resetBtn(self):
        reply = QMessageBox.question(self, 'Reset?', 'Would you like to reset all parameters?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.resetParameter()
        elif reply == QMessageBox.No:
            pass

    def resetParameter(self):
        _translate = QtCore.QCoreApplication.translate
        self.QPT_sampling_rate.setPlainText(_translate("MainWindow", "20000"))
        self.QPT_strecting_rate.setPlainText(_translate("MainWindow", "10"))
        self.QPT_high_cut.setPlainText(_translate("MainWindow", "1.2"))
        self.QPT_low_cut.setPlainText(_translate("MainWindow", "-6.5"))
        self.QPT_high_length.setPlainText(_translate("MainWindow", "-0.3"))
        self.QPT_low_length.setPlainText(_translate("MainWindow", "-6"))
        self.QPT_add_length.setPlainText(_translate("MainWindow", "500"))
        self.QPT_biasV.setPlainText(_translate("MainWindow", "0.1"))
        self.QPT_zero_set.setPlainText(_translate("MainWindow", "-0.3"))


        self.QPT_2D_binsx.setPlainText(_translate("MainWindow", "500"))
        self.QPT_2D_binsy.setPlainText(_translate("MainWindow", "800"))
        self.QPT_2D_xlim_l.setPlainText(_translate("MainWindow", "-0.2"))
        self.QPT_2D_xlim_r.setPlainText(_translate("MainWindow", "2"))
        self.QPT_2D_ylim_l.setPlainText(_translate("MainWindow", "-8"))
        self.QPT_2D_ylim_r.setPlainText(_translate("MainWindow", "1.5"))

        self.QPT_1D_bins.setPlainText(_translate("MainWindow", "800"))
        self.QPT_1D_xlim_l.setPlainText(_translate("MainWindow", "-8"))
        self.QPT_1D_xlim_r.setPlainText(_translate("MainWindow", "1.5"))

        self.QPT_leng_xlim_l.setPlainText(_translate("MainWindow", "0"))
        self.QPT_leng_xlim_r.setPlainText(_translate("MainWindow", "3"))
        self.QPT_leng_bins.setPlainText(_translate("MainWindow", "100"))

        self.QPT_start1.setPlainText(_translate("MainWindow", "-2"))
        self.QPT_end1.setPlainText(_translate("MainWindow", "-3"))
        self.QPT_start2.setPlainText(_translate("MainWindow", "-4"))
        self.QPT_end2.setPlainText(_translate("MainWindow", "-6"))
        self.QPT_lower_limit1.setPlainText(_translate("MainWindow", "-55"))
        self.QPT_upper_limit1.setPlainText(_translate("MainWindow", "55"))
        self.QPT_lower_limit2.setPlainText(_translate("MainWindow", "-55"))
        self.QPT_upper_limit2.setPlainText(_translate("MainWindow", "55"))

        self.QPT_f1_a1.setPlainText(_translate("MainWindow", "-9.1137"))
        self.QPT_f1_b1.setPlainText(_translate("MainWindow", "-27.646"))
        self.QPT_f1_c1.setPlainText(_translate("MainWindow", "-1.1614e-11"))
        self.QPT_f1_d1.setPlainText(_translate("MainWindow", "4.1597e-13"))
        self.QPT_f1_a2.setPlainText(_translate("MainWindow", "9.2183"))
        self.QPT_f1_b2.setPlainText(_translate("MainWindow", "-27.8018"))
        self.QPT_f1_c2.setPlainText(_translate("MainWindow", "-1.18929e-11"))
        self.QPT_f1_d2.setPlainText(_translate("MainWindow", "-1.4714e-13"))
        self.QPT_f1_offset.setPlainText(_translate("MainWindow", "0"))

        self.QPT_f2_a1.setPlainText(_translate("MainWindow", "7.11645"))
        self.QPT_f2_a2.setPlainText(_translate("MainWindow", "12.59542"))
        self.QPT_f2_b1.setPlainText(_translate("MainWindow", "-32.28028"))
        self.QPT_f2_b2.setPlainText(_translate("MainWindow", "-23.00707"))
        self.QPT_f2_c1.setPlainText(_translate("MainWindow", "-1.16402"))
        self.QPT_f2_c2.setPlainText(_translate("MainWindow", "-1.5182"))
        self.QPT_f2_d1.setPlainText(_translate("MainWindow", "4.42553"))
        self.QPT_f2_d2.setPlainText(_translate("MainWindow", "-6.14423"))
        self.QPT_f2_e1.setPlainText(_translate("MainWindow", "0.01091"))
        self.QPT_f2_e2.setPlainText(_translate("MainWindow", "0.2286"))
        self.QPT_f2_f1.setPlainText(_translate("MainWindow", "-1.17779"))
        self.QPT_f2_f2.setPlainText(_translate("MainWindow", "-1.2272"))
        self.QPT_f2_offset.setPlainText(_translate("MainWindow", "0"))

        self.QPT_f3_a1.setPlainText(_translate("MainWindow", "3.1435"))
        self.QPT_f3_b1.setPlainText(_translate("MainWindow", "-14.62"))
        self.QPT_f3_a1.setPlainText(_translate("MainWindow", "-3.1009"))
        self.QPT_f3_b1.setPlainText(_translate("MainWindow", "-14.456"))
        self.QPT_f3_offset.setPlainText(_translate("MainWindow", "0"))

    def saveDataAndFig(self):
        self.zeroPad()
        img_path = self.key_para['img_path']
        self.createDir(img_path)
        self.fig1.fig.savefig(str(img_path) + '/2D_Conductance.png', dpi=100, bbox_inches='tight')
        self.fig2.fig.savefig(str(img_path) + '/Conductance_count.png', dpi=100, bbox_inches='tight')
        self.fig3.fig.savefig(str(img_path) + '/Length_count.png', dpi=100, bbox_inches='tight')

        self.saveData()

        QMessageBox.information(self, 'Information', 'Save figures and data succeed!')
        self.showStatusbarMessage('All figures and data saved !')
        self.showTextBroswer('Save figures and data succeed! ')


    def zeroPad(self):
        _2D_bins_x = 500
        _2D_bins_y = 1000
        pad_num=500
        # if _2D_bins_x<_2D_bins_y:
        #     self.x_3D_new=np.pad(self.x_3D[1:],(0,pad_num),'constant', constant_values=(0))
        #     self.y_3D_new=self.y_3D[1:]
        # else:
        #     self.y_3D_new = np.pad(self.y_3D[1:], (0, pad_num), 'constant', constant_values=(0))
        #     self.x_3D_new = self.x_3D[1:]
        self.x_3D_new = np.pad(self.x_3Dedges[1:], (0, pad_num), 'constant', constant_values=(0))
        self.y_3D_new = self.y_3Dedges[1:]

    # =================保存图像对应的数据======================#
    def saveData(self):
        img_path = self.key_para['img_path']
        data_path = str(img_path)+'_'+'Analysis'
        self.createDir(data_path)

        np.savetxt(str(data_path)+'/WA-BJ_3Dhist.txt',self.H_3D*2,fmt='%d',delimiter='\t')
        hist_3D_scales=np.array([self.x_3D_new,self.y_3D_new]).T
        np.savetxt(str(data_path)+'/WA-BJ_3Dhist_scales.txt',hist_3D_scales,fmt='%.5e',delimiter='\t')
        hist_log=np.array([self.bin_edges_1D[:-1],self.hist_1D]).T
        np.savetxt(str(data_path)+ '/WA-BJ_logHist.txt', hist_log, fmt='%.5e', delimiter='\t')
        hist_plat = np.array([self.bin_edges_len[:-1], self.hist_len]).T
        np.savetxt(str(data_path)+ '/WA-BJ_plateau.txt', hist_plat, fmt='%.5e', delimiter='\t')


    def saveGoodTrace(self):
        img_path = self.key_para['img_path']
        data_path = str(img_path) + '_' + 'Analysis'
        self.createDir(data_path)
        xx=np.array(self.xx)
        yy=np.array(self.yy)
        # temp={'length':xx,'conductance':yy}
        # save_trace=pd.DataFrame(temp)
        GT=np.array([xx,yy]).T
        self.showStatusbarMessage('Start to save to goodtrace ...... ')
        try:
            # save_trace.to_csv(str(img_path) + '/goodtrace.txt',header=0, index = 0,sep='\t')
            np.savetxt(str(data_path)+'/goodtrace.txt',GT,fmt='%.5e',delimiter='\t')
        except Exception as e:
            QMessageBox.warning(self, 'Warning', 'Save to goodtrace failed !')
            self.showStatusbarMessage('Save to goodtrace failed !')
        else:
            QMessageBox.information(self, 'Information', 'Save to goodtrace succeed!')
            self.showStatusbarMessage('Save to goodtrace succeed!')
            self.showTextBroswer('Save to goodtrace succeed! ')

    def createDir(self,path):
        if not os.path.exists(str(path)):
            os.mkdir(str(path))
            print('Folder created ！')
            self.showStatusbarMessage('Create new folder:'+str(path))
        else:
            print('Folder already exist !')
            self.showStatusbarMessage('Folder already exist !')

class MyNavigationToolbar(NavigationToolbar):
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
    )



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = XMewindow()
    ui.show()
    sys.exit(app.exec())