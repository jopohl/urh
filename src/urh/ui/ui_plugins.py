# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/joe/GIT/urh/data/ui/plugins.ui',
# licensing of '/home/joe/GIT/urh/data/ui/plugins.ui' applies.
#
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_FramePlugins(object):
    def setupUi(self, FramePlugins):
        FramePlugins.setObjectName("FramePlugins")
        FramePlugins.resize(806, 683)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(FramePlugins)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(FramePlugins)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.listViewPlugins = QtWidgets.QListView(FramePlugins)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listViewPlugins.sizePolicy().hasHeightForWidth())
        self.listViewPlugins.setSizePolicy(sizePolicy)
        self.listViewPlugins.setObjectName("listViewPlugins")
        self.verticalLayout_2.addWidget(self.listViewPlugins)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(FramePlugins)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.txtEditPluginDescription = QtWidgets.QTextEdit(FramePlugins)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtEditPluginDescription.sizePolicy().hasHeightForWidth())
        self.txtEditPluginDescription.setSizePolicy(sizePolicy)
        self.txtEditPluginDescription.setReadOnly(True)
        self.txtEditPluginDescription.setPlaceholderText("")
        self.txtEditPluginDescription.setObjectName("txtEditPluginDescription")
        self.verticalLayout.addWidget(self.txtEditPluginDescription)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.groupBoxSettings = QtWidgets.QGroupBox(FramePlugins)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxSettings.sizePolicy().hasHeightForWidth())
        self.groupBoxSettings.setSizePolicy(sizePolicy)
        self.groupBoxSettings.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBoxSettings.setObjectName("groupBoxSettings")
        self.verticalLayout_3.addWidget(self.groupBoxSettings)

        self.retranslateUi(FramePlugins)

    def retranslateUi(self, FramePlugins):
        FramePlugins.setWindowTitle(QtWidgets.QApplication.translate("FramePlugins", "Plugins", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("FramePlugins", "Available Plugins", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("FramePlugins", "Description", None, -1))
        self.groupBoxSettings.setTitle(QtWidgets.QApplication.translate("FramePlugins", "Settings", None, -1))

