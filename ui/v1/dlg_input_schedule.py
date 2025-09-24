# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_input_schedulePihMzi.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDateTimeEdit,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_DlgCreateNewSchedule(object):
    def setupUi(self, DlgCreateNewSchedule):
        if not DlgCreateNewSchedule.objectName():
            DlgCreateNewSchedule.setObjectName(u"DlgCreateNewSchedule")
        DlgCreateNewSchedule.setWindowModality(Qt.WindowModality.ApplicationModal)
        DlgCreateNewSchedule.resize(464, 492)
        DlgCreateNewSchedule.setAutoFillBackground(False)
        DlgCreateNewSchedule.setInputMethodHints(Qt.InputMethodHint.ImhUrlCharactersOnly)
        DlgCreateNewSchedule.setSizeGripEnabled(False)
        self.buttonBoxSchedule = QDialogButtonBox(DlgCreateNewSchedule)
        self.buttonBoxSchedule.setObjectName(u"buttonBoxSchedule")
        self.buttonBoxSchedule.setGeometry(QRect(140, 430, 301, 32))
        self.buttonBoxSchedule.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.buttonBoxSchedule.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBoxSchedule.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.RestoreDefaults)
        self.buttonBoxSchedule.setCenterButtons(True)
        self.groupBoxRecords = QGroupBox(DlgCreateNewSchedule)
        self.groupBoxRecords.setObjectName(u"groupBoxRecords")
        self.groupBoxRecords.setGeometry(QRect(20, 290, 421, 131))
        self.formLayoutWidget_2 = QWidget(self.groupBoxRecords)
        self.formLayoutWidget_2.setObjectName(u"formLayoutWidget_2")
        self.formLayoutWidget_2.setGeometry(QRect(10, 30, 401, 81))
        self.formLayoutRecords = QFormLayout(self.formLayoutWidget_2)
        self.formLayoutRecords.setObjectName(u"formLayoutRecords")
        self.formLayoutRecords.setContentsMargins(0, 0, 0, 0)
        self.labelDuration = QLabel(self.formLayoutWidget_2)
        self.labelDuration.setObjectName(u"labelDuration")

        self.formLayoutRecords.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelDuration)

        self.labelSamplingRate = QLabel(self.formLayoutWidget_2)
        self.labelSamplingRate.setObjectName(u"labelSamplingRate")

        self.formLayoutRecords.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelSamplingRate)

        self.comboBoxSamplingRate = QComboBox(self.formLayoutWidget_2)
        self.comboBoxSamplingRate.setObjectName(u"comboBoxSamplingRate")

        self.formLayoutRecords.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBoxSamplingRate)

        self.labelFormat = QLabel(self.formLayoutWidget_2)
        self.labelFormat.setObjectName(u"labelFormat")

        self.formLayoutRecords.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelFormat)

        self.comboBoxFormat = QComboBox(self.formLayoutWidget_2)
        self.comboBoxFormat.setObjectName(u"comboBoxFormat")

        self.formLayoutRecords.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBoxFormat)

        self.comboBoxDuration = QComboBox(self.formLayoutWidget_2)
        self.comboBoxDuration.setObjectName(u"comboBoxDuration")

        self.formLayoutRecords.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBoxDuration)

        self.groupBoxSchedule = QGroupBox(DlgCreateNewSchedule)
        self.groupBoxSchedule.setObjectName(u"groupBoxSchedule")
        self.groupBoxSchedule.setGeometry(QRect(20, 160, 421, 121))
        self.formLayoutWidget_3 = QWidget(self.groupBoxSchedule)
        self.formLayoutWidget_3.setObjectName(u"formLayoutWidget_3")
        self.formLayoutWidget_3.setGeometry(QRect(10, 30, 401, 77))
        self.formLayoutSchedule = QFormLayout(self.formLayoutWidget_3)
        self.formLayoutSchedule.setObjectName(u"formLayoutSchedule")
        self.formLayoutSchedule.setContentsMargins(0, 0, 0, 0)
        self.labelStarTime = QLabel(self.formLayoutWidget_3)
        self.labelStarTime.setObjectName(u"labelStarTime")

        self.formLayoutSchedule.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelStarTime)

        self.labelIntervalRecord = QLabel(self.formLayoutWidget_3)
        self.labelIntervalRecord.setObjectName(u"labelIntervalRecord")

        self.formLayoutSchedule.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelIntervalRecord)

        self.dateTimeEditStartExperiment = QDateTimeEdit(self.formLayoutWidget_3)
        self.dateTimeEditStartExperiment.setObjectName(u"dateTimeEditStartExperiment")

        self.formLayoutSchedule.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dateTimeEditStartExperiment)

        self.labeFinishTime = QLabel(self.formLayoutWidget_3)
        self.labeFinishTime.setObjectName(u"labeFinishTime")

        self.formLayoutSchedule.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labeFinishTime)

        self.dateTimeEditFinishExperiment = QDateTimeEdit(self.formLayoutWidget_3)
        self.dateTimeEditFinishExperiment.setObjectName(u"dateTimeEditFinishExperiment")

        self.formLayoutSchedule.setWidget(1, QFormLayout.ItemRole.FieldRole, self.dateTimeEditFinishExperiment)

        self.comboBoxInterval = QComboBox(self.formLayoutWidget_3)
        self.comboBoxInterval.setObjectName(u"comboBoxInterval")

        self.formLayoutSchedule.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBoxInterval)

        self.formLayoutWidget = QWidget(DlgCreateNewSchedule)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(30, 30, 401, 115))
        self.formLayoutInformation = QFormLayout(self.formLayoutWidget)
        self.formLayoutInformation.setObjectName(u"formLayoutInformation")
        self.formLayoutInformation.setContentsMargins(0, 0, 0, 0)
        self.LabelExperiment = QLabel(self.formLayoutWidget)
        self.LabelExperiment.setObjectName(u"LabelExperiment")

        self.formLayoutInformation.setWidget(0, QFormLayout.ItemRole.LabelRole, self.LabelExperiment)

        self.LabelObject = QLabel(self.formLayoutWidget)
        self.LabelObject.setObjectName(u"LabelObject")

        self.formLayoutInformation.setWidget(1, QFormLayout.ItemRole.LabelRole, self.LabelObject)

        self.LineEditObject = QLineEdit(self.formLayoutWidget)
        self.LineEditObject.setObjectName(u"LineEditObject")

        self.formLayoutInformation.setWidget(1, QFormLayout.ItemRole.FieldRole, self.LineEditObject)

        self.LabelModelDevice = QLabel(self.formLayoutWidget)
        self.LabelModelDevice.setObjectName(u"LabelModelDevice")

        self.formLayoutInformation.setWidget(2, QFormLayout.ItemRole.LabelRole, self.LabelModelDevice)

        self.comboBoxModelDevice = QComboBox(self.formLayoutWidget)
        self.comboBoxModelDevice.setObjectName(u"comboBoxModelDevice")

        self.formLayoutInformation.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBoxModelDevice)

        self.LineEditSnDevice = QLineEdit(self.formLayoutWidget)
        self.LineEditSnDevice.setObjectName(u"LineEditSnDevice")

        self.formLayoutInformation.setWidget(3, QFormLayout.ItemRole.FieldRole, self.LineEditSnDevice)

        self.LabelSnDevice = QLabel(self.formLayoutWidget)
        self.LabelSnDevice.setObjectName(u"LabelSnDevice")

        self.formLayoutInformation.setWidget(3, QFormLayout.ItemRole.LabelRole, self.LabelSnDevice)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBoxExperiment = QComboBox(self.formLayoutWidget)
        self.comboBoxExperiment.setObjectName(u"comboBoxExperiment")
        self.comboBoxExperiment.setEnabled(True)
        self.comboBoxExperiment.setEditable(False)

        self.horizontalLayout.addWidget(self.comboBoxExperiment)


        self.formLayoutInformation.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)


        self.retranslateUi(DlgCreateNewSchedule)
        self.buttonBoxSchedule.accepted.connect(DlgCreateNewSchedule.accept)
        self.buttonBoxSchedule.rejected.connect(DlgCreateNewSchedule.reject)

        QMetaObject.connectSlotsByName(DlgCreateNewSchedule)
    # setupUi

    def retranslateUi(self, DlgCreateNewSchedule):
        DlgCreateNewSchedule.setWindowTitle(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044f", None))
        self.groupBoxRecords.setTitle(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0437\u0430\u043f\u0438\u0441\u0438", None))
        self.labelDuration.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u0438", None))
        self.labelSamplingRate.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0427\u0430\u0441\u0442\u043e\u0442\u0430 \u043e\u0446\u0438\u0444\u0440\u043e\u0432\u043a\u0438", None))
        self.labelFormat.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0424\u043e\u0440\u043c\u0430\u0442", None))
        self.groupBoxSchedule.setTitle(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0420\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None))
        self.labelStarTime.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041d\u0430\u0447\u0430\u043b\u043e ", None))
        self.labelIntervalRecord.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041f\u0435\u0440\u0438\u043e\u0434\u0438\u0447\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u0438", None))
        self.labeFinishTime.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435", None))
        self.LabelExperiment.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442", None))
        self.LabelObject.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041e\u0431\u044a\u0435\u043a\u0442", None))
        self.LabelModelDevice.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u041c\u043e\u0434\u0435\u043b\u044c \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430", None))
        self.LabelSnDevice.setText(QCoreApplication.translate("DlgCreateNewSchedule", u"\u0421\u0435\u0440\u0438\u0439\u043d\u044b\u0439 \u043d\u043e\u043c\u0435\u0440 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430", None))
        self.comboBoxExperiment.setCurrentText("")
    # retranslateUi

