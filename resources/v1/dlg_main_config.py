# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_main_configubNMUr.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QWidget)

class Ui_DlgMainConfig(object):
    def setupUi(self, DlgMainConfig):
        if not DlgMainConfig.objectName():
            DlgMainConfig.setObjectName(u"DlgMainConfig")
        DlgMainConfig.resize(429, 248)
        self.gridLayout_2 = QGridLayout(DlgMainConfig)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.pushButtonCancel = QPushButton(DlgMainConfig)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.gridLayout_2.addWidget(self.pushButtonCancel, 1, 2, 1, 1)

        self.pushButtonOk = QPushButton(DlgMainConfig)
        self.pushButtonOk.setObjectName(u"pushButtonOk")

        self.gridLayout_2.addWidget(self.pushButtonOk, 1, 1, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelMaxCntDevice = QLabel(DlgMainConfig)
        self.labelMaxCntDevice.setObjectName(u"labelMaxCntDevice")

        self.gridLayout.addWidget(self.labelMaxCntDevice, 0, 0, 1, 1)

        self.pushButtonRecordRecovery = QPushButton(DlgMainConfig)
        self.pushButtonRecordRecovery.setObjectName(u"pushButtonRecordRecovery")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonRecordRecovery.sizePolicy().hasHeightForWidth())
        self.pushButtonRecordRecovery.setSizePolicy(sizePolicy)
        font = QFont()
        font.setKerning(True)
        self.pushButtonRecordRecovery.setFont(font)

        self.gridLayout.addWidget(self.pushButtonRecordRecovery, 1, 1, 1, 1)

        self.labelRecordQuestion = QLabel(DlgMainConfig)
        self.labelRecordQuestion.setObjectName(u"labelRecordQuestion")

        self.gridLayout.addWidget(self.labelRecordQuestion, 1, 0, 1, 1)

        self.comboBoxMaxCntDevice = QComboBox(DlgMainConfig)
        self.comboBoxMaxCntDevice.setObjectName(u"comboBoxMaxCntDevice")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBoxMaxCntDevice.sizePolicy().hasHeightForWidth())
        self.comboBoxMaxCntDevice.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.comboBoxMaxCntDevice, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 3)


        self.retranslateUi(DlgMainConfig)

        QMetaObject.connectSlotsByName(DlgMainConfig)
    # setupUi

    def retranslateUi(self, DlgMainConfig):
        DlgMainConfig.setWindowTitle(QCoreApplication.translate("DlgMainConfig", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("DlgMainConfig", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.pushButtonOk.setText(QCoreApplication.translate("DlgMainConfig", u"\u041e\u043a", None))
        self.labelMaxCntDevice.setText(QCoreApplication.translate("DlgMainConfig", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u043e\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432:", None))
        self.pushButtonRecordRecovery.setText(QCoreApplication.translate("DlgMainConfig", u"\u0412\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c", None))
        self.labelRecordQuestion.setText(QCoreApplication.translate("DlgMainConfig", u"\u0412\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u0443\u0434\u0430\u043b\u0435\u043d\u043d\u044b\u0435 \u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u044f?", None))
    # retranslateUi

