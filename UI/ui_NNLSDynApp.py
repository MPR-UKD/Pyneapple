# Form implementation generated from reading ui file 'd:\home\Thomas\Documents\Python\NNLSDynApp\UI\NNLSDynApp.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1010, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1010, 500))
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 994, 431))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.RightSidePanel = QtWidgets.QVBoxLayout()
        self.RightSidePanel.setObjectName("RightSidePanel")
        self.Lbl_PltStyle = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.Lbl_PltStyle.setObjectName("Lbl_PltStyle")
        self.RightSidePanel.addWidget(self.Lbl_PltStyle)
        self.cmbBox_PltStyle = QtWidgets.QComboBox(parent=self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbBox_PltStyle.sizePolicy().hasHeightForWidth())
        self.cmbBox_PltStyle.setSizePolicy(sizePolicy)
        self.cmbBox_PltStyle.setMinimumSize(QtCore.QSize(70, 25))
        self.cmbBox_PltStyle.setMaximumSize(QtCore.QSize(500, 25))
        self.cmbBox_PltStyle.setEditable(False)
        self.cmbBox_PltStyle.setCurrentText("")
        self.cmbBox_PltStyle.setObjectName("cmbBox_PltStyle")
        self.RightSidePanel.addWidget(self.cmbBox_PltStyle)
        self.line = QtWidgets.QFrame(parent=self.horizontalLayoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.RightSidePanel.addWidget(self.line)
        self.lbl_FittingBoundries = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.lbl_FittingBoundries.setObjectName("lbl_FittingBoundries")
        self.RightSidePanel.addWidget(self.lbl_FittingBoundries)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtEdt_BoundMin = QtWidgets.QTextEdit(parent=self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtEdt_BoundMin.sizePolicy().hasHeightForWidth())
        self.txtEdt_BoundMin.setSizePolicy(sizePolicy)
        self.txtEdt_BoundMin.setMaximumSize(QtCore.QSize(75, 25))
        self.txtEdt_BoundMin.setAcceptDrops(False)
        self.txtEdt_BoundMin.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferNumbers)
        self.txtEdt_BoundMin.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.txtEdt_BoundMin.setObjectName("txtEdt_BoundMin")
        self.horizontalLayout.addWidget(self.txtEdt_BoundMin)
        self.txtEdt_BoundMax = QtWidgets.QTextEdit(parent=self.horizontalLayoutWidget)
        self.txtEdt_BoundMax.setMaximumSize(QtCore.QSize(75, 25))
        self.txtEdt_BoundMax.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.txtEdt_BoundMax.setObjectName("txtEdt_BoundMax")
        self.horizontalLayout.addWidget(self.txtEdt_BoundMax)
        self.RightSidePanel.addLayout(self.horizontalLayout)
        self.line_2 = QtWidgets.QFrame(parent=self.horizontalLayoutWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.RightSidePanel.addWidget(self.line_2)
        self.vLayout_nSlice = QtWidgets.QVBoxLayout()
        self.vLayout_nSlice.setObjectName("vLayout_nSlice")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lbl_nSlice = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.lbl_nSlice.setObjectName("lbl_nSlice")
        self.horizontalLayout_3.addWidget(self.lbl_nSlice)
        self.spnBx_nSlice = QtWidgets.QSpinBox(parent=self.horizontalLayoutWidget)
        self.spnBx_nSlice.setEnabled(False)
        self.spnBx_nSlice.setMinimum(1)
        self.spnBx_nSlice.setObjectName("spnBx_nSlice")
        self.horizontalLayout_3.addWidget(self.spnBx_nSlice)
        self.vLayout_nSlice.addLayout(self.horizontalLayout_3)
        self.Sldr_nSlice = QtWidgets.QSlider(parent=self.horizontalLayoutWidget)
        self.Sldr_nSlice.setEnabled(False)
        self.Sldr_nSlice.setMinimum(1)
        self.Sldr_nSlice.setMaximum(100)
        self.Sldr_nSlice.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.Sldr_nSlice.setObjectName("Sldr_nSlice")
        self.vLayout_nSlice.addWidget(self.Sldr_nSlice)
        self.line_5 = QtWidgets.QFrame(parent=self.horizontalLayoutWidget)
        self.line_5.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_5.setObjectName("line_5")
        self.vLayout_nSlice.addWidget(self.line_5)
        self.pushButton = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.vLayout_nSlice.addWidget(self.pushButton)
        self.RightSidePanel.addLayout(self.vLayout_nSlice)
        spacerItem = QtWidgets.QSpacerItem(20, 120, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.RightSidePanel.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.RightSidePanel)
        self.line_3 = QtWidgets.QFrame(parent=self.horizontalLayoutWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_2.addWidget(self.line_3)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.BttnImgDynLoad = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.BttnImgDynLoad.setMinimumSize(QtCore.QSize(25, 0))
        self.BttnImgDynLoad.setMaximumSize(QtCore.QSize(50, 16777215))
        self.BttnImgDynLoad.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("d:\\home\\Thomas\\Documents\\Python\\NNLSDynApp\\UI\\resources/openFolder.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.BttnImgDynLoad.setIcon(icon)
        self.BttnImgDynLoad.setObjectName("BttnImgDynLoad")
        self.verticalLayout.addWidget(self.BttnImgDynLoad)
        self.BttnImgDynRotate = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.BttnImgDynRotate.setMaximumSize(QtCore.QSize(50, 16777215))
        self.BttnImgDynRotate.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("d:\\home\\Thomas\\Documents\\Python\\NNLSDynApp\\UI\\resources/rot90.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.BttnImgDynRotate.setIcon(icon1)
        self.BttnImgDynRotate.setObjectName("BttnImgDynRotate")
        self.verticalLayout.addWidget(self.BttnImgDynRotate)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.AXImgDyn = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.AXImgDyn.setMinimumSize(QtCore.QSize(256, 256))
        self.AXImgDyn.setMaximumSize(QtCore.QSize(512, 512))
        self.AXImgDyn.setText("")
        self.AXImgDyn.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.AXImgDyn.setObjectName("AXImgDyn")
        self.horizontalLayout_2.addWidget(self.AXImgDyn)
        self.line_4 = QtWidgets.QFrame(parent=self.horizontalLayoutWidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_2.addWidget(self.line_4)
        self.AXPltDyn = QtWidgets.QGraphicsView(parent=self.horizontalLayoutWidget)
        self.AXPltDyn.setMinimumSize(QtCore.QSize(512, 256))
        self.AXPltDyn.setObjectName("AXPltDyn")
        self.horizontalLayout_2.addWidget(self.AXPltDyn)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1010, 25))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(parent=self.menubar)
        self.menu_File.setObjectName("menu_File")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Open = QtGui.QAction(parent=MainWindow)
        self.action_Open.setObjectName("action_Open")
        self.actionOpen_Image = QtGui.QAction(parent=MainWindow)
        self.actionOpen_Image.setObjectName("actionOpen_Image")
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.actionOpen_Image)
        self.menubar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MainWindow)
        self.cmbBox_PltStyle.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Lbl_PltStyle.setText(_translate("MainWindow", "Plot Style"))
        self.cmbBox_PltStyle.setPlaceholderText(_translate("MainWindow", "Spectrum", "Spectrum"))
        self.lbl_FittingBoundries.setText(_translate("MainWindow", "Fitting Boundries:"))
        self.txtEdt_BoundMin.setPlaceholderText(_translate("MainWindow", "0.0001"))
        self.txtEdt_BoundMax.setPlaceholderText(_translate("MainWindow", "0.2"))
        self.lbl_nSlice.setText(_translate("MainWindow", "Slice:"))
        self.pushButton.setText(_translate("MainWindow", "Refresh Images"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.action_Open.setText(_translate("MainWindow", "&Open Dyn"))
        self.actionOpen_Image.setText(_translate("MainWindow", "Open Image"))
