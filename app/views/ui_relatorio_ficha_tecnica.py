# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'relatorio_ficha_tecnicayGbaBE.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Rel_Ficha_Tecnica(object):
    def setupUi(self, Rel_Ficha_Tecnica):
        if not Rel_Ficha_Tecnica.objectName():
            Rel_Ficha_Tecnica.setObjectName(u"Rel_Ficha_Tecnica")
        Rel_Ficha_Tecnica.resize(460, 92)
        Rel_Ficha_Tecnica.setMinimumSize(QSize(460, 92))
        Rel_Ficha_Tecnica.setMaximumSize(QSize(460, 92))
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Rel_Ficha_Tecnica.setFont(font)
        self.horizontalLayout = QHBoxLayout(Rel_Ficha_Tecnica)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Relatorio = QFrame(Rel_Ficha_Tecnica)
        self.frm_Relatorio.setObjectName(u"frm_Relatorio")
        self.frm_Relatorio.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Relatorio.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Relatorio)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Codigo = QFrame(self.frm_Relatorio)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Fichas_Tecnicas = QLabel(self.frm_Codigo)
        self.lb_Fichas_Tecnicas.setObjectName(u"lb_Fichas_Tecnicas")
        self.lb_Fichas_Tecnicas.setMinimumSize(QSize(0, 30))
        self.lb_Fichas_Tecnicas.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Fichas_Tecnicas)

        self.txt_Fichas_Tecnicas = QLineEdit(self.frm_Codigo)
        self.txt_Fichas_Tecnicas.setObjectName(u"txt_Fichas_Tecnicas")
        self.txt_Fichas_Tecnicas.setMinimumSize(QSize(0, 30))
        self.txt_Fichas_Tecnicas.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.txt_Fichas_Tecnicas)

        self.bt_Pesquisar_Fichas_Tecnicas = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Fichas_Tecnicas.setObjectName(u"bt_Pesquisar_Fichas_Tecnicas")
        self.bt_Pesquisar_Fichas_Tecnicas.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Fichas_Tecnicas.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisar_Fichas_Tecnicas)


        self.verticalLayout.addWidget(self.frm_Codigo)

        self.frm_Botoes = QFrame(self.frm_Relatorio)
        self.frm_Botoes.setObjectName(u"frm_Botoes")
        self.frm_Botoes.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Botoes.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Botoes)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.bt_Filtrar = QPushButton(self.frm_Botoes)
        self.bt_Filtrar.setObjectName(u"bt_Filtrar")
        self.bt_Filtrar.setMinimumSize(QSize(0, 30))
        self.bt_Filtrar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Filtrar)


        self.verticalLayout.addWidget(self.frm_Botoes)


        self.horizontalLayout.addWidget(self.frm_Relatorio)


        self.retranslateUi(Rel_Ficha_Tecnica)

        QMetaObject.connectSlotsByName(Rel_Ficha_Tecnica)
    # setupUi

    def retranslateUi(self, Rel_Ficha_Tecnica):
        Rel_Ficha_Tecnica.setWindowTitle(QCoreApplication.translate("Rel_Ficha_Tecnica", u"Relat\u00f3rio de Fichas Tecnicas", None))
        self.lb_Fichas_Tecnicas.setText(QCoreApplication.translate("Rel_Ficha_Tecnica", u"Fichas T\u00e9cnicas:", None))
        self.bt_Pesquisar_Fichas_Tecnicas.setText(QCoreApplication.translate("Rel_Ficha_Tecnica", u"...", None))
        self.bt_Filtrar.setText(QCoreApplication.translate("Rel_Ficha_Tecnica", u"Filtrar", None))
    # retranslateUi

