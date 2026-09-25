# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cad_motivo_entradawtJbwm.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Cad_Motivo_Entrada(object):
    def setupUi(self, Cad_Motivo_Entrada):
        if not Cad_Motivo_Entrada.objectName():
            Cad_Motivo_Entrada.setObjectName(u"Cad_Motivo_Entrada")
        Cad_Motivo_Entrada.resize(552, 136)
        Cad_Motivo_Entrada.setMinimumSize(QSize(552, 136))
        Cad_Motivo_Entrada.setMaximumSize(QSize(552, 136))
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Cad_Motivo_Entrada.setFont(font)
        self.horizontalLayout = QHBoxLayout(Cad_Motivo_Entrada)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Cadastro = QFrame(Cad_Motivo_Entrada)
        self.frm_Cadastro.setObjectName(u"frm_Cadastro")
        self.frm_Cadastro.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Cadastro.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Cadastro)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Codigo = QFrame(self.frm_Cadastro)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Codigo = QLabel(self.frm_Codigo)
        self.lb_Codigo.setObjectName(u"lb_Codigo")
        self.lb_Codigo.setMinimumSize(QSize(0, 30))
        self.lb_Codigo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Codigo)

        self.txt_Codigo = QLineEdit(self.frm_Codigo)
        self.txt_Codigo.setObjectName(u"txt_Codigo")
        self.txt_Codigo.setMinimumSize(QSize(100, 30))
        self.txt_Codigo.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_2.addWidget(self.txt_Codigo)

        self.pushButton = QPushButton(self.frm_Codigo)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(40, 30))
        self.pushButton.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.bt_Novo = QPushButton(self.frm_Codigo)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frm_Codigo)

        self.frm_Descricao = QFrame(self.frm_Cadastro)
        self.frm_Descricao.setObjectName(u"frm_Descricao")
        self.frm_Descricao.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Descricao.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Descricao)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Descricao = QLabel(self.frm_Descricao)
        self.lb_Descricao.setObjectName(u"lb_Descricao")
        self.lb_Descricao.setMinimumSize(QSize(0, 30))
        self.lb_Descricao.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Descricao)

        self.txt_Descricao = QLineEdit(self.frm_Descricao)
        self.txt_Descricao.setObjectName(u"txt_Descricao")
        self.txt_Descricao.setMinimumSize(QSize(0, 30))
        self.txt_Descricao.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.txt_Descricao)

        self.chk_Baixa_Ficha = QCheckBox(self.frm_Descricao)
        self.chk_Baixa_Ficha.setObjectName(u"chk_Baixa_Ficha")
        self.chk_Baixa_Ficha.setMinimumSize(QSize(0, 30))
        self.chk_Baixa_Ficha.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.chk_Baixa_Ficha)


        self.verticalLayout.addWidget(self.frm_Descricao)

        self.frm_Crud = QFrame(self.frm_Cadastro)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Editar)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Excluir)


        self.verticalLayout.addWidget(self.frm_Crud)


        self.horizontalLayout.addWidget(self.frm_Cadastro)


        self.retranslateUi(Cad_Motivo_Entrada)

        QMetaObject.connectSlotsByName(Cad_Motivo_Entrada)
    # setupUi

    def retranslateUi(self, Cad_Motivo_Entrada):
        Cad_Motivo_Entrada.setWindowTitle(QCoreApplication.translate("Cad_Motivo_Entrada", u"Motivo Entrada", None))
        self.lb_Codigo.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"C\u00f3digo:", None))
        self.pushButton.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"+", None))
        self.lb_Descricao.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"Descri\u00e7\u00e3o:", None))
        self.chk_Baixa_Ficha.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"Baixa Ficha Tecnica", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Cad_Motivo_Entrada", u"Excluir", None))
    # retranslateUi

