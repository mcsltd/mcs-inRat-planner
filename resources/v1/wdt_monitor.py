# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wdt_monitoruSVZsu.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGridLayout,
    QLabel, QSizePolicy, QVBoxLayout, QWidget)

class Ui_FormMonitor(object):
    def setupUi(self, FormMonitor):
        if not FormMonitor.objectName():
            FormMonitor.setObjectName(u"FormMonitor")
        FormMonitor.resize(1275, 612)
        self.gridLayout = QGridLayout(FormMonitor)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutMonitor = QVBoxLayout()
        self.verticalLayoutMonitor.setObjectName(u"verticalLayoutMonitor")

        self.gridLayout.addLayout(self.verticalLayoutMonitor, 0, 0, 1, 1)

        self.verticalLayoutInfo = QVBoxLayout()
        self.verticalLayoutInfo.setObjectName(u"verticalLayoutInfo")
        self.labelInformation = QLabel(FormMonitor)
        self.labelInformation.setObjectName(u"labelInformation")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelInformation.sizePolicy().hasHeightForWidth())
        self.labelInformation.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        self.labelInformation.setFont(font)
        self.labelInformation.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutInfo.addWidget(self.labelInformation)

        self.line = QFrame(FormMonitor)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayoutInfo.addWidget(self.line)

        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.labelObject = QLabel(FormMonitor)
        self.labelObject.setObjectName(u"labelObject")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labelObject.sizePolicy().hasHeightForWidth())
        self.labelObject.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(10)
        self.labelObject.setFont(font1)

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelObject)

        self.labelObjectValue = QLabel(FormMonitor)
        self.labelObjectValue.setObjectName(u"labelObjectValue")
        self.labelObjectValue.setFont(font1)
        self.labelObjectValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelObjectValue)

        self.labelDevice = QLabel(FormMonitor)
        self.labelDevice.setObjectName(u"labelDevice")
        sizePolicy1.setHeightForWidth(self.labelDevice.sizePolicy().hasHeightForWidth())
        self.labelDevice.setSizePolicy(sizePolicy1)
        self.labelDevice.setFont(font1)

        self.formLayout_5.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDevice)

        self.labelDeviceValue = QLabel(FormMonitor)
        self.labelDeviceValue.setObjectName(u"labelDeviceValue")
        self.labelDeviceValue.setFont(font1)
        self.labelDeviceValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_5.setWidget(1, QFormLayout.ItemRole.FieldRole, self.labelDeviceValue)

        self.labelSamplingRate = QLabel(FormMonitor)
        self.labelSamplingRate.setObjectName(u"labelSamplingRate")
        sizePolicy1.setHeightForWidth(self.labelSamplingRate.sizePolicy().hasHeightForWidth())
        self.labelSamplingRate.setSizePolicy(sizePolicy1)
        self.labelSamplingRate.setFont(font1)

        self.formLayout_5.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSamplingRate)

        self.labelSamplingRateValue = QLabel(FormMonitor)
        self.labelSamplingRateValue.setObjectName(u"labelSamplingRateValue")
        self.labelSamplingRateValue.setFont(font1)
        self.labelSamplingRateValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_5.setWidget(2, QFormLayout.ItemRole.FieldRole, self.labelSamplingRateValue)

        self.labelStartTime = QLabel(FormMonitor)
        self.labelStartTime.setObjectName(u"labelStartTime")
        sizePolicy1.setHeightForWidth(self.labelStartTime.sizePolicy().hasHeightForWidth())
        self.labelStartTime.setSizePolicy(sizePolicy1)
        self.labelStartTime.setFont(font1)

        self.formLayout_5.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelStartTime)

        self.labelDuration = QLabel(FormMonitor)
        self.labelDuration.setObjectName(u"labelDuration")
        sizePolicy1.setHeightForWidth(self.labelDuration.sizePolicy().hasHeightForWidth())
        self.labelDuration.setSizePolicy(sizePolicy1)
        self.labelDuration.setFont(font1)

        self.formLayout_5.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelDuration)

        self.labelDurationValue = QLabel(FormMonitor)
        self.labelDurationValue.setObjectName(u"labelDurationValue")
        self.labelDurationValue.setFont(font1)
        self.labelDurationValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_5.setWidget(4, QFormLayout.ItemRole.FieldRole, self.labelDurationValue)

        self.labelStartTimeValue = QLabel(FormMonitor)
        self.labelStartTimeValue.setObjectName(u"labelStartTimeValue")
        self.labelStartTimeValue.setFont(font1)
        self.labelStartTimeValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_5.setWidget(3, QFormLayout.ItemRole.FieldRole, self.labelStartTimeValue)

        self.labelFormat = QLabel(FormMonitor)
        self.labelFormat.setObjectName(u"labelFormat")
        sizePolicy1.setHeightForWidth(self.labelFormat.sizePolicy().hasHeightForWidth())
        self.labelFormat.setSizePolicy(sizePolicy1)
        self.labelFormat.setFont(font1)

        self.formLayout_5.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelFormat)

        self.labelFormatValue = QLabel(FormMonitor)
        self.labelFormatValue.setObjectName(u"labelFormatValue")
        self.labelFormatValue.setFont(font1)
        self.labelFormatValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout_5.setWidget(5, QFormLayout.ItemRole.FieldRole, self.labelFormatValue)


        self.verticalLayoutInfo.addLayout(self.formLayout_5)


        self.gridLayout.addLayout(self.verticalLayoutInfo, 0, 1, 1, 1)


        self.retranslateUi(FormMonitor)

        QMetaObject.connectSlotsByName(FormMonitor)
    # setupUi

    def retranslateUi(self, FormMonitor):
        FormMonitor.setWindowTitle(QCoreApplication.translate("FormMonitor", u"\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433", None))
        self.labelInformation.setText(QCoreApplication.translate("FormMonitor", u"\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0437\u0430\u043f\u0438\u0441\u0438:", None))
        self.labelObject.setText(QCoreApplication.translate("FormMonitor", u"\u041e\u0431\u044a\u0435\u043a\u0442:", None))
        self.labelObjectValue.setText(QCoreApplication.translate("FormMonitor", u"None", None))
        self.labelDevice.setText(QCoreApplication.translate("FormMonitor", u"\u0423\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e:", None))
        self.labelDeviceValue.setText(QCoreApplication.translate("FormMonitor", u"None", None))
        self.labelSamplingRate.setText(QCoreApplication.translate("FormMonitor", u"\u0427\u0430\u0441\u0442\u043e\u0442\u0430 \u043e\u0446\u0438\u0444\u0440\u043e\u0432\u043a\u0438:", None))
        self.labelSamplingRateValue.setText(QCoreApplication.translate("FormMonitor", u"None", None))
        self.labelStartTime.setText(QCoreApplication.translate("FormMonitor", u"\u0412\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0437\u0430\u043f\u0438\u0441\u0438:", None))
        self.labelDuration.setText(QCoreApplication.translate("FormMonitor", u"\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u0438:", None))
        self.labelDurationValue.setText(QCoreApplication.translate("FormMonitor", u"None", None))
        self.labelStartTimeValue.setText(QCoreApplication.translate("FormMonitor", u"None", None))
        self.labelFormat.setText(QCoreApplication.translate("FormMonitor", u"\u0424\u043e\u0440\u043c\u0430\u0442 \u0444\u0430\u0439\u043b\u0430:", None))
        self.labelFormatValue.setText(QCoreApplication.translate("FormMonitor", u"None", None))
    # retranslateUi

