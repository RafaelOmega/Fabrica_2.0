# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cad_produtosVujgCq.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Cad_Produtos(object):
    def setupUi(self, Cad_Produtos):
        if not Cad_Produtos.objectName():
            Cad_Produtos.setObjectName(u"Cad_Produtos")
        Cad_Produtos.resize(623, 221)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Cad_Produtos.setFont(font)
        self.horizontalLayout = QHBoxLayout(Cad_Produtos)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Cadastro = QFrame(Cad_Produtos)
        self.frm_Cadastro.setObjectName(u"frm_Cadastro")
        self.frm_Cadastro.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Cadastro.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Cadastro)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Novo = QFrame(self.frm_Cadastro)
        self.frm_Novo.setObjectName(u"frm_Novo")
        self.frm_Novo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Novo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Novo)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.lb_Codigo = QLabel(self.frm_Novo)
        self.lb_Codigo.setObjectName(u"lb_Codigo")
        self.lb_Codigo.setMinimumSize(QSize(0, 30))
        self.lb_Codigo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.lb_Codigo)

        self.txt_Codigo = QLineEdit(self.frm_Novo)
        self.txt_Codigo.setObjectName(u"txt_Codigo")
        self.txt_Codigo.setMinimumSize(QSize(100, 30))
        self.txt_Codigo.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_4.addWidget(self.txt_Codigo)

        self.bt_Pesquisar_Produtos = QPushButton(self.frm_Novo)
        self.bt_Pesquisar_Produtos.setObjectName(u"bt_Pesquisar_Produtos")
        self.bt_Pesquisar_Produtos.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Produtos.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_4.addWidget(self.bt_Pesquisar_Produtos)

        self.bt_Novo = QPushButton(self.frm_Novo)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_4.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frm_Novo)

        self.frm_Corpo = QFrame(self.frm_Cadastro)
        self.frm_Corpo.setObjectName(u"frm_Corpo")
        self.frm_Corpo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Corpo.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frm_Corpo)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Descricao = QFrame(self.frm_Corpo)
        self.frm_Descricao.setObjectName(u"frm_Descricao")
        self.frm_Descricao.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Descricao.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frm_Descricao)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(5, 5, 5, 5)
        self.lb_Descricao = QLabel(self.frm_Descricao)
        self.lb_Descricao.setObjectName(u"lb_Descricao")
        self.lb_Descricao.setMinimumSize(QSize(0, 30))
        self.lb_Descricao.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.lb_Descricao)

        self.txt_Descricao = QLineEdit(self.frm_Descricao)
        self.txt_Descricao.setObjectName(u"txt_Descricao")
        self.txt_Descricao.setMinimumSize(QSize(0, 30))
        self.txt_Descricao.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.txt_Descricao)


        self.gridLayout.addWidget(self.frm_Descricao, 0, 1, 1, 1)

        self.frm_Custo = QFrame(self.frm_Corpo)
        self.frm_Custo.setObjectName(u"frm_Custo")
        self.frm_Custo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Custo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frm_Custo)
        self.horizontalLayout_6.setSpacing(5)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(5, 5, 5, 5)
        self.lb_Peso = QLabel(self.frm_Custo)
        self.lb_Peso.setObjectName(u"lb_Peso")
        self.lb_Peso.setMinimumSize(QSize(0, 30))
        self.lb_Peso.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_6.addWidget(self.lb_Peso)

        self.txt_Peso = QDoubleSpinBox(self.frm_Custo)
        self.txt_Peso.setObjectName(u"txt_Peso")
        self.txt_Peso.setMinimumSize(QSize(120, 30))
        self.txt_Peso.setMaximumSize(QSize(120, 30))
        self.txt_Peso.setMaximum(9999999999.989999771118164)

        self.horizontalLayout_6.addWidget(self.txt_Peso)

        self.lb_Custo = QLabel(self.frm_Custo)
        self.lb_Custo.setObjectName(u"lb_Custo")
        self.lb_Custo.setMinimumSize(QSize(90, 30))
        self.lb_Custo.setMaximumSize(QSize(90, 30))

        self.horizontalLayout_6.addWidget(self.lb_Custo)

        self.txt_Custo = QDoubleSpinBox(self.frm_Custo)
        self.txt_Custo.setObjectName(u"txt_Custo")
        self.txt_Custo.setMinimumSize(QSize(120, 30))
        self.txt_Custo.setMaximumSize(QSize(120, 30))
        self.txt_Custo.setMaximum(9999999999.989999771118164)

        self.horizontalLayout_6.addWidget(self.txt_Custo)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)


        self.gridLayout.addWidget(self.frm_Custo, 1, 1, 1, 1)

        self.frm_Crud = QFrame(self.frm_Corpo)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Editar)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Excluir)


        self.gridLayout.addWidget(self.frm_Crud, 2, 1, 1, 1)

        self.frm_Opcoes = QFrame(self.frm_Corpo)
        self.frm_Opcoes.setObjectName(u"frm_Opcoes")
        self.frm_Opcoes.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Opcoes.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Opcoes)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.ch_Controla_Estoque = QCheckBox(self.frm_Opcoes)
        self.ch_Controla_Estoque.setObjectName(u"ch_Controla_Estoque")

        self.verticalLayout_2.addWidget(self.ch_Controla_Estoque)

        self.ch_Mao_Obra = QCheckBox(self.frm_Opcoes)
        self.ch_Mao_Obra.setObjectName(u"ch_Mao_Obra")

        self.verticalLayout_2.addWidget(self.ch_Mao_Obra)

        self.ch_Prod_Acabado = QCheckBox(self.frm_Opcoes)
        self.ch_Prod_Acabado.setObjectName(u"ch_Prod_Acabado")

        self.verticalLayout_2.addWidget(self.ch_Prod_Acabado)

        self.ch_Mat_Prima = QCheckBox(self.frm_Opcoes)
        self.ch_Mat_Prima.setObjectName(u"ch_Mat_Prima")

        self.verticalLayout_2.addWidget(self.ch_Mat_Prima)

        self.ch_Embalagem = QCheckBox(self.frm_Opcoes)
        self.ch_Embalagem.setObjectName(u"ch_Embalagem")

        self.verticalLayout_2.addWidget(self.ch_Embalagem)


        self.gridLayout.addWidget(self.frm_Opcoes, 0, 0, 3, 1)


        self.verticalLayout.addWidget(self.frm_Corpo)


        self.horizontalLayout.addWidget(self.frm_Cadastro)


        self.retranslateUi(Cad_Produtos)

        QMetaObject.connectSlotsByName(Cad_Produtos)
    # setupUi

    def retranslateUi(self, Cad_Produtos):
        Cad_Produtos.setWindowTitle(QCoreApplication.translate("Cad_Produtos", u"Cadastro de Produtos", None))
        self.lb_Codigo.setText(QCoreApplication.translate("Cad_Produtos", u"C\u00f3digo:", None))
        self.bt_Pesquisar_Produtos.setText(QCoreApplication.translate("Cad_Produtos", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Cad_Produtos", u"+", None))
        self.lb_Descricao.setText(QCoreApplication.translate("Cad_Produtos", u"Descri\u00e7\u00e3o:", None))
        self.lb_Peso.setText(QCoreApplication.translate("Cad_Produtos", u"Peso do Saco:", None))
        self.txt_Peso.setSuffix(QCoreApplication.translate("Cad_Produtos", u" Kg", None))
        self.lb_Custo.setText(QCoreApplication.translate("Cad_Produtos", u"Custo Unit\u00e1rio:", None))
        self.txt_Custo.setPrefix(QCoreApplication.translate("Cad_Produtos", u"R$ ", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Cad_Produtos", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Cad_Produtos", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Cad_Produtos", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Cad_Produtos", u"Excluir", None))
        self.ch_Controla_Estoque.setText(QCoreApplication.translate("Cad_Produtos", u"Controla Estoque?", None))
        self.ch_Mao_Obra.setText(QCoreApplication.translate("Cad_Produtos", u"M\u00e3o de obra", None))
        self.ch_Prod_Acabado.setText(QCoreApplication.translate("Cad_Produtos", u"Produto Acabado", None))
        self.ch_Mat_Prima.setText(QCoreApplication.translate("Cad_Produtos", u"Mat\u00e9ria Prima", None))
        self.ch_Embalagem.setText(QCoreApplication.translate("Cad_Produtos", u"Embalagem", None))
    # retranslateUi

