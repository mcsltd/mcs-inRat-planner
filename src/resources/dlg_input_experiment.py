# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_input_experimentGSvwiM.ui'
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
    QFormLayout, QGridLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)
import resources.resources_rc

class Ui_DlgInputExperiment(object):
    def setupUi(self, DlgInputExperiment):
        if not DlgInputExperiment.objectName():
            DlgInputExperiment.setObjectName(u"DlgInputExperiment")
        DlgInputExperiment.setWindowModality(Qt.WindowModality.ApplicationModal)
        DlgInputExperiment.resize(400, 154)
        font = QFont()
        font.setFamilies([u"Segoe UI Emoji"])
        font.setPointSize(11)
        DlgInputExperiment.setFont(font)
        icon = QIcon()
        icon.addFile(u":/images/icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        DlgInputExperiment.setWindowIcon(icon)
        self.gridLayout = QGridLayout(DlgInputExperiment)
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelExperiment = QLabel(DlgInputExperiment)
        self.labelExperiment.setObjectName(u"labelExperiment")
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(11)
        self.labelExperiment.setFont(font1)

        self.gridLayout.addWidget(self.labelExperiment, 0, 0, 1, 1)

        self.formLayoutExperiment = QFormLayout()
        self.formLayoutExperiment.setObjectName(u"formLayoutExperiment")
        self.lineEditExperiment = QLineEdit(DlgInputExperiment)
        self.lineEditExperiment.setObjectName(u"lineEditExperiment")
        self.lineEditExperiment.setFont(font)

        self.formLayoutExperiment.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditExperiment)


        self.gridLayout.addLayout(self.formLayoutExperiment, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(DlgInputExperiment)
        self.buttonBox.setObjectName(u"buttonBox")
        font2 = QFont()
        font2.setFamilies([u"Segoe UI Emoji"])
        font2.setPointSize(9)
        self.buttonBox.setFont(font2)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)


        self.retranslateUi(DlgInputExperiment)
        self.buttonBox.accepted.connect(DlgInputExperiment.accept)
        self.buttonBox.rejected.connect(DlgInputExperiment.reject)

        QMetaObject.connectSlotsByName(DlgInputExperiment)
    # setupUi

    def retranslateUi(self, DlgInputExperiment):
        DlgInputExperiment.setWindowTitle(QCoreApplication.translate("DlgInputExperiment", u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u044d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430", None))
        self.labelExperiment.setText(QCoreApplication.translate("DlgInputExperiment", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u044d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430:", None))
    # retranslateUi

