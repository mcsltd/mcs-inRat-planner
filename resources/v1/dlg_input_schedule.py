# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_input_scheduleqsuXWk.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateTimeEdit, QDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_DlgCreateNewSchedule(object):
    def setupUi(self, DlgCreateNewSchedule):
        if not DlgCreateNewSchedule.objectName():
            DlgCreateNewSchedule.setObjectName(u"DlgCreateNewSchedule")
        DlgCreateNewSchedule.setWindowModality(Qt.WindowModality.ApplicationModal)
        DlgCreateNewSchedule.resize(492, 537)
        DlgCreateNewSchedule.setAutoFillBackground(False)
        DlgCreateNewSchedule.setInputMethodHints(Qt.InputMethodHint.ImhUrlCharactersOnly)
        DlgCreateNewSchedule.setSizeGripEnabled(False)
        self.groupBoxRecords = QGroupBox(DlgCreateNewSchedule)
        self.groupBoxRecords.setObjectName(u"groupBoxRecords")
        self.groupBoxRecords.setGeometry(QRect(20, 290, 451, 191))
        self.formLayoutWidget_2 = QWidget(self.groupBoxRecords)
        self.formLayoutWidget_2.setObjectName(u"formLayoutWidget_2")
        self.formLayoutWidget_2.setGeometry(QRect(10, 30, 431, 116))
        self.formLayoutRecords = QFormLayout(self.formLayoutWidget_2)
        self.formLayoutRecords.setObjectName(u"formLayoutRecords")
        self.formLayoutRecords.setContentsMargins(0, 0, 0, 0)
        self.labelIntervalRecord = QLabel(self.formLayoutWidget_2)
        self.labelIntervalRecord.setObjectName(u"labelIntervalRecord")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelIntervalRecord.sizePolicy().hasHeightForWidth())
        self.labelIntervalRecord.setSizePolicy(sizePolicy)
        self.labelIntervalRecord.setMinimumSize(QSize(170, 0))

        self.formLayoutRecords.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelIntervalRecord)

        self.comboBoxInterval = QComboBox(self.formLayoutWidget_2)
        self.comboBoxInterval.setObjectName(u"comboBoxInterval")

        self.formLayoutRecords.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBoxInterval)

        self.labelDuration = QLabel(self.formLayoutWidget_2)
        self.labelDuration.setObjectName(u"labelDuration")
        sizePolicy.setHeightForWidth(self.labelDuration.sizePolicy().hasHeightForWidth())
        self.labelDuration.setSizePolicy(sizePolicy)
        self.labelDuration.setMinimumSize(QSize(170, 0))

        self.formLayoutRecords.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDuration)

        self.comboBoxDuration = QComboBox(self.formLayoutWidget_2)
        self.comboBoxDuration.setObjectName(u"comboBoxDuration")

        self.formLayoutRecords.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBoxDuration)

        self.labelSamplingRate = QLabel(self.formLayoutWidget_2)
        self.labelSamplingRate.setObjectName(u"labelSamplingRate")
        sizePolicy.setHeightForWidth(self.labelSamplingRate.sizePolicy().hasHeightForWidth())
        self.labelSamplingRate.setSizePolicy(sizePolicy)
        self.labelSamplingRate.setMinimumSize(QSize(170, 0))

        self.formLayoutRecords.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSamplingRate)

        self.comboBoxSamplingRate = QComboBox(self.formLayoutWidget_2)
        self.comboBoxSamplingRate.setObjectName(u"comboBoxSamplingRate")

        self.formLayoutRecords.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBoxSamplingRate)

        self.labelFormat = QLabel(self.formLayoutWidget_2)
        self.labelFormat.setObjectName(u"labelFormat")
        sizePolicy.setHeightForWidth(self.labelFormat.sizePolicy().hasHeightForWidth())
        self.labelFormat.setSizePolicy(sizePolicy)
        self.labelFormat.setMinimumSize(QSize(170, 0))

        self.formLayoutRecords.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelFormat)

        self.comboBoxFormat = QComboBox(self.formLayoutWidget_2)
        self.comboBoxFormat.setObjectName(u"comboBoxFormat")

        self.formLayoutRecords.setWidget(3, QFormLayout.ItemRole.FieldRole, self.comboBoxFormat)

        self.pushButtonByDefault = QPushButton(self.groupBoxRecords)
        self.pushButtonByDefault.setObjectName(u"pushButtonByDefault")
        self.pushButtonByDefault.setGeometry(QRect(10, 150, 100, 24))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButtonByDefault.sizePolicy().hasHeightForWidth())
        self.pushButtonByDefault.setSizePolicy(sizePolicy1)
        self.pushButtonByDefault.setMinimumSize(QSize(100, 0))
        self.pushButtonByDefault.setMaximumSize(QSize(100, 16777215))
        self.groupBoxSchedule = QGroupBox(DlgCreateNewSchedule)
        self.groupBoxSchedule.setObjectName(u"groupBoxSchedule")
        self.groupBoxSchedule.setGeometry(QRect(20, 150, 451, 131))
        self.formLayoutWidget_3 = QWidget(self.groupBoxSchedule)
        self.formLayoutWidget_3.setObjectName(u"formLayoutWidget_3")
        self.formLayoutWidget_3.setGeometry(QRect(10, 30, 431, 51))
        self.formLayoutSchedule = QFormLayout(self.formLayoutWidget_3)
        self.formLayoutSchedule.setObjectName(u"formLayoutSchedule")
        self.formLayoutSchedule.setContentsMargins(0, 0, 0, 0)
        self.labelStarTime = QLabel(self.formLayoutWidget_3)
        self.labelStarTime.setObjectName(u"labelStarTime")
        sizePolicy.setHeightForWidth(self.labelStarTime.sizePolicy().hasHeightForWidth())
        self.labelStarTime.setSizePolicy(sizePolicy)
        self.labelStarTime.setMinimumSize(QSize(170, 0))

        self.formLayoutSchedule.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelStarTime)

        self.dateTimeEditStartExperiment = QDateTimeEdit(self.formLayoutWidget_3)
        self.dateTimeEditStartExperiment.setObjectName(u"dateTimeEditStartExperiment")

        self.formLayoutSchedule.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dateTimeEditStartExperiment)

        self.labeFinishTime = QLabel(self.formLayoutWidget_3)
        self.labeFinishTime.setObjectName(u"labeFinishTime")
        sizePolicy.setHeightForWidth(self.labeFinishTime.sizePolicy().hasHeightForWidth())
        self.labeFinishTime.setSizePolicy(sizePolicy)
        self.labeFinishTime.setMinimumSize(QSize(170, 0))

        self.formLayoutSchedule.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labeFinishTime)

        self.dateTimeEditFinishExperiment = QDateTimeEdit(self.formLayoutWidget_3)
        self.dateTimeEditFinishExperiment.setObjectName(u"dateTimeEditFinishExperiment")

        self.formLayoutSchedule.setWidget(1, QFormLayout.ItemRole.FieldRole, self.dateTimeEditFinishExperiment)

        self.pushButtonResetTime = QPushButton(self.groupBoxSchedule)
        self.pushButtonResetTime.setObjectName(u"pushButtonResetTime")
        self.pushButtonResetTime.setGeometry(QRect(10, 90, 100, 24))
        sizePolicy1.setHeightForWidth(self.pushButtonResetTime.sizePolicy().hasHeightForWidth())
        self.pushButtonResetTime.setSizePolicy(sizePolicy1)
        self.pushButtonResetTime.setMinimumSize(QSize(100, 0))
        self.pushButtonResetTime.setMaximumSize(QSize(100, 16777215))
        self.formLayoutWidget = QWidget(DlgCreateNewSchedule)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(30, 30, 441, 115))
        self.formLayoutInformation = QFormLayout(self.formLayoutWidget)
        self.formLayoutInformation.setObjectName(u"formLayoutInformation")
        self.formLayoutInformation.setContentsMargins(0, 0, 0, 0)
        self.LabelExperiment = QLabel(self.formLayoutWidget)
        self.LabelExperiment.setObjectName(u"LabelExperiment")
        sizePolicy.setHeightForWidth(self.LabelExperiment.sizePolicy().hasHeightForWidth())
        self.LabelExperiment.setSizePolicy(sizePolicy)
        self.LabelExperiment.setMinimumSize(QSize(170, 0))

        self.formLayoutInformation.setWidget(0, QFormLayout.ItemRole.LabelRole, self.LabelExperiment)

        self.LabelObject = QLabel(self.formLayoutWidget)
        self.LabelObject.setObjectName(u"LabelObject")
        sizePolicy.setHeightForWidth(self.LabelObject.sizePolicy().hasHeightForWidth())
        self.LabelObject.setSizePolicy(sizePolicy)
        self.LabelObject.setMinimumSize(QSize(170, 0))

        self.formLayoutInformation.setWidget(1, QFormLayout.ItemRole.LabelRole, self.LabelObject)

        self.LineEditObject = QLineEdit(self.formLayoutWidget)
        self.LineEditObject.setObjectName(u"LineEditObject")

        self.formLayoutInformation.setWidget(1, QFormLayout.ItemRole.FieldRole, self.LineEditObject)

        self.LabelModelDevice = QLabel(self.formLayoutWidget)
        self.LabelModelDevice.setObjectName(u"LabelModelDevice")
        sizePolicy.setHeightForWidth(self.LabelModelDevice.sizePolicy().hasHeightForWidth())
        self.LabelModelDevice.setSizePolicy(sizePolicy)
        self.LabelModelDevice.setMinimumSize(QSize(170, 0))

        self.formLayoutInformation.setWidget(2, QFormLayout.ItemRole.LabelRole, self.LabelModelDevice)

        self.comboBoxModelDevice = QComboBox(self.formLayoutWidget)
        self.comboBoxModelDevice.setObjectName(u"comboBoxModelDevice")

        self.formLayoutInformation.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBoxModelDevice)

        self.LineEditSnDevice = QLineEdit(self.formLayoutWidget)
        self.LineEditSnDevice.setObjectName(u"LineEditSnDevice")

        self.formLayoutInformation.setWidget(3, QFormLayout.ItemRole.FieldRole, self.LineEditSnDevice)

        self.LabelSnDevice = QLabel(self.formLayoutWidget)
        self.LabelSnDevice.setObjectName(u"LabelSnDevice")
        sizePolicy.setHeightForWidth(self.LabelSnDevice.sizePolicy().hasHeightForWidth())
        self.LabelSnDevice.setSizePolicy(sizePolicy)
        self.LabelSnDevice.setMinimumSize(QSize(170, 0))

        self.formLayoutInformation.setWidget(3, QFormLayout.ItemRole.LabelRole, self.LabelSnDevice)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBoxExperiment = QComboBox(self.formLayoutWidget)
        self.comboBoxExperiment.setObjectName(u"comboBoxExperiment")
        self.comboBoxExperiment.setEnabled(True)
        self.comboBoxExperiment.setEditable(False)

        self.horizontalLayout.addWidget(self.comboBoxExperiment)

        self.pushButtonAddExperiment = QPushButton(self.formLayoutWidget)
        self.pushButtonAddExperiment.setObjectName(u"pushButtonAddExperiment")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButtonAddExperiment.sizePolicy().hasHeightForWidth())
        self.pushButtonAddExperiment.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.pushButtonAddExperiment)


        self.formLayoutInformation.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.horizontalLayoutWidget = QWidget(DlgCreateNewSchedule)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(30, 490, 431, 31))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButtonOk = QPushButton(self.horizontalLayoutWidget)
        self.pushButtonOk.setObjectName(u"pushButtonOk")

        self.horizontalLayout_2.addWidget(self.pushButtonOk)

        self.pushButtonCancel = QPushButton(self.horizontalLayoutWidget)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.horizontalLayout_2.addWidget(self.pushButtonCancel)


        self.retranslateUi(DlgCreateNewSchedule)

        QMetaObject.connectSlotsByName(DlgCreateNewSchedule)
    # setupUi

    def retranslateUi(self, DlgCreateNewSchedule):
        DlgCreateNewSchedule.setWindowTitle(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044f", None))
        self.groupBoxRecords.setTitle(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0437\u0430\u043f\u0438\u0441\u0438", None))
        self.labelIntervalRecord.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041f\u0435\u0440\u0438\u043e\u0434\u0438\u0447\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u0438", None))
        self.labelDuration.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u0438", None))
        self.labelSamplingRate.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0427\u0430\u0441\u0442\u043e\u0442\u0430 \u043e\u0446\u0438\u0444\u0440\u043e\u0432\u043a\u0438", None))
        self.labelFormat.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0424\u043e\u0440\u043c\u0430\u0442", None))
        self.pushButtonByDefault.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e", None))
        self.groupBoxSchedule.setTitle(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0420\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None))
        self.labelStarTime.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430", None))
        self.labeFinishTime.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f", None))
        self.pushButtonResetTime.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c \u0432\u0440\u0435\u043c\u044f", None))
        self.LabelExperiment.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442", None))
        self.LabelObject.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041e\u0431\u044a\u0435\u043a\u0442", None))
        self.LabelModelDevice.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041c\u043e\u0434\u0435\u043b\u044c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430", None))
        self.LabelSnDevice.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0421\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430", None))
        self.comboBoxExperiment.setCurrentText("")
        self.pushButtonAddExperiment.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c", None))
        self.pushButtonOk.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"Ok", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c", None))
    # retranslateUi

