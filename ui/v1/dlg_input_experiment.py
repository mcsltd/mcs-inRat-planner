# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'designerYRpPSi.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_DlgInputExperiment(object):
    def setupUi(self, DlgInputExperiment):
        if not DlgInputExperiment.objectName():
            DlgInputExperiment.setObjectName(u"DlgInputExperiment")
        DlgInputExperiment.setWindowModality(Qt.WindowModality.ApplicationModal)
        DlgInputExperiment.resize(400, 153)
        font = QFont()
        font.setFamilies([u"Segoe UI Emoji"])
        font.setPointSize(11)
        DlgInputExperiment.setFont(font)
        self.buttonBox = QDialogButtonBox(DlgInputExperiment)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(20, 90, 341, 32))
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.formLayoutWidget = QWidget(DlgInputExperiment)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(30, 50, 341, 31))
        self.formLayoutWidget.setFont(font)
        self.formLayoutExperiment = QFormLayout(self.formLayoutWidget)
        self.formLayoutExperiment.setObjectName(u"formLayoutExperiment")
        self.formLayoutExperiment.setContentsMargins(0, 0, 0, 0)
        self.labelExperiment = QLabel(self.formLayoutWidget)
        self.labelExperiment.setObjectName(u"labelExperiment")
        self.labelExperiment.setFont(font)

        self.formLayoutExperiment.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelExperiment)

        self.lineEditExperiment = QLineEdit(self.formLayoutWidget)
        self.lineEditExperiment.setObjectName(u"lineEditExperiment")
        self.lineEditExperiment.setFont(font)

        self.formLayoutExperiment.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditExperiment)


        self.retranslateUi(DlgInputExperiment)
        self.buttonBox.accepted.connect(DlgInputExperiment.accept)
        self.buttonBox.rejected.connect(DlgInputExperiment.reject)

        QMetaObject.connectSlotsByName(DlgInputExperiment)
    # setupUi

    def retranslateUi(self, DlgInputExperiment):
        DlgInputExperiment.setWindowTitle(QCoreApplication.translate("DlgInputExperiment", u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u044d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430", None))
        self.labelExperiment.setText(QCoreApplication.translate("DlgInputExperiment", u"\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442", None))
    # retranslateUi

