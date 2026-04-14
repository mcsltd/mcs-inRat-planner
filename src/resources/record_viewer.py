# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'record_viewernfPfrp.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QScrollBar, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
import src.resources.resources_rc

class Ui_frmRecordViewer(object):
    def setupUi(self, frmRecordViewer):
        if not frmRecordViewer.objectName():
            frmRecordViewer.setObjectName(u"frmRecordViewer")
        frmRecordViewer.resize(1271, 604)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        frmRecordViewer.setWindowIcon(icon)
        self.gridLayout = QGridLayout(frmRecordViewer)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutMonitor = QVBoxLayout()
        self.verticalLayoutMonitor.setSpacing(0)
        self.verticalLayoutMonitor.setObjectName(u"verticalLayoutMonitor")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(3, 3, 3, 3)
        self.labelSpeed = QLabel(frmRecordViewer)
        self.labelSpeed.setObjectName(u"labelSpeed")

        self.horizontalLayout.addWidget(self.labelSpeed)

        self.comboBoxSpeed = QComboBox(frmRecordViewer)
        self.comboBoxSpeed.setObjectName(u"comboBoxSpeed")

        self.horizontalLayout.addWidget(self.comboBoxSpeed)

        self.labelSens = QLabel(frmRecordViewer)
        self.labelSens.setObjectName(u"labelSens")

        self.horizontalLayout.addWidget(self.labelSens)

        self.comboBoxSens = QComboBox(frmRecordViewer)
        self.comboBoxSens.setObjectName(u"comboBoxSens")

        self.horizontalLayout.addWidget(self.comboBoxSens)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayoutMonitor.addLayout(self.horizontalLayout)

        self.ScrollBarWindow = QScrollBar(frmRecordViewer)
        self.ScrollBarWindow.setObjectName(u"ScrollBarWindow")
        self.ScrollBarWindow.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayoutMonitor.addWidget(self.ScrollBarWindow)


        self.gridLayout.addLayout(self.verticalLayoutMonitor, 0, 0, 1, 1)


        self.retranslateUi(frmRecordViewer)

        QMetaObject.connectSlotsByName(frmRecordViewer)
    # setupUi

    def retranslateUi(self, frmRecordViewer):
        frmRecordViewer.setWindowTitle(QCoreApplication.translate("frmRecordViewer", u"\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433", None))
        self.labelSpeed.setText(QCoreApplication.translate("frmRecordViewer", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c", None))
        self.labelSens.setText(QCoreApplication.translate("frmRecordViewer", u"\u0427\u0443\u0432\u0441\u0442\u0432\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c", None))
    # retranslateUi

