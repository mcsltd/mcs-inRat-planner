# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowRBTWJZ.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(815, 576)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        MainWindow.setFont(font)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionLicenses = QAction(MainWindow)
        self.actionLicenses.setObjectName(u"actionLicenses")
        self.actionExperiments = QAction(MainWindow)
        self.actionExperiments.setObjectName(u"actionExperiments")
        self.actionDEBUGActiveSchedule = QAction(MainWindow)
        self.actionDEBUGActiveSchedule.setObjectName(u"actionDEBUGActiveSchedule")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutHistory = QVBoxLayout()
        self.verticalLayoutHistory.setObjectName(u"verticalLayoutHistory")
        self.horizontalLayoutShowRecords = QHBoxLayout()
        self.horizontalLayoutShowRecords.setObjectName(u"horizontalLayoutShowRecords")
        self.labelHistory = QLabel(self.centralwidget)
        self.labelHistory.setObjectName(u"labelHistory")
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(11)
        self.labelHistory.setFont(font1)

        self.horizontalLayoutShowRecords.addWidget(self.labelHistory)

        self.horizontalSpacerDownloadRecords = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutShowRecords.addItem(self.horizontalSpacerDownloadRecords)

        self.pushButtonDownloadRecords = QPushButton(self.centralwidget)
        self.pushButtonDownloadRecords.setObjectName(u"pushButtonDownloadRecords")
        self.pushButtonDownloadRecords.setFont(font1)

        self.horizontalLayoutShowRecords.addWidget(self.pushButtonDownloadRecords)


        self.verticalLayoutHistory.addLayout(self.horizontalLayoutShowRecords)


        self.gridLayout.addLayout(self.verticalLayoutHistory, 1, 0, 1, 1)

        self.verticalLayoutSchedule = QVBoxLayout()
        self.verticalLayoutSchedule.setObjectName(u"verticalLayoutSchedule")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelSchedule = QLabel(self.centralwidget)
        self.labelSchedule.setObjectName(u"labelSchedule")
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


        self.gridLayout.addLayout(self.verticalLayoutSchedule, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 815, 22))
        self.file = QMenu(self.menubar)
        self.file.setObjectName(u"file")
        self.help = QMenu(self.menubar)
        self.help.setObjectName(u"help")
        self.manage = QMenu(self.menubar)
        self.manage.setObjectName(u"manage")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.file.menuAction())
        self.menubar.addAction(self.manage.menuAction())
        self.menubar.addAction(self.help.menuAction())
        self.file.addAction(self.actionSettings)
        self.file.addSeparator()
        self.file.addAction(self.actionExit)
        self.help.addAction(self.actionDEBUGActiveSchedule)
        self.help.addAction(self.actionLicenses)
        self.help.addAction(self.actionAbout)
        self.manage.addAction(self.actionExperiments)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"InRat Planner", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0445\u043e\u0434", None))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"\u041e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0435...", None))
        self.actionLicenses.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0432\u0435\u0434\u0435\u043d\u0438\u044f \u043e \u043b\u0438\u0446\u0435\u043d\u0437\u0438\u044f\u0445", None))
        self.actionExperiments.setText(QCoreApplication.translate("MainWindow", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u044b", None))
        self.actionDEBUGActiveSchedule.setText(QCoreApplication.translate("MainWindow", u"DEBUG: \u043a\u043e\u043b-\u0432\u043e \u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0445 \u0437\u0430\u0434\u0430\u0447", None))
        self.labelHistory.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0440\u0445\u0438\u0432 \u0437\u0430\u043f\u0438\u0441\u0435\u0439", None))
        self.pushButtonDownloadRecords.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0433\u0440\u0443\u0437\u0438\u0442\u044c", None))
        self.labelSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None))
        self.pushButtonAddSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.pushButtonUpdateSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.pushButtonDeleteSchedule.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0440\u0445\u0438\u0432\u0438\u0440\u043e\u0432\u0430\u0442\u044c", None))
        self.file.setTitle(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u0439\u043b", None))
        self.help.setTitle(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043c\u043e\u0449\u044c", None))
        self.manage.setTitle(QCoreApplication.translate("MainWindow", u"\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435", None))
    # retranslateUi

