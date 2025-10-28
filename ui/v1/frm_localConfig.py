# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frm_localConfiggdMqfT.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_FrmMainConfig(object):
    def setupUi(self, FrmMainConfig):
        if not FrmMainConfig.objectName():
            FrmMainConfig.setObjectName(u"FrmMainConfig")
        FrmMainConfig.resize(762, 534)
        self.gridLayout = QGridLayout(FrmMainConfig)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutConfig = QVBoxLayout()
        self.verticalLayoutConfig.setObjectName(u"verticalLayoutConfig")
        self.horizontalLayoutMainConfig = QHBoxLayout()
        self.horizontalLayoutMainConfig.setObjectName(u"horizontalLayoutMainConfig")
        self.listWidget = QListWidget(FrmMainConfig)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setMaximumSize(QSize(250, 16777215))

        self.horizontalLayoutMainConfig.addWidget(self.listWidget)


        self.verticalLayoutConfig.addLayout(self.horizontalLayoutMainConfig)

        self.lineSeparate = QFrame(FrmMainConfig)
        self.lineSeparate.setObjectName(u"lineSeparate")
        self.lineSeparate.setFrameShape(QFrame.Shape.HLine)
        self.lineSeparate.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayoutConfig.addWidget(self.lineSeparate)

        self.horizontalLayoutControlConfig = QHBoxLayout()
        self.horizontalLayoutControlConfig.setObjectName(u"horizontalLayoutControlConfig")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutControlConfig.addItem(self.horizontalSpacer_2)

        self.pushButtonDefault = QPushButton(FrmMainConfig)
        self.pushButtonDefault.setObjectName(u"pushButtonDefault")

        self.horizontalLayoutControlConfig.addWidget(self.pushButtonDefault)

        self.pushButtonOk = QPushButton(FrmMainConfig)
        self.pushButtonOk.setObjectName(u"pushButtonOk")

        self.horizontalLayoutControlConfig.addWidget(self.pushButtonOk)

        self.pushButtonCancel = QPushButton(FrmMainConfig)
        self.pushButtonCancel.setObjectName(u"pushButtonCancel")

        self.horizontalLayoutControlConfig.addWidget(self.pushButtonCancel)


        self.verticalLayoutConfig.addLayout(self.horizontalLayoutControlConfig)


        self.gridLayout.addLayout(self.verticalLayoutConfig, 0, 0, 1, 1)


        self.retranslateUi(FrmMainConfig)

        QMetaObject.connectSlotsByName(FrmMainConfig)
    # setupUi

    def retranslateUi(self, FrmMainConfig):
        FrmMainConfig.setWindowTitle(QCoreApplication.translate("FrmMainConfig", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.pushButtonDefault.setText(QCoreApplication.translate("FrmMainConfig", u"\u041f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e", None))
        self.pushButtonOk.setText(QCoreApplication.translate("FrmMainConfig", u"\u041e\u043a", None))
        self.pushButtonCancel.setText(QCoreApplication.translate("FrmMainConfig", u"\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c", None))
    # retranslateUi

