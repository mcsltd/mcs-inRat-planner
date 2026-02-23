# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frm_localConfigJOwqqB.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QSizePolicy, QVBoxLayout, QWidget)
import resources.resources_rc

class Ui_FrmMainConfig(object):
    def setupUi(self, FrmMainConfig):
        if not FrmMainConfig.objectName():
            FrmMainConfig.setObjectName(u"FrmMainConfig")
        FrmMainConfig.resize(762, 534)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        FrmMainConfig.setWindowIcon(icon)
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


        self.gridLayout.addLayout(self.verticalLayoutConfig, 0, 0, 1, 1)


        self.retranslateUi(FrmMainConfig)

        QMetaObject.connectSlotsByName(FrmMainConfig)
    # setupUi

    def retranslateUi(self, FrmMainConfig):
        FrmMainConfig.setWindowTitle(QCoreApplication.translate("FrmMainConfig", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
    # retranslateUi

