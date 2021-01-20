# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_main_interface.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(909, 659)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_img = QtWidgets.QVBoxLayout()
        self.verticalLayout_img.setObjectName("verticalLayout_img")
        self.verticalLayout.addLayout(self.verticalLayout_img)
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_3.addWidget(self.label_5)
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_3.addWidget(self.label_8)
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lineEdit_id = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_id.setObjectName("lineEdit_id")
        self.verticalLayout_2.addWidget(self.lineEdit_id)
        self.lineEdit_mode = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_mode.setObjectName("lineEdit_mode")
        self.verticalLayout_2.addWidget(self.lineEdit_mode)
        self.lineEdit_loc = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_loc.setObjectName("lineEdit_loc")
        self.verticalLayout_2.addWidget(self.lineEdit_loc)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        spacerItem = QtWidgets.QSpacerItem(20, 314, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.pbn_del = QtWidgets.QPushButton(self.groupBox_2)
        self.pbn_del.setObjectName("pbn_del")
        self.verticalLayout_4.addWidget(self.pbn_del)
        self.pbn_start = QtWidgets.QPushButton(self.groupBox_2)
        self.pbn_start.setMinimumSize(QtCore.QSize(161, 91))
        self.pbn_start.setObjectName("pbn_start")
        self.verticalLayout_4.addWidget(self.pbn_start)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.horizontalLayout.setStretch(0, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 909, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit_E = QtWidgets.QMenu(self.menubar)
        self.menuEdit_E.setObjectName("menuEdit_E")
        self.menuHelp_H = QtWidgets.QMenu(self.menubar)
        self.menuHelp_H.setObjectName("menuHelp_H")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setCheckable(True)
        self.actionLoad.setObjectName("actionLoad")
        self.actionpreview = QtWidgets.QAction(MainWindow)
        self.actionpreview.setCheckable(True)
        self.actionpreview.setObjectName("actionpreview")
        self.actionshowlog = QtWidgets.QAction(MainWindow)
        self.actionshowlog.setCheckable(True)
        self.actionshowlog.setObjectName("actionshowlog")
        self.actionClearLog = QtWidgets.QAction(MainWindow)
        self.actionClearLog.setObjectName("actionClearLog")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSetting = QtWidgets.QAction(MainWindow)
        self.actionSetting.setObjectName("actionSetting")
        self.menuFile.addAction(self.actionSetting)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit_E.addAction(self.actionpreview)
        self.menuEdit_E.addSeparator()
        self.menuEdit_E.addAction(self.actionshowlog)
        self.menuEdit_E.addAction(self.actionClearLog)
        self.menuHelp_H.addSeparator()
        self.menuHelp_H.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit_E.menuAction())
        self.menubar.addAction(self.menuHelp_H.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Video View"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Action Editor"))
        self.label_5.setText(_translate("MainWindow", "ID"))
        self.label_8.setText(_translate("MainWindow", "攻击类型"))
        self.label_7.setText(_translate("MainWindow", "位置"))
        self.pbn_del.setText(_translate("MainWindow", "删除"))
        self.pbn_start.setText(_translate("MainWindow", "开始"))
        self.pbn_start.setShortcut(_translate("MainWindow", "Space"))
        self.menuFile.setTitle(_translate("MainWindow", "File(&F)"))
        self.menuEdit_E.setTitle(_translate("MainWindow", "Edit(&E)"))
        self.menuHelp_H.setTitle(_translate("MainWindow", "Help(&H)"))
        self.actionExit.setText(_translate("MainWindow", "退出"))
        self.actionLoad.setText(_translate("MainWindow", "加载"))
        self.actionLoad.setShortcut(_translate("MainWindow", "Ctrl+L"))
        self.actionpreview.setText(_translate("MainWindow", "预览"))
        self.actionpreview.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.actionshowlog.setText(_translate("MainWindow", "显示日志"))
        self.actionshowlog.setShortcut(_translate("MainWindow", "Ctrl+G"))
        self.actionClearLog.setText(_translate("MainWindow", "清空日志"))
        self.actionClearLog.setToolTip(_translate("MainWindow", "清除日志"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSetting.setText(_translate("MainWindow", "配置"))
        self.actionSetting.setShortcut(_translate("MainWindow", "Ctrl+Alt+S"))