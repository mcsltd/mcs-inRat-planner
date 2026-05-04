# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'record_viewerbRRFoK.ui'
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
    QSlider, QSpacerItem, QVBoxLayout, QWidget)
import resources.resources_rc

class Ui_frmRecordViewer(object):
    def setupUi(self, frmRecordViewer):
        if not frmRecordViewer.objectName():
            frmRecordViewer.setObjectName(u"frmRecordViewer")
        frmRecordViewer.resize(1267, 596)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        frmRecordViewer.setWindowIcon(icon)
        self.gridLayout = QGridLayout(frmRecordViewer)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutMonitor = QVBoxLayout()
        self.verticalLayoutMonitor.setSpacing(0)
        self.verticalLayoutMonitor.setObjectName(u"verticalLayoutMonitor")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(9)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.groupBoxTimescale = QGroupBox(frmRecordViewer)
        self.groupBoxTimescale.setObjectName(u"groupBoxTimescale")
        self.gridLayout_2 = QGridLayout(self.groupBoxTimescale)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayoutControlPlot = QGridLayout()
        self.gridLayoutControlPlot.setObjectName(u"gridLayoutControlPlot")
        self.comboBoxSpeed = QComboBox(self.groupBoxTimescale)
        self.comboBoxSpeed.setObjectName(u"comboBoxSpeed")

        self.gridLayoutControlPlot.addWidget(self.comboBoxSpeed, 1, 0, 1, 1)

        self.labelLimitEcg = QLabel(self.groupBoxTimescale)
        self.labelLimitEcg.setObjectName(u"labelLimitEcg")

        self.gridLayoutControlPlot.addWidget(self.labelLimitEcg, 0, 1, 1, 1)

        self.comboBoxLimitEcg = QComboBox(self.groupBoxTimescale)
        self.comboBoxLimitEcg.setObjectName(u"comboBoxLimitEcg")

        self.gridLayoutControlPlot.addWidget(self.comboBoxLimitEcg, 1, 1, 1, 1)

        self.labelSpeed = QLabel(self.groupBoxTimescale)
        self.labelSpeed.setObjectName(u"labelSpeed")

        self.gridLayoutControlPlot.addWidget(self.labelSpeed, 0, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayoutControlPlot, 0, 1, 1, 1)


        self.horizontalLayout.addWidget(self.groupBoxTimescale)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayoutMonitor.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.horizontalSlider = QSlider(frmRecordViewer)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_4.addWidget(self.horizontalSlider)

        self.line = QFrame(frmRecordViewer)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_4.addWidget(self.line)

        self.labelCurrentTime = QLabel(frmRecordViewer)
        self.labelCurrentTime.setObjectName(u"labelCurrentTime")

        self.horizontalLayout_4.addWidget(self.labelCurrentTime)


        self.verticalLayoutMonitor.addLayout(self.horizontalLayout_4)


        self.gridLayout.addLayout(self.verticalLayoutMonitor, 0, 0, 1, 1)


        self.retranslateUi(frmRecordViewer)

        QMetaObject.connectSlotsByName(frmRecordViewer)
    # setupUi

    def retranslateUi(self, frmRecordViewer):
        frmRecordViewer.setWindowTitle(QCoreApplication.translate("frmRecordViewer", u"\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433", None))
        self.groupBoxTimescale.setTitle(QCoreApplication.translate("frmRecordViewer", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f", None))
        self.labelLimitEcg.setText(QCoreApplication.translate("frmRecordViewer", u"\u0414\u0438\u0430\u043f\u0430\u0437\u043e\u043d \u042d\u041a\u0413, \u00b1\u043c\u0412", None))
        self.labelSpeed.setText(QCoreApplication.translate("frmRecordViewer", u"\u0421\u043a\u043e\u0440\u043e\u0441\u0442\u044c, \u043c\u043c/c", None))
        self.labelCurrentTime.setText(QCoreApplication.translate("frmRecordViewer", u"00:00", None))
    # retranslateUi

