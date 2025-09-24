# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowLRROLd.ui'
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
    QLabel, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(827, 607)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutSchedule = QVBoxLayout()
        self.verticalLayoutSchedule.setObjectName(u"verticalLayoutSchedule")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelSchedule = QLabel(self.centralwidget)
        self.labelSchedule.setObjectName(u"labelSchedule")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(11)
        self.labelSchedule.setFont(font1)

        self.horizontalLayout_2.addWidget(self.labelSchedule)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButtonAddSchedule = QPushButton(self.centralwidget)
        self.pushButtonAddSchedule.setObjectName(u"pushButtonAddSchedule")
        self.pushButtonAddSchedule.setFont(font1)

        self.horizontalLayout_2.addWidget(self.pushButtonAddSchedule)

        self.pushButtonUpdateSchedule = QPushButton(self.centralwidget)
        self.pushButtonUpdateSchedule.setObjectName(u"pushButtonUpdateSchedule")
        self.pushButtonUpdateSchedule.setFont(font1)

        self.horizontalLayout_2.addWidget(self.pushButtonUpdateSchedule)

        self.pushButtonDeleteSchedule = QPushButton(self.centralwidget)
        self.pushButtonDeleteSchedule.setObjectName(u"pushButtonDeleteSchedule")
        self.pushButtonDeleteSchedule.setFont(font1)

        self.horizontalLayout_2.addWidget(self.pushButtonDeleteSchedule)


        self.verticalLayoutSchedule.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.verticalLayoutSchedule, 2, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButtonAddExperiment = QPushButton(self.centralwidget)
        self.pushButtonAddExperiment.setObjectName(u"pushButtonAddExperiment")
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        self.pushButtonAddExperiment.setFont(font2)

        self.horizontalLayout.addWidget(self.pushButtonAddExperiment)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.verticalLayoutHistory = QVBoxLayout()
        self.verticalLayoutHistory.setObjectName(u"verticalLayoutHistory")
        self.horizontalLayoutShowRecords = QHBoxLayout()
        self.horizontalLayoutShowRecords.setObjectName(u"horizontalLayoutShowRecords")
        self.labelHistory = QLabel(self.centralwidget)
        self.labelHistory.setObjectName(u"labelHistory")
        self.labelHistory.setFont(font1)

        self.horizontalLayoutShowRecords.addWidget(self.labelHistory)

        self.horizontalSpacerDownloadRecords = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutShowRecords.addItem(self.horizontalSpacerDownloadRecords)

        self.pushButtonDownloadRecords = QPushButton(self.centralwidget)
        self.pushButtonDownloadRecords.setObjectName(u"pushButtonDownloadRecords")
        self.pushButtonDownloadRecords.setFont(font1)

        self.horizontalLayoutShowRecords.addWidget(self.pushButtonDownloadRecords)


        self.verticalLayoutHistory.addLayout(self.horizontalLayoutShowRecords)


        self.gridLayout.addLayout(self.verticalLayoutHistory, 3, 0, 1, 1)

        self.lineSeparate = QFrame(self.centralwidget)
        self.lineSeparate.setObjectName(u"lineSeparate")
        self.lineSeparate.setFrameShape(QFrame.Shape.HLine)
        self.lineSeparate.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.lineSeparate, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 827, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"InRat Planner", None))
        self.labelSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None))
        self.pushButtonAddSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.pushButtonUpdateSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.pushButtonDeleteSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.pushButtonAddExperiment.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c\n"
" \u044d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442", None))
        self.labelHistory.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0441\u0442\u043e\u0440\u0438\u044f", None))
        self.pushButtonDownloadRecords.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043a\u0430\u0447\u0430\u0442\u044c", None))
    # retranslateUi

