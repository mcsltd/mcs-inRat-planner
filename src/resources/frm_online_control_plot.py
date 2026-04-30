# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frm_online_control_plotKjdFEE.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QLabel, QSizePolicy,
    QWidget)

class Ui_FrmOnlineControlPane(object):
    def setupUi(self, FrmOnlineControlPane):
        if not FrmOnlineControlPane.objectName():
            FrmOnlineControlPane.setObjectName(u"FrmOnlineControlPane")
        FrmOnlineControlPane.resize(340, 148)
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
        self.labelTime = QLabel(self.groupBox)
        self.labelTime.setObjectName(u"labelTime")

        self.gridLayout_3.addWidget(self.labelTime, 0, 0, 1, 1)

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

        self.comboBoxEcgLimit = QComboBox(self.groupBox)
        self.comboBoxEcgLimit.setObjectName(u"comboBoxEcgLimit")
        self.comboBoxEcgLimit.setEnabled(False)

        self.gridLayout_3.addWidget(self.comboBoxEcgLimit, 1, 1, 1, 1)

        self.labelECG = QLabel(self.groupBox)
        self.labelECG.setObjectName(u"labelECG")

        self.gridLayout_3.addWidget(self.labelECG, 1, 0, 1, 1)

        self.checkBoxDynamicRange = QCheckBox(self.groupBox)
        self.checkBoxDynamicRange.setObjectName(u"checkBoxDynamicRange")
        self.checkBoxDynamicRange.setEnabled(False)
        self.checkBoxDynamicRange.setAutoRepeat(False)

        self.gridLayout_3.addWidget(self.checkBoxDynamicRange, 2, 1, 1, 1)

        self.labelDynamicRange = QLabel(self.groupBox)
        self.labelDynamicRange.setObjectName(u"labelDynamicRange")

        self.gridLayout_3.addWidget(self.labelDynamicRange, 2, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_3, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)


        self.retranslateUi(FrmOnlineControlPane)

        QMetaObject.connectSlotsByName(FrmOnlineControlPane)
    # setupUi

    def retranslateUi(self, FrmOnlineControlPane):
        FrmOnlineControlPane.setWindowTitle(QCoreApplication.translate("FrmOnlineControlPane", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("FrmOnlineControlPane", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043c\u0430\u0441\u0448\u0442\u0430\u0431\u0430", None))
        self.labelTime.setText(QCoreApplication.translate("FrmOnlineControlPane", u"\u0412\u0440\u0435\u043c\u044f, \u043c\u043c/c", None))
        self.labelECG.setText(QCoreApplication.translate("FrmOnlineControlPane", u"\u041b\u0438\u043c\u0438\u0442 \u042d\u041a\u0413, \u00b1\u043c\u0412", None))
        self.checkBoxDynamicRange.setText("")
        self.labelDynamicRange.setText(QCoreApplication.translate("FrmOnlineControlPane", u"\u0414\u0438\u043d\u0430\u043c\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u0434\u0438\u0430\u043f\u0430\u0437\u043e\u043d", None))
    # retranslateUi

