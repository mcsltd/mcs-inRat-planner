# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_inrat_controllernYbDGO.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_DlgInRatController(object):
    def setupUi(self, DlgInRatController):
        if not DlgInRatController.objectName():
            DlgInRatController.setObjectName(u"DlgInRatController")
        DlgInRatController.resize(1005, 568)
        self.verticalLayoutWidget = QWidget(DlgInRatController)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(700, 20, 291, 541))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayoutInfo = QFormLayout()
        self.formLayoutInfo.setObjectName(u"formLayoutInfo")
        self.labelDevice = QLabel(self.verticalLayoutWidget)
        self.labelDevice.setObjectName(u"labelDevice")

        self.formLayoutInfo.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelDevice)

        self.labelDeviceName = QLabel(self.verticalLayoutWidget)
        self.labelDeviceName.setObjectName(u"labelDeviceName")

        self.formLayoutInfo.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelDeviceName)


        self.verticalLayout.addLayout(self.formLayoutInfo)

        self.pushButtonStart = QPushButton(self.verticalLayoutWidget)
        self.pushButtonStart.setObjectName(u"pushButtonStart")

        self.verticalLayout.addWidget(self.pushButtonStart)

        self.pushButtonStop = QPushButton(self.verticalLayoutWidget)
        self.pushButtonStop.setObjectName(u"pushButtonStop")

        self.verticalLayout.addWidget(self.pushButtonStop)

        self.labelSettingDevice = QLabel(self.verticalLayoutWidget)
        self.labelSettingDevice.setObjectName(u"labelSettingDevice")

        self.verticalLayout.addWidget(self.labelSettingDevice)

        self.formLayoutSettings = QFormLayout()
        self.formLayoutSettings.setObjectName(u"formLayoutSettings")
        self.labelSampleFreq = QLabel(self.verticalLayoutWidget)
        self.labelSampleFreq.setObjectName(u"labelSampleFreq")

        self.formLayoutSettings.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelSampleFreq)

        self.comboBoxSampleFreq = QComboBox(self.verticalLayoutWidget)
        self.comboBoxSampleFreq.setObjectName(u"comboBoxSampleFreq")

        self.formLayoutSettings.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBoxSampleFreq)

        self.labelMode = QLabel(self.verticalLayoutWidget)
        self.labelMode.setObjectName(u"labelMode")

        self.formLayoutSettings.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelMode)

        self.comboBoxMode = QComboBox(self.verticalLayoutWidget)
        self.comboBoxMode.setObjectName(u"comboBoxMode")

        self.formLayoutSettings.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBoxMode)


        self.verticalLayout.addLayout(self.formLayoutSettings)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayoutWidget_2 = QWidget(DlgInRatController)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(10, 10, 681, 551))
        self.verticalLayoutPlot = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayoutPlot.setObjectName(u"verticalLayoutPlot")
        self.verticalLayoutPlot.setContentsMargins(0, 0, 0, 0)

        self.retranslateUi(DlgInRatController)

        QMetaObject.connectSlotsByName(DlgInRatController)
    # setupUi

    def retranslateUi(self, DlgInRatController):
        DlgInRatController.setWindowTitle(QCoreApplication.translate("DlgInRatController", u"Dialog", None))
        self.labelDevice.setText(QCoreApplication.translate("DlgInRatController", u"\u0423\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e:", None))
        self.labelDeviceName.setText("")
        self.pushButtonStart.setText(QCoreApplication.translate("DlgInRatController", u"\u0421\u0442\u0430\u0440\u0442", None))
        self.pushButtonStop.setText(QCoreApplication.translate("DlgInRatController", u"\u0421\u0442\u043e\u043f", None))
        self.labelSettingDevice.setText(QCoreApplication.translate("DlgInRatController", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430", None))
        self.labelSampleFreq.setText(QCoreApplication.translate("DlgInRatController", u"l\u0427\u0430\u0441\u0442\u043e\u0442\u0430 \u043e\u0446\u0438\u0444\u0440\u043e\u0432\u043a\u0438:", None))
        self.labelMode.setText(QCoreApplication.translate("DlgInRatController", u"\u0420\u0435\u0436\u0438\u043c", None))
    # retranslateUi

