# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_show_licensesXoDZHF.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHeaderView,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class Ui_DlgLicenses(object):
    def setupUi(self, DlgLicenses):
        if not DlgLicenses.objectName():
            DlgLicenses.setObjectName(u"DlgLicenses")
        DlgLicenses.resize(638, 406)
        self.gridLayout = QGridLayout(DlgLicenses)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tableWidgetLicense = QTableWidget(DlgLicenses)
        self.tableWidgetLicense.setObjectName(u"tableWidgetLicense")

        self.gridLayout.addWidget(self.tableWidgetLicense, 0, 0, 1, 1)


        self.retranslateUi(DlgLicenses)

        QMetaObject.connectSlotsByName(DlgLicenses)
    # setupUi

    def retranslateUi(self, DlgLicenses):
        DlgLicenses.setWindowTitle(QCoreApplication.translate("DlgLicenses", u"\u041b\u0438\u0446\u0435\u043d\u0437\u0438\u0438 \u0441\u0442\u043e\u0440\u043e\u043d\u043d\u0438\u0445 \u0431\u0438\u0431\u043b\u0438\u043e\u0442\u0435\u043a", None))
    # retranslateUi

