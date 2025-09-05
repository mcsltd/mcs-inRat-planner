# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowIuywIN.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTableView,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(803, 517)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineSeparateSchedule = QFrame(self.centralwidget)
        self.lineSeparateSchedule.setObjectName(u"lineSeparateSchedule")
        self.lineSeparateSchedule.setFrameShape(QFrame.Shape.VLine)
        self.lineSeparateSchedule.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.lineSeparateSchedule, 0, 1, 1, 1)

        self.verticalLayoutDeviceRat = QVBoxLayout()
        self.verticalLayoutDeviceRat.setObjectName(u"verticalLayoutDeviceRat")
        self.labelDevices = QLabel(self.centralwidget)
        self.labelDevices.setObjectName(u"labelDevices")

        self.verticalLayoutDeviceRat.addWidget(self.labelDevices)

        self.tableViewDevice = QTableView(self.centralwidget)
        self.tableViewDevice.setObjectName(u"tableViewDevice")

        self.verticalLayoutDeviceRat.addWidget(self.tableViewDevice)

        self.horizontalLayoutControlDevice = QHBoxLayout()
        self.horizontalLayoutControlDevice.setObjectName(u"horizontalLayoutControlDevice")
        self.pushButtonAddDevice = QPushButton(self.centralwidget)
        self.pushButtonAddDevice.setObjectName(u"pushButtonAddDevice")

        self.horizontalLayoutControlDevice.addWidget(self.pushButtonAddDevice)

        self.pushButtonDeleteDevice = QPushButton(self.centralwidget)
        self.pushButtonDeleteDevice.setObjectName(u"pushButtonDeleteDevice")

        self.horizontalLayoutControlDevice.addWidget(self.pushButtonDeleteDevice)


        self.verticalLayoutDeviceRat.addLayout(self.horizontalLayoutControlDevice)

        self.verticalLayoutRat = QVBoxLayout()
        self.verticalLayoutRat.setObjectName(u"verticalLayoutRat")
        self.labelRat = QLabel(self.centralwidget)
        self.labelRat.setObjectName(u"labelRat")

        self.verticalLayoutRat.addWidget(self.labelRat)

        self.tableViewRat = QTableView(self.centralwidget)
        self.tableViewRat.setObjectName(u"tableViewRat")

        self.verticalLayoutRat.addWidget(self.tableViewRat)

        self.horizontalLayoutControlRat = QHBoxLayout()
        self.horizontalLayoutControlRat.setObjectName(u"horizontalLayoutControlRat")
        self.pushButtonAddRat = QPushButton(self.centralwidget)
        self.pushButtonAddRat.setObjectName(u"pushButtonAddRat")

        self.horizontalLayoutControlRat.addWidget(self.pushButtonAddRat)

        self.pushButtonDeleteRat = QPushButton(self.centralwidget)
        self.pushButtonDeleteRat.setObjectName(u"pushButtonDeleteRat")

        self.horizontalLayoutControlRat.addWidget(self.pushButtonDeleteRat)


        self.verticalLayoutRat.addLayout(self.horizontalLayoutControlRat)


        self.verticalLayoutDeviceRat.addLayout(self.verticalLayoutRat)


        self.gridLayout.addLayout(self.verticalLayoutDeviceRat, 0, 3, 1, 1)

        self.verticalLayoutSchedule = QVBoxLayout()
        self.verticalLayoutSchedule.setObjectName(u"verticalLayoutSchedule")
        self.tableViewSchedule = QTableView(self.centralwidget)
        self.tableViewSchedule.setObjectName(u"tableViewSchedule")

        self.verticalLayoutSchedule.addWidget(self.tableViewSchedule)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButtonCreateTask = QPushButton(self.centralwidget)
        self.pushButtonCreateTask.setObjectName(u"pushButtonCreateTask")

        self.horizontalLayout_2.addWidget(self.pushButtonCreateTask)


        self.verticalLayoutSchedule.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.verticalLayoutSchedule, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 803, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.labelDevices.setText(QCoreApplication.translate("MainWindow", u"Devices", None))
        self.pushButtonAddDevice.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.pushButtonDeleteDevice.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.labelRat.setText(QCoreApplication.translate("MainWindow", u"Rats", None))
        self.pushButtonAddRat.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.pushButtonDeleteRat.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButtonCreateTask.setText(QCoreApplication.translate("MainWindow", u"Create", None))
    # retranslateUi

