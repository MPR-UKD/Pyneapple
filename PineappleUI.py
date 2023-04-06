import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from pathlib import Path
from utils import *
from PIL import ImageQt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class appData:
    def __init__(self):
        self.nii_img: nifti_img = nifti_img()
        self.nii_mask: nifti_img = nifti_img()
        self.nii_img_masked: nifti_img = nifti_img()
        self.nii_dyn: nifti_img = nifti_img()
        self.plt = plt_settings()


class plt_settings:
    def __init__(self):
        self.nslice: nslice = nslice(0)
        self.scaling: int = 4
        self.overlay: bool = False
        self.alpha: int = 126
        self.showPlt: bool = False
        self.qImg: QPixmap = None
        self.whichImg: str = "Img"
        self.pos = [10, 10]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, path: Path | str = None) -> None:
        super(MainWindow, self).__init__()
        self.data = appData()
        # initiate UI
        self._setupUI()
        # Connect Actions
        self._connectActions()
        # if function is UI ist initiated with a Path to a nifti load the nifti
        if path:
            self._loadImage(path)

    def _setupUI(self):
        # Window setting
        self.setMinimumSize(512, 512)
        self.setWindowTitle("Pineapple")
        img = Path(Path(__file__).parent, "resources", "Logo.png").__str__()
        self.setWindowIcon(QtGui.QIcon(img))
        self.mainWidget = QtWidgets.QWidget()

        # Menubar
        self._createMenuBar()

        # Main vertical Layout
        self.main_hLayout = QtWidgets.QHBoxLayout()
        self.main_vLayout = QtWidgets.QVBoxLayout()
        self.main_AX = QtWidgets.QLabel()
        self.main_AX.setPixmap(
            QtGui.QPixmap(
                Path(Path(__file__).parent, "resources", "noImage.png").__str__()
            )
        )
        self.main_AX.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # self.main_AX.setScaledContents(True)
        self.main_AX.installEventFilter(self)
        self.main_vLayout.addWidget(self.main_AX)
        self.SliceHlayout = QtWidgets.QHBoxLayout()
        # Slider
        self.SliceSldr = QtWidgets.QSlider()
        self.SliceSldr.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.SliceSldr.setEnabled(False)
        self.SliceSldr.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.SliceSldr.setTickInterval(1)
        self.SliceSldr.setMinimum(1)
        self.SliceSldr.setMaximum(20)
        self.SliceHlayout.addWidget(self.SliceSldr)
        # SpinBox
        self.SliceSpnBx = QtWidgets.QSpinBox()
        self.SliceSpnBx.setValue(1)
        self.SliceSpnBx.setEnabled(False)
        self.SliceSpnBx.setMinimumWidth(20)
        self.SliceSpnBx.setMaximumWidth(40)
        self.SliceHlayout.addWidget(self.SliceSpnBx)
        self.main_vLayout.addLayout(self.SliceHlayout)

        # Plotting Frame
        self.figure = Figure()
        self.figCanvas = FigureCanvas(self.figure)
        self.figAX = self.figure.add_subplot(111)
        self.figAX.set_xscale("log")
        self.figAX.set_xlabel("D (mm²/s)")

        self.main_hLayout.addLayout(self.main_vLayout)
        self.mainWidget.setLayout(self.main_hLayout)

        self.setCentralWidget(self.mainWidget)

        # StatusBar
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)

    def _createMenuBar(self):
        # Setup Menubar
        menuBar = self.menuBar()
        # File Menu
        fileMenu = QtWidgets.QMenu("&File", self)
        self.loadImage = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Image...",
            self,
        )
        self.loadMask = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Mask...",
            self,
        )
        self.loadDyn = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Dynamic Image...",
            self,
        )
        self.saveImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Image...",
            self,
        )
        self.saveMaskedImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Masked Image...",
            self,
        )
        self.saveMaskedImage.setEnabled(False)
        fileMenu.addAction(self.loadImage)
        fileMenu.addAction(self.loadMask)
        fileMenu.addAction(self.loadDyn)
        fileMenu.addSeparator()
        fileMenu.addAction(self.saveImage)
        fileMenu.addAction(self.saveMaskedImage)
        menuBar.addMenu(fileMenu)

        # Edit Menu
        editMenu = QtWidgets.QMenu("&Edit", self)
        MaskMenu = QtWidgets.QMenu("&Mask Tools", self)
        OrientationMenu = QtWidgets.QMenu("&Orientation", self)
        self.rotMask = QtGui.QAction("&Rotate Mask clockwise", self)
        self.rotMask.setEnabled(False)
        OrientationMenu.addAction(self.rotMask)
        self.maskFlipUpDown = QtGui.QAction("Flip Mask Up-Down", self)
        self.maskFlipUpDown.setEnabled(False)
        OrientationMenu.addAction(self.maskFlipUpDown)
        self.maskFlipLeftRight = QtGui.QAction("Flip Mask Left-Right", self)
        self.maskFlipLeftRight.setEnabled(False)
        OrientationMenu.addAction(self.maskFlipLeftRight)
        MaskMenu.addMenu(OrientationMenu)
        self.mask2img = QtGui.QAction("&Apply on Image", self)
        self.mask2img.setEnabled(False)
        MaskMenu.addAction(self.mask2img)
        editMenu.addMenu(MaskMenu)
        menuBar.addMenu(editMenu)

        # Fitting Menu
        fitMenu = QtWidgets.QMenu("&Fitting", self)
        fitMenu.setEnabled(False)
        menuBar.addMenu(fitMenu)

        # View Menu
        viewMenu = QtWidgets.QMenu("&View", self)
        imageMenu = QtWidgets.QMenu("Switch Image", self)
        self.plt_showImg = QtGui.QAction("Image", self)
        # imageMenu.addAction(self.plt_showImg)
        self.plt_showMask = QtGui.QAction("Mask", self)
        # imageMenu.addAction(self.plt_showMask)
        self.plt_showMaskedImage = QtGui.QAction("Image with applied Mask")
        self.plt_showMaskedImage.setEnabled(False)
        self.plt_showMaskedImage.setCheckable(True)
        self.plt_showMaskedImage.setChecked(False)
        imageMenu.addAction(self.plt_showMaskedImage)
        self.plt_showDyn = QtGui.QAction("Dynamic", self)
        # imageMenu.addAction(self.plt_showDyn)
        viewMenu.addMenu(imageMenu)
        self.plt_show = QtGui.QAction("Show Plot")
        self.plt_show.setEnabled(True)
        viewMenu.addAction(self.plt_show)
        self.plt_overlay = QtGui.QAction("Show Mask Overlay", self)
        self.plt_overlay.setEnabled(False)
        self.plt_overlay.setCheckable(True)
        self.plt_overlay.setChecked(False)
        viewMenu.addAction(self.plt_overlay)
        menuBar.addMenu(viewMenu)

        evalMenu = QtWidgets.QMenu("Evaluation", self)
        evalMenu.setEnabled(False)
        menuBar.addMenu(evalMenu)

    def _connectActions(self):
        self.loadImage.triggered.connect(self._loadImage)
        self.loadMask.triggered.connect(self._loadMask)
        self.loadDyn.triggered.connect(self._loadDyn)
        self.saveImage.triggered.connect(self._saveImage)
        self.saveMaskedImage.triggered.connect(self._saveMaskedImage)
        self.SliceSldr.valueChanged.connect(self._SliceSldrChanged)
        self.SliceSpnBx.valueChanged.connect(self._SliceSpnBxChanged)
        self.maskFlipUpDown.triggered.connect(self._maskFlipUpDown)
        self.maskFlipLeftRight.triggered.connect(self._maskFlipLeftRight)
        self.mask2img.triggered.connect(self._mask2img)
        self.plt_showImg.triggered.connect(lambda x: self._switchImage("Img"))
        self.plt_showMask.triggered.connect(lambda x: self._switchImage("Mask"))
        self.plt_showDyn.triggered.connect(lambda x: self._switchImage("Dyn"))
        self.plt_show.triggered.connect(self._plt_show)
        self.plt_overlay.toggled.connect(self._plt_overlay)
        self.plt_showMaskedImage.toggled.connect(self._plt_showMaskedImage)

    def eventFilter(self, source, event):
        if source == self.main_AX:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                if self.data.nii_img.path:
                    self.data.plt.pos = plotting.lbl2np(
                        event.pos().x(),
                        event.pos().y(),
                        self.data.nii_img.size[1],
                        self.data.plt.scaling,
                    )
                    self.statusBar.showMessage(
                        "(%d, %d)" % (self.data.plt.pos[0], self.data.plt.pos[1])
                    )
                    if self.data.plt.showPlt:
                        plotting.showSpectrum(self.figAX, self.figCanvas, self.data)

        return super().eventFilter(source, event)

    def _loadImage(self, path: Path | str = None):
        if not path:
            path = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open Image", "", "NifTi (*.nii *.nii.gz)"
            )[0]
        file = Path(path) if path else None
        self.data.nii_img = nifti_img(file)
        if self.data.nii_img.path is not None:
            self.data.plt.nslice.number = self.SliceSldr.value()
            self.SliceSldr.setEnabled(True)
            self.SliceSldr.setMaximum(self.data.nii_img.size[2])
            self.SliceSpnBx.setEnabled(True)
            self.SliceSpnBx.setMaximum(self.data.nii_img.size[2])
            self.setupImage()
            self.mask2img.setEnabled(True if self.data.nii_mask.path else False)
            self.plt_overlay.setEnabled(True if self.data.nii_mask.path else False)

    def _loadMask(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Mask Image", "", "NifTi (*.nii *.nii.gz)"
        )[0]
        file = Path(path) if path else None
        self.data.nii_mask = nifti_img(file)
        if self.data.nii_mask:
            self.data.nii_mask.mask = True
            self.mask2img.setEnabled(True if self.data.nii_mask.path else False)
            self.plt_overlay.setEnabled(True if self.data.nii_mask.path else False)
            self.maskFlipUpDown.setEnabled(True)
            self.maskFlipLeftRight.setEnabled(True)

    def _loadDyn(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Dynamic Image", "", "NifTi (*.nii *.nii.gz)"
        )[0]
        file = Path(path) if path else None
        self.data.nii_dyn = nifti_img(file)
        if self.data.plt.showPlt:
            plotting.showSpectrum(self.figAX, self.figCanvas, self.data)

    def _saveImage(self):
        fname = self.data.nii_img.path
        file = Path(
            QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save Image",
                fname.__str__(),
                "NifTi (*.nii *.nii.gz)",
            )[0]
        )
        self.data.nii_img.save(file)

    def _saveMaskedImage(self):
        fname = self.data.nii_img.path
        fname = Path(str(fname).replace(fname.stem, fname.stem + "_masked"))
        file = Path(
            QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save Masked Image",
                fname.__str__(),
                "NifTi (*.nii *.nii.gz)",
            )[0]
        )
        self.data.nii_img_masked.save(file)

    def _maskFlipUpDown(self):
        # Images are rotated 90 degrees so lr and ud are switched
        self.data.nii_mask.array = np.fliplr(self.data.nii_mask.array)
        self.setupImage()

    def _maskFlipLeftRight(self):
        # Images are rotated 90 degrees so lr and ud are switched
        self.data.nii_mask.array = np.flipud(self.data.nii_mask.array)
        self.setupImage()

    def _mask2img(self):
        self.data.nii_img_masked = processing.mergeNiiImages(
            self.data.nii_img, self.data.nii_mask
        )
        if self.data.nii_img_masked:
            self.plt_showMaskedImage.setEnabled(True)
            self.saveMaskedImage.setEnabled(True)

    def _switchImage(self, which: str = "Img"):
        self.data.plt.whichImg = which
        self.setupImage()

    def _plt_show(self):
        if self.data.plt.showPlt:
            self.figCanvas.setParent(None)
            self.figure.set_visible(False)
            self.data.plt.showPlt = False
        else:
            self.main_hLayout.addWidget(self.figCanvas)
            self.data.plt.showPlt = True
        self.resizeMainWindow()

    def _plt_overlay(self):
        self.setupImage()

    def _plt_showMaskedImage(self):
        if self.plt_showMaskedImage.isChecked():
            self.plt_overlay.setChecked(False)
            self.plt_overlay.setEnabled(False)
            self.setupImage()
        else:
            self.plt_overlay.setEnabled(True)
            self.setupImage()

    def _SliceSldrChanged(self):
        self.data.plt.nslice.number = self.SliceSldr.value()
        self.SliceSpnBx.setValue(self.SliceSldr.value())
        self.setupImage()

    def _SliceSpnBxChanged(self):
        self.data.plt.nslice.number = self.SliceSpnBx.value()
        self.SliceSldr.setValue(self.SliceSpnBx.value())
        self.setupImage()

    def setupImage(self):
        nslice = self.data.plt.nslice.value
        scaling = self.data.plt.scaling
        if not self.plt_showMaskedImage.isChecked():
            self.data.plt.nslice.number = self.SliceSldr.value()
            if (
                self.plt_overlay.isChecked()
                and self.data.nii_img.path
                and self.data.nii_mask.path
            ):
                img = plotting.overlayImage(
                    self.data.nii_img,
                    self.data.nii_mask,
                    nslice,
                    self.data.plt.alpha,
                    scaling,
                )
                self.data.plt.qImg = QPixmap.fromImage(ImageQt.ImageQt(img))
            else:
                self.plt_overlay.setChecked(False)
                # self.data.plt.qImg = self.data.nii_img.QPixmap(nslice, scaling)
                self.data.plt.qImg = self.showImage().QPixmap(nslice, scaling)
        elif self.plt_showMaskedImage.isChecked():
            self.data.plt.qImg = self.data.nii_img_masked.QPixmap(nslice, scaling)
        if self.data.plt.qImg:
            self.main_AX.setPixmap(self.data.plt.qImg)
            # self.main_AX.setMinimumSize(self.data.plt.qImg.size())
            self.SliceSldr.setMaximumWidth(
                self.data.plt.qImg.width() - self.SliceSpnBx.maximumWidth()
            )
        self.resizeMainWindow()

    def showImage(self):
        if self.data.plt.whichImg == "Img":
            return self.data.nii_img
        elif self.data.plt.whichImg == "Mask":
            return self.data.nii_mask
        elif self.data.plt.whichImg == "Dyn":
            return self.data.nii_dyn

    def resizeMainWindow(self):
        if self.data.plt.qImg:
            if not self.data.plt.showPlt:
                self.setMinimumHeight(
                    self.data.plt.qImg.height()
                    + self.SliceSldr.height()
                    + self.statusBar.height()
                )
            else:
                # width = self.main_AX.width()
                width = self.main_AX.width() + 300
                height = self.data.plt.qImg.height()
                self.setMinimumSize(QtCore.QSize(width, height))
        else:
            self.setMinimumWidth(self.main_AX.width() * 2)


def startAppUI(path: Path | str = None):
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(path)  # QtWidgets.QWidget()
    window.show()
    app.exec()
    # sys.exit(app.exec())


startAppUI()

# # Start App, parse path if given
# argv = sys.argv[1:]
# if len(argv) > 0:
#     startPineappleUI(argv[0])
# else:
#     startPineappleUI()
