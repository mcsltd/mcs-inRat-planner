# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frm_online_control_plotItEtxD.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_FrmOnlineControlPane(object):
    def setupUi(self, FrmOnlineControlPane):
        if not FrmOnlineControlPane.objectName():
            FrmOnlineControlPane.setObjectName(u"FrmOnlineControlPane")
        FrmOnlineControlPane.resize(342, 122)
        FrmOnlineControlPane.setFrameShape(QFrame.Shape.Panel)
        FrmOnlineControlPane.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(FrmOnlineControlPane)
        self.gridLayout_2.setSpacing(7)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.groupBox = QGroupBox(FrmOnlineControlPane)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(30, 40))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, -1, 4, -1)
        self.labelAxisX = QLabel(self.groupBox)
        self.labelAxisX.setObjectName(u"labelAxisX")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labelAxisX.sizePolicy().hasHeightForWidth())
        self.labelAxisX.setSizePolicy(sizePolicy1)
        self.labelAxisX.setMinimumSize(QSize(60, 0))

        self.horizontalLayout.addWidget(self.labelAxisX)

        self.comboBoxTimebase = QComboBox(self.groupBox)
        self.comboBoxTimebase.setObjectName(u"comboBoxTimebase")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBoxTimebase.sizePolicy().hasHeightForWidth())
        self.comboBoxTimebase.setSizePolicy(sizePolicy2)
        self.comboBoxTimebase.setMinimumSize(QSize(40, 0))

        self.horizontalLayout.addWidget(self.comboBoxTimebase)

        self.labelAxisXDim = QLabel(self.groupBox)
        self.labelAxisXDim.setObjectName(u"labelAxisXDim")

        self.horizontalLayout.addWidget(self.labelAxisXDim)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)


        self.retranslateUi(FrmOnlineControlPane)

        QMetaObject.connectSlotsByName(FrmOnlineControlPane)
    # setupUi

    def retranslateUi(self, FrmOnlineControlPane):
        FrmOnlineControlPane.setWindowTitle(QCoreApplication.translate("FrmOnlineControlPane", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("FrmOnlineControlPane", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430", None))
        self.labelAxisX.setText(QCoreApplication.translate("FrmOnlineControlPane", u"\u0412\u0440\u0435\u043c\u0435\u043d\u043d\u043e\u0435 \u043e\u043a\u043d\u043e", None))
        self.labelAxisXDim.setText(QCoreApplication.translate("FrmOnlineControlPane", u"/\u0441", None))
    # retranslateUi

