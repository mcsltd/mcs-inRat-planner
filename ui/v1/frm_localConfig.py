# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frm_localConfigcGUxGK.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QListView,
    QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_FrmConfig(object):
    def setupUi(self, FrmConfig):
        if not FrmConfig.objectName():
            FrmConfig.setObjectName(u"FrmConfig")
        FrmConfig.resize(565, 426)
        self.gridLayout = QGridLayout(FrmConfig)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelItem = QLabel(FrmConfig)
        self.labelItem.setObjectName(u"labelItem")
        font = QFont()
        font.setPointSize(11)
        self.labelItem.setFont(font)
        self.labelItem.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout.addWidget(self.labelItem)


        self.gridLayout.addLayout(self.verticalLayout, 0, 2, 1, 1)

        self.listWidget = QListWidget(FrmConfig)
        self.listWidget.setObjectName(u"listWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QSize(100, 0))
        self.listWidget.setMaximumSize(QSize(200, 16777215))
        self.listWidget.setFlow(QListView.Flow.TopToBottom)

        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 3, 1, 1)


        self.retranslateUi(FrmConfig)

        QMetaObject.connectSlotsByName(FrmConfig)
    # setupUi

    def retranslateUi(self, FrmConfig):
        FrmConfig.setWindowTitle(QCoreApplication.translate("FrmConfig", u"\u041b\u043e\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.labelItem.setText(QCoreApplication.translate("FrmConfig", u"Item", None))
    # retranslateUi

