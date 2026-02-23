# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget_crud_experimentakrloK.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QSizePolicy, QVBoxLayout,
    QWidget)
import resources.resources_rc

class Ui_WidgetCrudExperiment(object):
    def setupUi(self, WidgetCrudExperiment):
        if not WidgetCrudExperiment.objectName():
            WidgetCrudExperiment.setObjectName(u"WidgetCrudExperiment")
        WidgetCrudExperiment.resize(700, 500)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        WidgetCrudExperiment.setWindowIcon(icon)
        self.gridLayout = QGridLayout(WidgetCrudExperiment)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(WidgetCrudExperiment)

        QMetaObject.connectSlotsByName(WidgetCrudExperiment)
    # setupUi

    def retranslateUi(self, WidgetCrudExperiment):
        WidgetCrudExperiment.setWindowTitle(QCoreApplication.translate("WidgetCrudExperiment", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u044b", None))
    # retranslateUi

