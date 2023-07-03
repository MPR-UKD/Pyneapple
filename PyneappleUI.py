import sys, os
import typing
from PyQt6 import QtWidgets, QtGui, QtCore
from pathlib import Path

from PyQt6.QtWidgets import QWidget
from utils import *
from fit import *
from plotting import Plotting
from PIL import ImageQt
from multiprocessing import freeze_support
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# v0.4.2


class appData:
    def __init__(self):
        self.nii_img: Nii = Nii()
        self.nii_seg: Nii_seg = Nii_seg()
        self.nii_img_masked: Nii = Nii()
        self.nii_dyn: Nii = Nii()
        self.plt = self._pltSettings()
        self.fit = self._fitData()

    class _pltSettings:
        def __init__(self):
            self.nslice: NSlice = NSlice(0)
            self.alpha: int = 0.5

    class _fitData:
        def __init__(self):
            self.NNLS = FitData("NNLS")
            self.NNLSreg = FitData("NNLSreg")
            self.NNLSregCV = FitData("NNLSregCV")
            self.mono = FitData("mono")
            self.mono_t1 = FitData("mono_T1")


class SettingsWidget(QtWidgets.QHBoxLayout):    
    def __init__(self, name: str, default: int | float | np.ndarray, value_range: list):
        super().__init__()
        self.default = default
        self.value = default
        self.value_range = value_range 
        self.addWidget(QtWidgets.QLabel(name + ":"))
        self.edit_field = QtWidgets.QTextEdit()
        self.edit_field.setText(str(default))
        self.edit_field.textChanged.connect(self._text_changed)
        # self.edit_field.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.edit_field.setMaximumHeight(28)
        self.addWidget(self.edit_field) 

    def _text_changed(self):
        self.value(self.edit_field.toPlainText())

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if type(self.default) == {int, float}:
            value = type(self.default)(value)
        elif type(self.default) == np.ndarray:
            value = np.fromstring(value) 
        # TODO: range implementation
        # if value < self.value_range[0] or value > self.value_range[1]:
        #     self.__value = self.default
        #     print("Value exceded value range.")
        # else:
        #     self.__value = value
        self.__value = value

class FittingWindow(QtWidgets.QWidget):
    def __init__(self, name: str, fitting_dict: dict) -> None:
        super().__init__()
        self.setWindowTitle("Fitting "+ name)
        # self.setWindowIcon(QtGui.QIcon(img))
        self.setMinimumSize(192, 64)
        self.main_layout = QtWidgets.QVBoxLayout()
        for key in fitting_dict:
            self.main_layout.addLayout(fitting_dict[key])
        
        self.setLayout(self.main_layout)

class SettingsWindow(QtWidgets.QWidget):
        def __init__(self, parent:QtWidgets.QMainWindow, settings: QtCore.QSettings) -> None:
            super().__init__()
            
            self.settings = settings
            self.setWindowTitle("Settings")
            # self.setWindowIcon(QtGui.QIcon(img))

            # TODO: Would be nice to center  
            # geometry = self.geometry() 
            # geometry.moveCenter(parent.geometry().center())
            # self.setGeometry(geometry)
            self.setMinimumSize(192, 64)

            self.main_layout = QtWidgets.QVBoxLayout()

            general_label = QtWidgets.QLabel("General:")
            self.main_layout.addWidget(general_label)
            general_line = QtWidgets.QFrame()
            general_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            general_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            self.main_layout.addWidget(general_line)   

            self.theme_layout = QtWidgets.QHBoxLayout()
            theme_label = QtWidgets.QLabel("Theme:")  
            self.theme_layout.addWidget(theme_label)
            self.theme_combobox = QtWidgets.QComboBox()
            self.theme_combobox.addItems(["Dark","Light"])
            self.theme_combobox.setCurrentText(settings.value("theme"))            
            self.theme_combobox.currentIndexChanged.connect(self._theme_changed)
            self.theme_layout.addWidget(self.theme_combobox)

            self.main_layout.addLayout(self.theme_layout)
            # self.theme_combobox.setItem

            self.setLayout(self.main_layout)
        
        def _theme_changed(self):
            self.settings.setValue("theme", self.theme_combobox.currentText())

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, path: Path | str = None) -> None:
        super(MainWindow, self).__init__()
        self.data = appData()

        # Load Settings
        self._load_settings()
        
        # initiate UI
        self._setupUI()

        if path:
            self._load_image(path)

    def _load_settings(self):
        self.settings = QtCore.QSettings("MyApp", "Pyneapple")
        if self.settings.value("last_dir","") == "":
            self.settings.setValue("last_dir",os.path.abspath(__file__))
            self.settings.setValue("theme","Light") # "Dark", "Light"
            self.settings.setValue("plt_show", False)



    def _setupUI(self):
        # ----- Window setting
        self.setMinimumSize(512, 512)
        self.setWindowTitle("Pyneapple")
        img = Path(Path(__file__).parent, "resources", "Logo.png").__str__()
        self.setWindowIcon(QtGui.QIcon(img))
        self.mainWidget = QtWidgets.QWidget()

        # ----- Menubar
        self._createMenuBar()

        # ----- Context Menu
        self._createContextMenu()

        # ----- Main vertical Layout
        self.main_hLayout = QtWidgets.QHBoxLayout()  # Main horzizontal Layout
        self.main_vLayout = QtWidgets.QVBoxLayout()  # Main Layout for img ans slider

        # ----- Main Image Axis
        self.img_fig = Figure()
        self.img_canvas = FigureCanvas(self.img_fig)
        self.img_ax = self.img_fig.add_subplot(111)
        self.img_ax.axis("off")
        self.main_vLayout.addWidget(self.img_canvas)
        self.img_fig.canvas.mpl_connect("button_press_event", self.event_filter)

        self.img_ax.clear()

        if self.settings.value("theme") == "Dark":
            self.img_ax.imshow(
                np.array(
                    Image.open(
                        # Path(Path(__file__).parent, "resources", "noImage_white.png")
                        Path(Path(__file__).parent, "resources", "PyneAppleLogo_gray.png")
                    )
                ),
                cmap="gray",
            )
            self.img_fig.set_facecolor("black")
        elif self.settings.value("theme") == "Light":
            self.img_ax.imshow(
                np.array(
                    Image.open(
                        Path(Path(__file__).parent, "resources", "noImage.png")
                        # Path(Path(__file__).parent, "resources", "PyNeapple_BW_JJ.png")
                    )
                ),
                cmap="gray",
            )
        self.img_ax.axis("off")
        self._resize_figure_axis()
        self.img_canvas.draw()

        # ----- Slider
        self.SliceHlayout = QtWidgets.QHBoxLayout()  # Layout for Slider ans Spinbox
        self.SliceSldr = QtWidgets.QSlider()
        self.SliceSldr.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.SliceSldr.setEnabled(False)
        self.SliceSldr.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.SliceSldr.setTickInterval(1)
        self.SliceSldr.setMinimum(1)
        self.SliceSldr.setMaximum(20)
        self.SliceSldr.valueChanged.connect(self._SliceSldrChanged)
        self.SliceHlayout.addWidget(self.SliceSldr)

        # ----- SpinBox
        self.SliceSpnBx = QtWidgets.QSpinBox()
        self.SliceSpnBx.setValue(1)
        self.SliceSpnBx.setEnabled(False)
        self.SliceSpnBx.setMinimumWidth(20) 
        self.SliceSpnBx.setMaximumWidth(40)
        self.SliceSpnBx.valueChanged.connect(self._SliceSpnBxChanged)
        self.SliceHlayout.addWidget(self.SliceSpnBx)

        self.main_vLayout.addLayout(self.SliceHlayout)

        # ----- Plotting Frame
        self.plt_fig = Figure()
        self.plt_canvas = FigureCanvas(self.plt_fig)
        self.plt_AX = self.plt_fig.add_subplot(111)
        self.plt_AX.set_xscale("log")
        self.plt_AX.set_xlabel("D (mm²/s)")

        self.main_hLayout.addLayout(self.main_vLayout)
        self.mainWidget.setLayout(self.main_hLayout)

        self.setCentralWidget(self.mainWidget)

        # ----- StatusBar
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)

    def _createMenuBar(self):

        # ----- Setup Menubar

        menuBar = self.menuBar()

        # ----- File Menu
        fileMenu = QtWidgets.QMenu("&File", self)
        self.loadImage = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Image...",
            self,
        )
        self.loadImage.triggered.connect(self._load_image)
        fileMenu.addAction(self.loadImage)

        self.loadSeg = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Segmentation...",
            self,
        )
        self.loadSeg.triggered.connect(self._load_seg)
        fileMenu.addAction(self.loadSeg)

        self.loadDyn = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Dynamic Image...",
            self,
        )
        self.loadDyn.triggered.connect(self._load_dyn)
        fileMenu.addAction(self.loadDyn)
        fileMenu.addSeparator()

        self.saveImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Image...",
            self,
        )
        self.saveImage.triggered.connect(self._save_image)
        fileMenu.addAction(self.saveImage)

        self.saveFitImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Fit to NifTi...",
            self,
        )
        self.saveFitImage.setEnabled(False)
        self.saveFitImage.triggered.connect(self._save_fit_image)
        fileMenu.addAction(self.saveFitImage)

        self.saveMaskedImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Masked Image...",
            self,
        )
        self.saveMaskedImage.setEnabled(False)
        self.saveMaskedImage.triggered.connect(self._save_masked_image)
        fileMenu.addAction(self.saveMaskedImage)

        fileMenu.addSeparator()
        
        self.open_settings_dlg = QtGui.QAction(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton), "Settings...",self)
        self.open_settings_dlg.setEnabled(True)
        self.open_settings_dlg.triggered.connect(self._open_settings_dlg)
        fileMenu.addAction(self.open_settings_dlg)

        menuBar.addMenu(fileMenu)

        # ----- Edit Menu
        editMenu = QtWidgets.QMenu("&Edit", self)
        MaskMenu = QtWidgets.QMenu("&Mask Tools", self)

        OrientationMenu = QtWidgets.QMenu("&Orientation", self)
        self.rotMask = QtGui.QAction("&Rotate Mask clockwise", self)
        self.rotMask.setEnabled(False)
        OrientationMenu.addAction(self.rotMask)

        self.maskFlipUpDown = QtGui.QAction("Flip Mask Up-Down", self)
        self.maskFlipUpDown.setEnabled(False)
        self.maskFlipUpDown.triggered.connect(self._mask_flip_up_down)
        OrientationMenu.addAction(self.maskFlipUpDown)

        self.maskFlipLeftRight = QtGui.QAction("Flip Mask Left-Right", self)
        self.maskFlipLeftRight.setEnabled(False)
        self.maskFlipLeftRight.triggered.connect(self._mask_flip_left_right)
        OrientationMenu.addAction(self.maskFlipLeftRight)

        self.maskFlipBackForth = QtGui.QAction("Flip Mask Back-Forth", self)
        self.maskFlipBackForth.setEnabled(False)
        self.maskFlipBackForth.triggered.connect(self._mask_flip_back_forth)
        OrientationMenu.addAction(self.maskFlipBackForth)

        MaskMenu.addMenu(OrientationMenu)

        self.mask2img = QtGui.QAction("&Apply on Image", self)
        self.mask2img.setEnabled(False)
        self.mask2img.triggered.connect(self._mask2img)
        MaskMenu.addAction(self.mask2img)

        editMenu.addMenu(MaskMenu)
        menuBar.addMenu(editMenu)

        # ----- Fitting Menu
        fitMenu = QtWidgets.QMenu("&Fitting", self)
        fitMenu.setEnabled(True)

        # ----- NNLS
        nnlsMenu = QtWidgets.QMenu("NNLS", self)
        self.fit_NNLS = QtGui.QAction("NNLS", self)
        self.fit_NNLS.triggered.connect(lambda x: self._fit_NNLS("NNLS"))
        nnlsMenu.addAction(self.fit_NNLS)

        self.fit_NNLSreg = QtGui.QAction("NNLS with regularisation", self)
        self.fit_NNLSreg.setEnabled(True)
        self.fit_NNLSreg.triggered.connect(lambda x: self._fit_NNLS("NNLSreg"))
        nnlsMenu.addAction(self.fit_NNLSreg)

        self.fit_NNLSregCV = QtGui.QAction("NNLS with regularisation by CV", self)
        self.fit_NNLSregCV.setEnabled(True)
        self.fit_NNLSregCV.triggered.connect(lambda x: self._fit_NNLS("NNLSregCV"))
        nnlsMenu.addAction(self.fit_NNLSregCV)
        
        fitMenu.addMenu(nnlsMenu)

        # ----- Mono / ADC
        monoMenu = QtWidgets.QMenu("Mono Exponential", self)
        self.fit_mono = QtGui.QAction("Monoexponential", self)
        self.fit_mono.triggered.connect(lambda x: self._fit_mono("mono"))
        monoMenu.addAction(self.fit_mono)

        self.fit_mono_t1 = QtGui.QAction("Monoexponential with T1", self)
        self.fit_mono_t1.triggered.connect(lambda x: self._fit_mono("mono_t1"))
        monoMenu.addAction(self.fit_mono_t1)
        # monoMenu.setEnabled(False)
        fitMenu.addMenu(monoMenu)
        menuBar.addMenu(fitMenu)

        # ----- View Menu
        viewMenu = QtWidgets.QMenu("&View", self)
        imageMenu = QtWidgets.QMenu("Switch Image", self)
        self.plt_showImg = QtGui.QAction("Image", self)
        self.plt_showImg.triggered.connect(lambda x: self._switchImage("Img"))
        # imageMenu.addAction(self.plt_showImg)

        self.plt_showMask = QtGui.QAction("Mask", self)
        self.plt_showMask.triggered.connect(lambda x: self._switchImage("Mask"))
        # imageMenu.addAction(self.plt_showMask)

        self.plt_showMaskedImage = QtGui.QAction("Image with applied Mask")
        self.plt_showMaskedImage.setEnabled(False)
        self.plt_showMaskedImage.setCheckable(True)
        self.plt_showMaskedImage.setChecked(False)
        self.plt_showMaskedImage.toggled.connect(self._plt_showMaskedImage)
        imageMenu.addAction(self.plt_showMaskedImage)

        self.plt_showDyn = QtGui.QAction("Dynamic", self)
        self.plt_showDyn.triggered.connect(lambda x: self._switchImage("Dyn"))
        # imageMenu.addAction(self.plt_showDyn)
        viewMenu.addMenu(imageMenu)

        self.plt_show = QtGui.QAction("Show Plot")
        self.plt_show.setEnabled(True)
        self.plt_show.setCheckable(True)
        self.plt_show.triggered.connect(self._plt_show)
        viewMenu.addAction(self.plt_show)
        viewMenu.addSeparator()

        self.plt_DispType_SingleVoxel = QtGui.QAction(
            "Show Single Voxel Spectrum", self
        )
        self.plt_DispType_SingleVoxel.setCheckable(True)
        self.plt_DispType_SingleVoxel.setChecked(True)
        self.settings.setValue("plt_disp_type", "single_voxel")
        self.plt_DispType_SingleVoxel.toggled.connect(
            lambda x: self._switchPlt("single_voxel")
        )
        viewMenu.addAction(self.plt_DispType_SingleVoxel)

        self.plt_DispType_SegSpectrum = QtGui.QAction(
            "Show Segmentation Spectrum", self
        )
        self.plt_DispType_SegSpectrum.setCheckable(True)
        self.plt_DispType_SegSpectrum.toggled.connect(
            lambda x: self._switchPlt("seg_spectrum")
        )
        viewMenu.addAction(self.plt_DispType_SegSpectrum)
        viewMenu.addSeparator()

        self.img_overlay = QtGui.QAction("Show Mask Overlay", self)
        self.img_overlay.setEnabled(False)
        self.img_overlay.setCheckable(True)
        self.img_overlay.setChecked(False)
        self.settings.setValue("img_disp_overlay", True)
        self.img_overlay.toggled.connect(self._img_overlay)
        viewMenu.addAction(self.img_overlay)
        menuBar.addMenu(viewMenu)

        evalMenu = QtWidgets.QMenu("Evaluation", self)
        evalMenu.setEnabled(False)
        # menuBar.addMenu(evalMenu)

    def _createContextMenu(self):
        self.contextMenu = QtWidgets.QMenu(self)
        pltMenu = QtWidgets.QMenu("Plotting", self)
        pltMenu.addAction(self.plt_show)
        pltMenu.addSeparator()

        pltMenu.addAction(self.plt_DispType_SingleVoxel)

        pltMenu.addAction(self.plt_DispType_SegSpectrum)

        self.contextMenu.addMenu(pltMenu)

    ## Events

    def event_filter(self, event):
        if event.button == 1:
            # left mouse button
            if self.data.nii_img.path:
                if event.xdata and event.ydata:
                    # check if point is on image
                    position_data = [round(event.xdata), round(event.ydata)]
                    self.statusBar.showMessage(
                        "(%d, %d)" % (position_data[0], position_data[1])
                    )
                    if self.settings.value("plt_show", type=bool):
                        if (
                            self.settings.value("plt_disp_type", type=str)
                            == "single_voxel"
                        ):
                            Plotting.show_pixel_spectrum(
                                self.plt_AX, self.plt_canvas, self.data, position_data
                            )
                        elif (
                            self.settings.value("plt_disp_type", type=str)
                            == "seg_spectrum"
                        ):
                            Plotting.show_seg_spectrum(
                                self.plt_AX, self.plt_canvas, self.data, 0
                            )

    def contextMenuEvent(self, event):
        self.contextMenu.popup(QtGui.QCursor.pos())

    def resizeEvent(self, event):
        self._resize_figure_axis()

    ## App Callbacks

    def _load_image(self, path: Path | str = None):
        if not path:
            path = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open Image", "", "NifTi (*.nii *.nii.gz)"
            )[0]
        if path:
            file = Path(path) if path else None
            self.data.nii_img = Nii(file)
            if self.data.nii_img.path is not None:
                self.data.plt.nslice.number = self.SliceSldr.value()
                self.SliceSldr.setEnabled(True)
                self.SliceSldr.setMaximum(self.data.nii_img.array.shape[2])
                self.SliceSpnBx.setEnabled(True)
                self.SliceSpnBx.setMaximum(self.data.nii_img.array.shape[2])
                self.settings.setValue("img_disp_type", "Img")
                self.setup_image()
                self.mask2img.setEnabled(True if self.data.nii_seg.path else False)
                self.img_overlay.setEnabled(True if self.data.nii_seg.path else False)
        else:
            print("Warning no file selcted")
    def _load_seg(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Mask Image", "", "NifTi (*.nii *.nii.gz)"
        )[0]
        if path:
            file = Path(path)
            self.data.nii_seg = Nii_seg(file)
            if self.data.nii_seg:
                self.data.nii_seg.mask = True
                self.mask2img.setEnabled(True if self.data.nii_seg.path else False)
                self.maskFlipUpDown.setEnabled(True)
                self.maskFlipLeftRight.setEnabled(True)
                self.maskFlipBackForth.setEnabled(True)

                self.img_overlay.setEnabled(True if self.data.nii_seg.path else False)
                self.img_overlay.setChecked(True if self.data.nii_seg.path else False)
                self.settings.setValue(
                    "img_disp_overlay", True if self.data.nii_seg.path else False
                )
        else:
            print("Warning no file selcted")
    def _load_dyn(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Dynamic Image", "", "NifTi (*.nii *.nii.gz)"
        )[0]
        if path:
            file = Path(path) if path else None
            self.data.nii_dyn = Nii(file)
        # if self.settings.value("plt_show", type=bool):
        #     Plotting.show_pixel_spectrum(self.plt_AX, self.plt_canvas, self.data)
        else:
            print("Warning no file selcted")

    def _save_image(self):
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

    def _save_fit_image(self):
        fname = self.data.nii_img.path
        file = Path(
            QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save Fit Image",
                fname.__str__(),
                "NifTi (*.nii *.nii.gz)",
            )[0]
        )
        self.data.nii_dyn.save(file)

    def _save_masked_image(self):
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

    def _open_settings_dlg(self):
        self.settings_dlg = SettingsWindow(self, self.settings)
        self.settings_dlg.show()

    def _mask_flip_up_down(self):
        # Images are rotated 90 degrees so lr and ud are switched
        self.data.nii_seg.array = np.fliplr(self.data.nii_seg.array)
        self.setup_image()

    def _mask_flip_left_right(self):
        # Images are rotated 90 degrees so lr and ud are switched
        self.data.nii_seg.array = np.flipud(self.data.nii_seg.array)
        self.setup_image()

    def _mask_flip_back_forth(self):
        self.data.nii_seg.array = np.flip(self.data.nii_seg.array, axis=2)
        self.setup_image()

    def _mask2img(self):
        self.data.nii_img_masked = Processing.merge_nii_images(
            self.data.nii_img, self.data.nii_seg
        )
        if self.data.nii_img_masked:
            self.plt_showMaskedImage.setEnabled(True)
            self.saveMaskedImage.setEnabled(True)

    def _fit_NNLS(self, model: str):
        self.mainWidget.setCursor(QtCore.Qt.CursorShape.WaitCursor)

        NNLS_dict = {"max_iter": SettingsWidget("Maximum Iterations", 250 , [0, np.power(10, 6)]),
                     "n_bins": SettingsWidget("Number of Bins", 250, [0, np.power(10, 6)]),
                     "d_range": SettingsWidget("Diffusion Range", np.array([1 * 1e-4, 2 * 1e-1]), [0,1])}

        self.fit_dlg = FittingWindow(model, NNLS_dict)
        self.fit_dlg.show()

        # if model == "NNLS":
        #     self.data.fit.NNLS.img = self.data.nii_img
        #     self.data.fit.NNLS.seg = self.data.nii_seg
        #     # self.data.fit.NNLS.fitParams = NNLSParams(model, nbins=250)
        #     self.data.fit.NNLS.fitting_pixelwise()
        # elif model == "NNLSreg":
        #     self.data.fit.NNLSreg.img = self.data.nii_img
        #     self.data.fit.NNLSreg.seg = self.data.nii_seg
        #     # self.data.fit.NNLSreg.reg_order = 2
        #     self.data.fit.NNLSreg.fitting_pixelwise()
        # elif model == "NNLSregCV":
        #     self.data.fit.NNLSregCV.img = self.data.nii_img
        #     self.data.fit.NNLSregCV.seg = self.data.nii_seg
        #     # self.data.fit.NNLSregCV.fitParams = NNLSParams("NNLSregCV", nbins=250)
        #     self.data.fit.NNLSregCV.fitting_pixelwise()

        # self.data.nii_dyn = Nii().from_array(
        #     getattr(self.data.fit, model).fit_pixel_results.spectrum
        # )
        # # self.data.nii_dyn = setup_pixelwise_fitting(getattr(self.data.fit, model))

        self.saveFitImage.setEnabled(True)
        self.mainWidget.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def _fit_mono(self, model: str):
        self.mainWidget.setCursor(QtCore.Qt.CursorShape.WaitCursor)

        if model == "mono":
            self.data.fit.mono.img = self.data.nii_img
            self.data.fit.mono.seg = self.data.nii_seg
            # self.data.fit.mono.fitParams = MonoParams("mono")
            self.data.fit.mono.fitting_pixelwise()

        elif model == "mono_t1":
            self.data.fit.mono_t1.img = self.data.nii_img
            self.data.fit.mono_t1.seg = self.data.nii_seg
            # self.data.fit.mono_t1.fitParams = MonoParams("mono_t1")
            self.data.fit.mono_t1.fit_params.variables.TM = (
                9.8  # add dynamic mixing times
            )
            self.data.fit.mono_t1.fitting_pixelwise()
        # self.data.nii_dyn = setup_pixelwise_fitting(getattr(self.data.fit, model))
        
        self.data.nii_dyn = Nii().from_array(
            getattr(self.data.fit, model).fit_pixel_results.spectrum
        )
        
        self.saveFitImage.setEnabled(True)
        self.mainWidget.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def _switchImage(self, type: str = "Img"):
        """Switch Image Callback"""
        self.settings.setValue("img_disp_type", type)
        self.setup_image()

    def _switchPlt(self, type: str = "single_voxel"):
        """Switch Plot Callback"""
        self.settings.setValue("plt_disp_type", type)
        if type == "single_voxel":
            if self.plt_DispType_SingleVoxel.isChecked():
                self.plt_DispType_SegSpectrum.setChecked(False)
            else:
                self.plt_DispType_SegSpectrum.setChecked(True)
        elif type == "seg_spectrum":
            if self.plt_DispType_SegSpectrum.isChecked():
                self.plt_DispType_SingleVoxel.setChecked(False)
            else:
                self.plt_DispType_SingleVoxel.setChecked(True)

    def _plt_show(self):
        """Plot Axis show Callback"""
        if not self.plt_show.isChecked():
            self.plt_canvas.setParent(None)
            self.plt_fig.set_visible(False)
            self.settings.setValue("plt_show", False)
        else:
            self.main_hLayout.addWidget(self.plt_canvas)
            self.settings.setValue("plt_show", True)
        # self.resizeMainWindow()
        self._resize_figure_axis()

    def _img_overlay(self):
        """Overlay Callback"""
        self.settings.setValue(
            "img_disp_overlay", True if self.img_overlay.isChecked() else False
        )
        self.setup_image()

    def _plt_showMaskedImage(self):
        if self.plt_showMaskedImage.isChecked():
            self.img_overlay.setChecked(False)
            self.img_overlay.setEnabled(False)
            self.settings.setValue("img_disp_overlay", False)
            self.setup_image()
        else:
            self.img_overlay.setEnabled(True)
            self.settings.setValue("img_disp_overlay", True)
            self.setup_image()

    def _SliceSldrChanged(self):
        """Slice Slider Callback"""
        self.data.plt.nslice.number = self.SliceSldr.value()
        self.SliceSpnBx.setValue(self.SliceSldr.value())
        self.setup_image()

    def _SliceSpnBxChanged(self):
        """Slice Spinbox Callback"""
        self.data.plt.nslice.number = self.SliceSpnBx.value()
        self.SliceSldr.setValue(self.SliceSpnBx.value())
        self.setup_image()

    def _resize_figure_axis(self, aspect_ratio: float | None = 1.0):
        """Resize main image axis to canvas size"""
        box = self.img_ax.get_position()
        if box.width > box.height:
            scaling = aspect_ratio / box.width
            new_height = box.height * scaling
            new_y0 = (1 - new_height) / 2
            self.img_ax.set_position(
                [(1 - aspect_ratio) / 2, new_y0, aspect_ratio, new_height]
            )
        elif box.width < box.height:
            scaling = aspect_ratio / box.height
            new_width = box.width * scaling
            new_x0 = (1 - new_width) / 2
            self.img_ax.set_position(
                [new_x0, (1 - aspect_ratio) / 2, new_width, aspect_ratio]
            )

    def _get_image_by_label(self) -> Nii:
        """Get selected Image from settings"""
        if self.settings.value("img_disp_type") == "Img":
            return self.data.nii_img
        elif self.settings.value("img_disp_type") == "Mask":
            return self.data.nii_seg
        elif self.settings.value("img_disp_type") == "Seg":
            return self.data.nii_seg
        elif self.settings.value("img_disp_type") == "Dyn":
            return self.data.nii_dyn

    def setup_image(self):
        """Setup Image on main Axis"""
        self.data.plt.nslice.number = self.SliceSldr.value()
        nii_img = self._get_image_by_label()
        if nii_img.path:
            img_display = nii_img.to_rgba_array(self.data.plt.nslice.value)
            self.img_ax.clear()
            self.img_ax.imshow(img_display, cmap="gray")
            # Add Patches
            if (
                self.settings.value("img_disp_overlay", type=bool)
                and self.data.nii_seg.path
            ):
                mask = self.data.nii_seg
                colors = ["r", "g", "b", "y"]
                for idx in range(mask.number_segs):
                    polygon_patches = mask.get_polygon_patch_2D(
                        idx + 1, self.data.plt.nslice.value
                    )
                    if polygon_patches:
                        for polygon_patch in polygon_patches:
                            if polygon_patch:
                                polygon_patch.set_edgecolor(colors[idx])
                                polygon_patch.set_alpha(self.data.plt.alpha)
                                # polygon_patch.set_facecolor(colors[idx])
                                polygon_patch.set_facecolor("none")
                                self.img_ax.add_patch(polygon_patch)

            self.img_ax.axis("off")
            self._resize_figure_axis()
            self.img_canvas.draw()

    def resizeMainWindow(self):
        # still needed ????
        self.main_hLayout.update()
        self.main_vLayout.update()


if __name__ == "__main__":
    freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()  # QtWidgets.QWidget()
    if main_window.settings.value("theme") == "Dark":
        app.setStyle("Fusion")        
    main_window.show()
    sys.exit(app.exec())
