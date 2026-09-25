# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pesquisa_motivo_entradaCvshZE.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)

class Ui_Pesquisa_Motivo_Entrada(object):
    def setupUi(self, Pesquisa_Motivo_Entrada):
        if not Pesquisa_Motivo_Entrada.objectName():
            Pesquisa_Motivo_Entrada.setObjectName(u"Pesquisa_Motivo_Entrada")
        Pesquisa_Motivo_Entrada.resize(542, 304)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Pesquisa_Motivo_Entrada.setFont(font)
        self.verticalLayout = QVBoxLayout(Pesquisa_Motivo_Entrada)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Filtro = QFrame(Pesquisa_Motivo_Entrada)
        self.frm_Filtro.setObjectName(u"frm_Filtro")
        self.frm_Filtro.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Filtro.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_Filtro)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.lb_Pesquisa = QLabel(self.frm_Filtro)
        self.lb_Pesquisa.setObjectName(u"lb_Pesquisa")
        self.lb_Pesquisa.setMinimumSize(QSize(0, 30))
        self.lb_Pesquisa.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Pesquisa)

        self.txt_Pesquisa = QLineEdit(self.frm_Filtro)
        self.txt_Pesquisa.setObjectName(u"txt_Pesquisa")
        self.txt_Pesquisa.setMinimumSize(QSize(0, 30))
        self.txt_Pesquisa.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.txt_Pesquisa)

        self.bt_Pesquisa = QPushButton(self.frm_Filtro)
        self.bt_Pesquisa.setObjectName(u"bt_Pesquisa")
        self.bt_Pesquisa.setMinimumSize(QSize(0, 30))
        self.bt_Pesquisa.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.bt_Pesquisa)


        self.verticalLayout.addWidget(self.frm_Filtro)

        self.frm_Lista = QFrame(Pesquisa_Motivo_Entrada)
        self.frm_Lista.setObjectName(u"frm_Lista")
        self.frm_Lista.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Lista.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Lista)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.tb_Motivo = QTableView(self.frm_Lista)
        self.tb_Motivo.setObjectName(u"tb_Motivo")

        self.verticalLayout_2.addWidget(self.tb_Motivo)


        self.verticalLayout.addWidget(self.frm_Lista)


        self.retranslateUi(Pesquisa_Motivo_Entrada)

        QMetaObject.connectSlotsByName(Pesquisa_Motivo_Entrada)
    # setupUi

    def retranslateUi(self, Pesquisa_Motivo_Entrada):
        Pesquisa_Motivo_Entrada.setWindowTitle(QCoreApplication.translate("Pesquisa_Motivo_Entrada", u"Pesquisa Motivo de Entrada", None))
        self.lb_Pesquisa.setText(QCoreApplication.translate("Pesquisa_Motivo_Entrada", u"Pesquisar:", None))
        self.bt_Pesquisa.setText(QCoreApplication.translate("Pesquisa_Motivo_Entrada", u"Confirmar", None))
    # retranslateUi

