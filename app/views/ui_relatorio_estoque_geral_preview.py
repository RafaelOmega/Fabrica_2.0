# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'relatorio_estoque_geral_previewpvqRfa.ui'
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
    QPushButton, QSizePolicy, QSpacerItem, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_Rel_Estoque_Geral_Preview(object):
    def setupUi(self, Rel_Estoque_Geral_Preview):
        if not Rel_Estoque_Geral_Preview.objectName():
            Rel_Estoque_Geral_Preview.setObjectName(u"Rel_Estoque_Geral_Preview")
        Rel_Estoque_Geral_Preview.resize(860, 600)
        Rel_Estoque_Geral_Preview.setMinimumSize(QSize(700, 500))
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Rel_Estoque_Geral_Preview.setFont(font)
        self.verticalLayout = QVBoxLayout(Rel_Estoque_Geral_Preview)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Visualizacao = QFrame(Rel_Estoque_Geral_Preview)
        self.frm_Visualizacao.setObjectName(u"frm_Visualizacao")
        self.frm_Visualizacao.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Visualizacao.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Visualizacao)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.txt_Visualizacao = QTextBrowser(self.frm_Visualizacao)
        self.txt_Visualizacao.setObjectName(u"txt_Visualizacao")

        self.verticalLayout_2.addWidget(self.txt_Visualizacao)


        self.verticalLayout.addWidget(self.frm_Visualizacao)

        self.frm_Botoes = QFrame(Rel_Estoque_Geral_Preview)
        self.frm_Botoes.setObjectName(u"frm_Botoes")
        self.frm_Botoes.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Botoes.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_Botoes)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.bt_PDF = QPushButton(self.frm_Botoes)
        self.bt_PDF.setObjectName(u"bt_PDF")
        self.bt_PDF.setMinimumSize(QSize(0, 30))

        self.horizontalLayout.addWidget(self.bt_PDF)

        self.bt_XLSX = QPushButton(self.frm_Botoes)
        self.bt_XLSX.setObjectName(u"bt_XLSX")
        self.bt_XLSX.setMinimumSize(QSize(0, 30))

        self.horizontalLayout.addWidget(self.bt_XLSX)

        self.bt_CSV = QPushButton(self.frm_Botoes)
        self.bt_CSV.setObjectName(u"bt_CSV")
        self.bt_CSV.setMinimumSize(QSize(0, 30))

        self.horizontalLayout.addWidget(self.bt_CSV)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.bt_Fechar = QPushButton(self.frm_Botoes)
        self.bt_Fechar.setObjectName(u"bt_Fechar")
        self.bt_Fechar.setMinimumSize(QSize(0, 30))

        self.horizontalLayout.addWidget(self.bt_Fechar)


        self.verticalLayout.addWidget(self.frm_Botoes)


        self.retranslateUi(Rel_Estoque_Geral_Preview)

        QMetaObject.connectSlotsByName(Rel_Estoque_Geral_Preview)
    # setupUi

    def retranslateUi(self, Rel_Estoque_Geral_Preview):
        Rel_Estoque_Geral_Preview.setWindowTitle(QCoreApplication.translate("Rel_Estoque_Geral_Preview", u"Pr\u00e9-visualiza\u00e7\u00e3o \u2014 Relat\u00f3rio de Estoque Geral", None))
        self.bt_PDF.setText(QCoreApplication.translate("Rel_Estoque_Geral_Preview", u"Gerar PDF", None))
        self.bt_XLSX.setText(QCoreApplication.translate("Rel_Estoque_Geral_Preview", u"Gerar XLSX", None))
        self.bt_CSV.setText(QCoreApplication.translate("Rel_Estoque_Geral_Preview", u"Gerar CSV", None))
        self.bt_Fechar.setText(QCoreApplication.translate("Rel_Estoque_Geral_Preview", u"Fechar", None))
    # retranslateUi

