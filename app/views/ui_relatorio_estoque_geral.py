# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'relatorio_estoque_geralRPnFRX.ui'
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
from PySide6.QtWidgets import (QApplication, QDateEdit, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Rel_Estoque_Geral(object):
    def setupUi(self, Rel_Estoque_Geral):
        if not Rel_Estoque_Geral.objectName():
            Rel_Estoque_Geral.setObjectName(u"Rel_Estoque_Geral")
        Rel_Estoque_Geral.resize(460, 136)
        Rel_Estoque_Geral.setMinimumSize(QSize(460, 136))
        Rel_Estoque_Geral.setMaximumSize(QSize(460, 136))
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Rel_Estoque_Geral.setFont(font)
        self.horizontalLayout = QHBoxLayout(Rel_Estoque_Geral)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Relatorio = QFrame(Rel_Estoque_Geral)
        self.frm_Relatorio.setObjectName(u"frm_Relatorio")
        self.frm_Relatorio.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Relatorio.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Relatorio)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Datas = QFrame(self.frm_Relatorio)
        self.frm_Datas.setObjectName(u"frm_Datas")
        self.frm_Datas.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Datas.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Datas)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Data_Inicial = QLabel(self.frm_Datas)
        self.lb_Data_Inicial.setObjectName(u"lb_Data_Inicial")
        self.lb_Data_Inicial.setMinimumSize(QSize(0, 30))
        self.lb_Data_Inicial.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Data_Inicial)

        self.dt_Data_Inicial = QDateEdit(self.frm_Datas)
        self.dt_Data_Inicial.setObjectName(u"dt_Data_Inicial")
        self.dt_Data_Inicial.setMinimumSize(QSize(120, 30))
        self.dt_Data_Inicial.setMaximumSize(QSize(120, 30))
        self.dt_Data_Inicial.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dt_Data_Inicial)

        self.lb_Data_Final = QLabel(self.frm_Datas)
        self.lb_Data_Final.setObjectName(u"lb_Data_Final")
        self.lb_Data_Final.setMinimumSize(QSize(0, 30))
        self.lb_Data_Final.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Data_Final)

        self.dt_Data_Final = QDateEdit(self.frm_Datas)
        self.dt_Data_Final.setObjectName(u"dt_Data_Final")
        self.dt_Data_Final.setMinimumSize(QSize(120, 30))
        self.dt_Data_Final.setMaximumSize(QSize(120, 30))
        self.dt_Data_Final.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dt_Data_Final)

        self.horizontalSpacer = QSpacerItem(47, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frm_Datas)

        self.frm_Codigo = QFrame(self.frm_Relatorio)
        self.frm_Codigo.setObjectName(u"frm_Codigo")
        self.frm_Codigo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Codigo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Codigo)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Produto = QLabel(self.frm_Codigo)
        self.lb_Produto.setObjectName(u"lb_Produto")
        self.lb_Produto.setMinimumSize(QSize(0, 30))
        self.lb_Produto.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Produto)

        self.txt_Produto = QLineEdit(self.frm_Codigo)
        self.txt_Produto.setObjectName(u"txt_Produto")
        self.txt_Produto.setMinimumSize(QSize(0, 30))
        self.txt_Produto.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.txt_Produto)

        self.bt_Pesquisar_Produtos = QPushButton(self.frm_Codigo)
        self.bt_Pesquisar_Produtos.setObjectName(u"bt_Pesquisar_Produtos")
        self.bt_Pesquisar_Produtos.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Produtos.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisar_Produtos)


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


        self.retranslateUi(Rel_Estoque_Geral)

        QMetaObject.connectSlotsByName(Rel_Estoque_Geral)
    # setupUi

    def retranslateUi(self, Rel_Estoque_Geral):
        Rel_Estoque_Geral.setWindowTitle(QCoreApplication.translate("Rel_Estoque_Geral", u"Relat\u00f3rio de Estoque Geral", None))
        self.lb_Data_Inicial.setText(QCoreApplication.translate("Rel_Estoque_Geral", u"Data Inicial:", None))
        self.lb_Data_Final.setText(QCoreApplication.translate("Rel_Estoque_Geral", u"Data Final:", None))
        self.lb_Produto.setText(QCoreApplication.translate("Rel_Estoque_Geral", u"Produto:", None))
        self.bt_Pesquisar_Produtos.setText(QCoreApplication.translate("Rel_Estoque_Geral", u"...", None))
        self.bt_Filtrar.setText(QCoreApplication.translate("Rel_Estoque_Geral", u"Filtrar", None))
    # retranslateUi

