# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_inrat_controllerqQUSRU.ui'
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
    QGridLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
import resources.resources_rc

class Ui_DlgInRatController(object):
    def setupUi(self, DlgInRatController):
        if not DlgInRatController.objectName():
            DlgInRatController.setObjectName(u"DlgInRatController")
        DlgInRatController.resize(1164, 586)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DlgInRatController.setWindowIcon(icon)
        self.gridLayout = QGridLayout(DlgInRatController)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutPlot = QVBoxLayout()
        self.verticalLayoutPlot.setObjectName(u"verticalLayoutPlot")

        self.gridLayout.addLayout(self.verticalLayoutPlot, 0, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayoutInfo = QFormLayout()
        self.formLayoutInfo.setObjectName(u"formLayoutInfo")
        self.labelExperiment = QLabel(DlgInRatController)
        self.labelExperiment.setObjectName(u"labelExperiment")

        self.formLayoutInfo.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelExperiment)

        self.labelExperimentName = QLabel(DlgInRatController)
        self.labelExperimentName.setObjectName(u"labelExperimentName")

        self.formLayoutInfo.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelExperimentName)

        self.labelDevice = QLabel(DlgInRatController)
        self.labelDevice.setObjectName(u"labelDevice")
        self.labelDevice.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayoutInfo.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelDevice)

        self.labelDeviceName = QLabel(DlgInRatController)
        self.labelDeviceName.setObjectName(u"labelDeviceName")

        self.formLayoutInfo.setWidget(2, QFormLayout.ItemRole.FieldRole, self.labelDeviceName)

        self.labelObject = QLabel(DlgInRatController)
        self.labelObject.setObjectName(u"labelObject")

        self.formLayoutInfo.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelObject)

        self.labelObjectName = QLabel(DlgInRatController)
        self.labelObjectName.setObjectName(u"labelObjectName")

        self.formLayoutInfo.setWidget(1, QFormLayout.ItemRole.FieldRole, self.labelObjectName)

        self.labelBatteryLevel = QLabel(DlgInRatController)
        self.labelBatteryLevel.setObjectName(u"labelBatteryLevel")

        self.formLayoutInfo.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelBatteryLevel)

        self.progressBarLevel = QProgressBar(DlgInRatController)
        self.progressBarLevel.setObjectName(u"progressBarLevel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBarLevel.sizePolicy().hasHeightForWidth())
        self.progressBarLevel.setSizePolicy(sizePolicy)
        self.progressBarLevel.setValue(0)

        self.formLayoutInfo.setWidget(3, QFormLayout.ItemRole.FieldRole, self.progressBarLevel)


        self.verticalLayout.addLayout(self.formLayoutInfo)

        self.gridLayoutControlPanel = QGridLayout()
        self.gridLayoutControlPanel.setObjectName(u"gridLayoutControlPanel")
        self.pushButtonStart = QPushButton(DlgInRatController)
        self.pushButtonStart.setObjectName(u"pushButtonStart")
        self.pushButtonStart.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButtonStart.sizePolicy().hasHeightForWidth())
        self.pushButtonStart.setSizePolicy(sizePolicy1)
        self.pushButtonStart.setMinimumSize(QSize(100, 0))

        self.gridLayoutControlPanel.addWidget(self.pushButtonStart, 0, 1, 1, 1)

        self.pushButtonConnection = QPushButton(DlgInRatController)
        self.pushButtonConnection.setObjectName(u"pushButtonConnection")

        self.gridLayoutControlPanel.addWidget(self.pushButtonConnection, 0, 0, 1, 1)

        self.pushButtonDisconnect = QPushButton(DlgInRatController)
        self.pushButtonDisconnect.setObjectName(u"pushButtonDisconnect")
        self.pushButtonDisconnect.setEnabled(False)

        self.gridLayoutControlPanel.addWidget(self.pushButtonDisconnect, 1, 0, 1, 1)

        self.pushButtonStop = QPushButton(DlgInRatController)
        self.pushButtonStop.setObjectName(u"pushButtonStop")
        self.pushButtonStop.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pushButtonStop.sizePolicy().hasHeightForWidth())
        self.pushButtonStop.setSizePolicy(sizePolicy1)
        self.pushButtonStop.setMinimumSize(QSize(100, 0))

        self.gridLayoutControlPanel.addWidget(self.pushButtonStop, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayoutControlPanel)

        self.labelSettingDevice = QLabel(DlgInRatController)
        self.labelSettingDevice.setObjectName(u"labelSettingDevice")
        self.labelSettingDevice.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelSettingDevice)

        self.formLayoutSettings = QFormLayout()
        self.formLayoutSettings.setObjectName(u"formLayoutSettings")
        self.labelSampleFreq = QLabel(DlgInRatController)
        self.labelSampleFreq.setObjectName(u"labelSampleFreq")

        self.formLayoutSettings.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelSampleFreq)

        self.comboBoxSampleFreq = QComboBox(DlgInRatController)
        self.comboBoxSampleFreq.setObjectName(u"comboBoxSampleFreq")
        self.comboBoxSampleFreq.setEnabled(False)

        self.formLayoutSettings.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBoxSampleFreq)

        self.labelMode = QLabel(DlgInRatController)
        self.labelMode.setObjectName(u"labelMode")

        self.formLayoutSettings.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelMode)

        self.comboBoxMode = QComboBox(DlgInRatController)
        self.comboBoxMode.setObjectName(u"comboBoxMode")
        self.comboBoxMode.setEnabled(False)

        self.formLayoutSettings.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBoxMode)


        self.verticalLayout.addLayout(self.formLayoutSettings)

        self.labelStorage = QLabel(DlgInRatController)
        self.labelStorage.setObjectName(u"labelStorage")
        self.labelStorage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelStorage)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.comboBoxFormat = QComboBox(DlgInRatController)
        self.comboBoxFormat.addItem("")
        self.comboBoxFormat.addItem("")
        self.comboBoxFormat.setObjectName(u"comboBoxFormat")
        self.comboBoxFormat.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBoxFormat.sizePolicy().hasHeightForWidth())
        self.comboBoxFormat.setSizePolicy(sizePolicy2)
        self.comboBoxFormat.setMaximumSize(QSize(100, 16777215))
        font = QFont()
        font.setPointSize(9)
        self.comboBoxFormat.setFont(font)
        self.comboBoxFormat.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow)

        self.gridLayout_7.addWidget(self.comboBoxFormat, 1, 1, 1, 1)

        self.labelRT = QLabel(DlgInRatController)
        self.labelRT.setObjectName(u"labelRT")
        self.labelRT.setFont(font)
        self.labelRT.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_7.addWidget(self.labelRT, 2, 0, 1, 1)

        self.labelFormat = QLabel(DlgInRatController)
        self.labelFormat.setObjectName(u"labelFormat")
        self.labelFormat.setFont(font)
        self.labelFormat.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_7.addWidget(self.labelFormat, 1, 0, 1, 1)

        self.labelRTvalue = QLabel(DlgInRatController)
        self.labelRTvalue.setObjectName(u"labelRTvalue")
        self.labelRTvalue.setFont(font)
        self.labelRTvalue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_7.addWidget(self.labelRTvalue, 2, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_7)

        self.horizontalLayoutRecording = QHBoxLayout()
        self.horizontalLayoutRecording.setObjectName(u"horizontalLayoutRecording")
        self.pushButtonStartRecording = QPushButton(DlgInRatController)
        self.pushButtonStartRecording.setObjectName(u"pushButtonStartRecording")
        self.pushButtonStartRecording.setEnabled(False)

        self.horizontalLayoutRecording.addWidget(self.pushButtonStartRecording)

        self.pushButtonStopRecording = QPushButton(DlgInRatController)
        self.pushButtonStopRecording.setObjectName(u"pushButtonStopRecording")
        self.pushButtonStopRecording.setEnabled(False)

        self.horizontalLayoutRecording.addWidget(self.pushButtonStopRecording)


        self.verticalLayout.addLayout(self.horizontalLayoutRecording)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)


        self.retranslateUi(DlgInRatController)

        QMetaObject.connectSlotsByName(DlgInRatController)
    # setupUi

    def retranslateUi(self, DlgInRatController):
        DlgInRatController.setWindowTitle(QCoreApplication.translate("DlgInRatController", u"Dialog", None))
        self.labelExperiment.setText(QCoreApplication.translate("DlgInRatController", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442:", None))
        self.labelExperimentName.setText("")
        self.labelDevice.setText(QCoreApplication.translate("DlgInRatController", u"\u0423\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e:", None))
        self.labelDeviceName.setText("")
        self.labelObject.setText(QCoreApplication.translate("DlgInRatController", u"\u041e\u0431\u044a\u0435\u043a\u0442:", None))
        self.labelObjectName.setText("")
        self.labelBatteryLevel.setText(QCoreApplication.translate("DlgInRatController", u"\u0417\u0430\u0440\u044f\u0434 \u0431\u0430\u0442\u0430\u0440\u0435\u0438:", None))
        self.pushButtonStart.setText(QCoreApplication.translate("DlgInRatController", u"\u0421\u0442\u0430\u0440\u0442", None))
        self.pushButtonConnection.setText(QCoreApplication.translate("DlgInRatController", u"\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c", None))
        self.pushButtonDisconnect.setText(QCoreApplication.translate("DlgInRatController", u"\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c", None))
        self.pushButtonStop.setText(QCoreApplication.translate("DlgInRatController", u"\u0421\u0442\u043e\u043f", None))
        self.labelSettingDevice.setText(QCoreApplication.translate("DlgInRatController", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438:", None))
        self.labelSampleFreq.setText(QCoreApplication.translate("DlgInRatController", u"\u0427\u0430\u0441\u0442\u043e\u0442\u0430 \u043e\u0446\u0438\u0444\u0440\u043e\u0432\u043a\u0438:", None))
        self.labelMode.setText(QCoreApplication.translate("DlgInRatController", u"\u0421\u0442\u0430\u0442\u0443\u0441:", None))
        self.labelStorage.setText(QCoreApplication.translate("DlgInRatController", u"\u0417\u0430\u043f\u0438\u0441\u044c \u0441\u0438\u0433\u043d\u0430\u043b\u0430:", None))
        self.comboBoxFormat.setItemText(0, QCoreApplication.translate("DlgInRatController", u"WFDB", None))
        self.comboBoxFormat.setItemText(1, QCoreApplication.translate("DlgInRatController", u"EDF", None))

        self.labelRT.setText(QCoreApplication.translate("DlgInRatController", u"\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0438\u0441\u0438:", None))
        self.labelFormat.setText(QCoreApplication.translate("DlgInRatController", u"\u0424\u043e\u0440\u043c\u0430\u0442:", None))
        self.labelRTvalue.setText(QCoreApplication.translate("DlgInRatController", u"00:00:00", None))
        self.pushButtonStartRecording.setText(QCoreApplication.translate("DlgInRatController", u"\u041d\u0430\u0447\u0430\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u044c", None))
        self.pushButtonStopRecording.setText(QCoreApplication.translate("DlgInRatController", u"\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u044c", None))
    # retranslateUi

