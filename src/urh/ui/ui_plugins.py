# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plugins.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_FramePlugins(object):
    def setupUi(self, FramePlugins):
        if FramePlugins.objectName():
            FramePlugins.setObjectName(u"FramePlugins")
        FramePlugins.resize(806, 683)
        self.verticalLayout_3 = QVBoxLayout(FramePlugins)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(FramePlugins)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.listViewPlugins = QListView(FramePlugins)
        self.listViewPlugins.setObjectName(u"listViewPlugins")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listViewPlugins.sizePolicy().hasHeightForWidth())
        self.listViewPlugins.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.listViewPlugins)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(FramePlugins)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_2)

        self.txtEditPluginDescription = QTextEdit(FramePlugins)
        self.txtEditPluginDescription.setObjectName(u"txtEditPluginDescription")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.txtEditPluginDescription.sizePolicy().hasHeightForWidth())
        self.txtEditPluginDescription.setSizePolicy(sizePolicy2)
        self.txtEditPluginDescription.setReadOnly(True)

        self.verticalLayout.addWidget(self.txtEditPluginDescription)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.groupBoxSettings = QGroupBox(FramePlugins)
        self.groupBoxSettings.setObjectName(u"groupBoxSettings")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBoxSettings.sizePolicy().hasHeightForWidth())
        self.groupBoxSettings.setSizePolicy(sizePolicy3)
        self.groupBoxSettings.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_3.addWidget(self.groupBoxSettings)


        self.retranslateUi(FramePlugins)
    # setupUi

    def retranslateUi(self, FramePlugins):
        FramePlugins.setWindowTitle(QCoreApplication.translate("FramePlugins", u"Plugins", None))
        self.label.setText(QCoreApplication.translate("FramePlugins", u"Available Plugins", None))
        self.label_2.setText(QCoreApplication.translate("FramePlugins", u"Description", None))
        self.txtEditPluginDescription.setPlaceholderText("")
        self.groupBoxSettings.setTitle(QCoreApplication.translate("FramePlugins", u"Settings", None))
    # retranslateUi

