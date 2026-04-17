# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_inrat_controller_v1YyMfGq.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QGridLayout,
    QLabel, QSizePolicy, QVBoxLayout, QWidget)
import src.resources.resources_rc

class Ui_DlgInRatController(object):
    def setupUi(self, DlgInRatController):
        if not DlgInRatController.objectName():
            DlgInRatController.setObjectName(u"DlgInRatController")
        DlgInRatController.resize(1164, 586)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DlgInRatController.setWindowIcon(icon)
        self.gridLayout = QGridLayout(DlgInRatController)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayoutPlot = QVBoxLayout()
        self.verticalLayoutPlot.setObjectName(u"verticalLayoutPlot")

        self.gridLayout.addLayout(self.verticalLayoutPlot, 0, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayoutInfo = QFormLayout()
        self.formLayoutInfo.setObjectName(u"formLayoutInfo")
        self.labelExperiment = QLabel(DlgInRatController)
        self.labelExperiment.setObjectName(u"labelExperiment")

        self.formLayoutInfo.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelExperiment)

        self.labelExperimentName = QLabel(DlgInRatController)
        self.labelExperimentName.setObjectName(u"labelExperimentName")

        self.formLayoutInfo.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelExperimentName)

        self.labelObject = QLabel(DlgInRatController)
        self.labelObject.setObjectName(u"labelObject")

        self.formLayoutInfo.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelObject)

        self.labelObjectName = QLabel(DlgInRatController)
        self.labelObjectName.setObjectName(u"labelObjectName")

        self.formLayoutInfo.setWidget(1, QFormLayout.ItemRole.FieldRole, self.labelObjectName)

        self.labelDevice = QLabel(DlgInRatController)
        self.labelDevice.setObjectName(u"labelDevice")
        self.labelDevice.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayoutInfo.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelDevice)

        self.labelDeviceName = QLabel(DlgInRatController)
        self.labelDeviceName.setObjectName(u"labelDeviceName")

        self.formLayoutInfo.setWidget(2, QFormLayout.ItemRole.FieldRole, self.labelDeviceName)


        self.verticalLayout.addLayout(self.formLayoutInfo)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)


        self.retranslateUi(DlgInRatController)

        QMetaObject.connectSlotsByName(DlgInRatController)
    # setupUi

    def retranslateUi(self, DlgInRatController):
        DlgInRatController.setWindowTitle(QCoreApplication.translate("DlgInRatController", u"Dialog", None))
        self.labelExperiment.setText(QCoreApplication.translate("DlgInRatController", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442:", None))
        self.labelExperimentName.setText("")
        self.labelObject.setText(QCoreApplication.translate("DlgInRatController", u"\u041e\u0431\u044a\u0435\u043a\u0442:", None))
        self.labelObjectName.setText("")
        self.labelDevice.setText(QCoreApplication.translate("DlgInRatController", u"\u0423\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e:", None))
        self.labelDeviceName.setText("")
    # retranslateUi

