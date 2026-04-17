# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frm_online_control_plotvjsyBj.ui'
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
    QGroupBox, QLabel, QSizePolicy, QWidget)

class Ui_FrmOnlineControlPane(object):
    def setupUi(self, FrmOnlineControlPane):
        if not FrmOnlineControlPane.objectName():
            FrmOnlineControlPane.setObjectName(u"FrmOnlineControlPane")
        FrmOnlineControlPane.resize(321, 91)
        FrmOnlineControlPane.setFrameShape(QFrame.Shape.Panel)
        FrmOnlineControlPane.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(FrmOnlineControlPane)
        self.gridLayout_2.setSpacing(7)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.groupBox = QGroupBox(FrmOnlineControlPane)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(30, 40))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.comboBoxSpeed = QComboBox(self.groupBox)
        self.comboBoxSpeed.setObjectName(u"comboBoxSpeed")
        self.comboBoxSpeed.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBoxSpeed.sizePolicy().hasHeightForWidth())
        self.comboBoxSpeed.setSizePolicy(sizePolicy1)
        self.comboBoxSpeed.setMinimumSize(QSize(40, 0))

        self.gridLayout_3.addWidget(self.comboBoxSpeed, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_3, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)


        self.retranslateUi(FrmOnlineControlPane)

        QMetaObject.connectSlotsByName(FrmOnlineControlPane)
    # setupUi

    def retranslateUi(self, FrmOnlineControlPane):
        FrmOnlineControlPane.setWindowTitle(QCoreApplication.translate("FrmOnlineControlPane", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("FrmOnlineControlPane", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043c\u0430\u0441\u0448\u0442\u0430\u0431\u0430", None))
        self.label.setText(QCoreApplication.translate("FrmOnlineControlPane", u"\u0412\u0440\u0435\u043c\u044f:", None))
    # retranslateUi

