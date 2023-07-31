import sys, os, re
import typing
from PyQt6 import QtWidgets, QtGui, QtCore
from pathlib import Path

from PyQt6.QtWidgets import QWidget
from utils import *
from fitData import *
from plotting import Plotting
from PIL import ImageQt
from typing import Callable
from multiprocessing import freeze_support
from matplotlib.figure import Figure
import matplotlib.patches as patches
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
            self.NNLS = FitData("NNLSreg")
            self.NNLSreg = FitData("NNLSreg")
            self.NNLSregCV = FitData("NNLSregCV")
            self.mono = FitData("mono")
            self.mono_t1 = FitData("mono_T1")


class FittingWidgets(object):
    class WidgetData:
        def __init__(
            self,
            name: str = "",
            current_value: int | float | np.ndarray = 1,
            value_range: list = [],
        ):
            self.name = name
            self.current_value = current_value
            self.value_range = value_range
            self.__value = current_value

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self, arg):
            if type(self.current_value) == (int or float):
                arg = type(self.current_value)(arg)
            elif type(arg) == np.ndarray:
                arg = np.frombuffer(arg)
            # TODO: range implementation
            # if value < self.value_range[0] or value > self.value_range[1]:
            #     self.__value = self.default
            #     print("Value exceded value range.")
            # else:
            #     self.__value = value
            self.__value = arg

    class EditField(WidgetData, QtWidgets.QLineEdit):
        def __init__(
            self,
            name: str,
            current_value: int | float | np.ndarray,
            value_range: list | None,
            tooltip: str | None = None,
        ):
            FittingWidgets.WidgetData.__init__(self, name, current_value, value_range)
            QtWidgets.QLineEdit.__init__(self)
            self.setText(str(current_value))
            self.textChanged.connect(self._text_changed)
            self.setMaximumHeight(28)

        def _text_changed(self):
            self.value = self.text()

    class CheckBox(WidgetData, QtWidgets.QCheckBox):
        def __init__(
            self,
            name: str,
            current_value: int | float | np.ndarray,
            value_range: list,
            tooltip: str | None = None,
        ):
            FittingWidgets.WidgetData.__init__(self, name, current_value, value_range)
            QtWidgets.QTextEdit.__init__(self)
            self.setText(str(current_value))
            self.stateChanged.connect(self._state_changed)

        def _state_changed(self):
            self.data.value = self.isChecked

    class ComboBox(WidgetData, QtWidgets.QComboBox):
        def __init__(
            self,
            name: str,
            current_value: str,
            value_range: list,
            tooltip: str | None = None,
        ):
            FittingWidgets.WidgetData.__init__(self, name, current_value, value_range)
            QtWidgets.QTextEdit.__init__(self)
            self.addItems(value_range)
            self.setCurrentText(current_value)
            self.currentIndexChanged.connect(self.__text_changed)

        def __text_changed(self):
            self.value = self.currentText()

    class PushButton(WidgetData, QtWidgets.QPushButton):
        def __init__(
            self,
            name: str,
            current_value: np.ndarray,
            bttn_function: Callable = None,
            bttn_text: str | None = None,
            tootip: str | None = None,
        ):
            FittingWidgets.WidgetData.__init__(self, name, current_value, [])
            QtWidgets.QPushButton.__init__(self)
            self.value = current_value
            self.clicked.connect(lambda x: self.__button_clicked(bttn_function))
            if bttn_text:
                self.setText(bttn_text)

        def __button_clicked(self, bttn_function: Callable):
            self.value = bttn_function()


class FittingWindow(QtWidgets.QDialog):
    def __init__(self, name: str, fitting_dict: dict) -> None:
        super().__init__()
        self.run = False
        self.fitting_dict = fitting_dict
        self.setWindowTitle("Fitting " + name)
        img = Path(Path(__file__).parent, "resources", "Logo.png").__str__()
        self.setWindowIcon(QtGui.QIcon(img))
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            )
        )
        # self.setWindowIcon(QtGui.QIcon(img))
        self.setMinimumSize(192, 64)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_grid = QtWidgets.QGridLayout()
        for idx, key in enumerate(fitting_dict):
            # self.main_layout.addLayout(fitting_dict[key])
            label = QtWidgets.QLabel(self.fitting_dict[key].name + ":")
            self.main_grid.addWidget(label, idx, 0)
            self.main_grid.addWidget(self.fitting_dict[key], idx, 1)
        self.main_layout.addLayout(self.main_grid)

        button_layout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(
            28,
            28,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        button_layout.addSpacerItem(spacer)
        self.run_button = QtWidgets.QPushButton()
        self.run_button.setText("Run Fitting")
        self.run_button.setMaximumWidth(75)
        self.run_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        button_layout.addWidget(self.run_button)
        self.main_layout.addLayout(button_layout)
        self.run_button.clicked.connect(self.run_button_pushed)
        self.setLayout(self.main_layout)

    def run_button_pushed(self):
        # self.output_dict = dict()
        for key in self.fitting_dict:
            self.fitting_dict[key].current_value = self.fitting_dict[key].value
        self.run = True
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        return super().closeEvent(event)

    def dict_to_attributes(self, fit_data: FitData.Parameters):
        # NOTE b_values and other special values have to be poped first

        for key, item in self.fitting_dict.items():
            entries = key.split(".")
            current_obj = fit_data
            if len(entries) > 1:
                for entry in entries[:-2]:
                    current_obj = getattr(current_obj, entry)
            setattr(current_obj, entries[-1], item.value)


class SettingsWindow(QtWidgets.QWidget):
    def __init__(
        self, parent: QtWidgets.QMainWindow, settings: QtCore.QSettings
    ) -> None:
        super().__init__()

        self.settings = settings
        self.setWindowTitle("Settings")
        img = Path(Path(__file__).parent, "resources", "Logo.png").__str__()
        self.setWindowIcon(QtGui.QIcon(img))
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
        self.theme_combobox.addItems(["Dark", "Light"])
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

        # if path:
        #     self._load_image(path)

    def _load_settings(self):
        self.settings = QtCore.QSettings("MyApp", "Pyneapple")
        if self.settings.value("last_dir", "") == "":
            self.settings.setValue("last_dir", os.path.abspath(__file__))
            self.settings.setValue("theme", "Light")  # "Dark", "Light"
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
                        Path(
                            Path(__file__).parent, "resources", "PyneAppleLogo_gray.png"
                        )
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
        def _SliceSldrChanged(self):
            """Slice Slider Callback"""
            self.data.plt.nslice.number = self.SliceSldr.value()
            self.SliceSpnBx.setValue(self.SliceSldr.value())
            self.setup_image()

        self.SliceHlayout = QtWidgets.QHBoxLayout()  # Layout for Slider ans Spinbox
        self.SliceSldr = QtWidgets.QSlider()
        self.SliceSldr.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.SliceSldr.setEnabled(False)
        self.SliceSldr.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.SliceSldr.setTickInterval(1)
        self.SliceSldr.setMinimum(1)
        self.SliceSldr.setMaximum(20)
        self.SliceSldr.valueChanged.connect(lambda x: _SliceSldrChanged(self))
        self.SliceHlayout.addWidget(self.SliceSldr)

        # ----- SpinBox
        def _SliceSpnBxChanged(self):
            """Slice Spinbox Callback"""
            self.data.plt.nslice.number = self.SliceSpnBx.value()
            self.SliceSldr.setValue(self.SliceSpnBx.value())
            self.setup_image()

        self.SliceSpnBx = QtWidgets.QSpinBox()
        self.SliceSpnBx.setValue(1)
        self.SliceSpnBx.setEnabled(False)
        self.SliceSpnBx.setMinimumWidth(20)
        self.SliceSpnBx.setMaximumWidth(40)
        self.SliceSpnBx.valueChanged.connect(lambda x: _SliceSpnBxChanged(self))
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

        # Load Image
        def _load_image(self, path: Path | str = None):
            if not path:
                path = QtWidgets.QFileDialog.getOpenFileName(
                    self,
                    caption="Open Image",
                    directory="",
                    filter="NifTi (*.nii *.nii.gz)",
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
                    self.img_overlay.setEnabled(
                        True if self.data.nii_seg.path else False
                    )
                else:
                    print("Warning no file selcted")

        self.loadImage = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Image...",
            self,
        )
        self.loadImage.triggered.connect(lambda x: _load_image(self))
        fileMenu.addAction(self.loadImage)

        # Load Segmentation
        def _load_seg(self):
            # TODO create overlay in advance before loading not on the fly
            path = QtWidgets.QFileDialog.getOpenFileName(
                self,
                caption="Open Mask Image",
                directory="",
                filter="NifTi (*.nii *.nii.gz)",
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

                    self.img_overlay.setEnabled(
                        True if self.data.nii_seg.path else False
                    )
                    self.img_overlay.setChecked(
                        True if self.data.nii_seg.path else False
                    )
                    self.settings.setValue(
                        "img_disp_overlay", True if self.data.nii_seg.path else False
                    )
            else:
                print("Warning no file selcted")

        self.loadSeg = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Segmentation...",
            self,
        )
        self.loadSeg.triggered.connect(lambda x: _load_seg(self))
        fileMenu.addAction(self.loadSeg)

        # Load dynamic Image
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

        self.loadDyn = QtGui.QAction(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
            "Open &Dynamic Image...",
            self,
        )
        self.loadDyn.triggered.connect(lambda x: _load_dyn(self))
        fileMenu.addAction(self.loadDyn)
        fileMenu.addSeparator()

        # Save Image
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

        self.saveImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Image...",
            self,
        )
        self.saveImage.triggered.connect(lambda x: _save_image(self))
        fileMenu.addAction(self.saveImage)

        # Save Fit Image
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

        self.saveFitImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Fit to NifTi...",
            self,
        )
        self.saveFitImage.setEnabled(False)
        self.saveFitImage.triggered.connect(lambda x: _save_fit_image(self))
        fileMenu.addAction(self.saveFitImage)

        # Save masked image
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

        self.saveMaskedImage = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton
            ),
            "Save Masked Image...",
            self,
        )
        self.saveMaskedImage.setEnabled(False)
        self.saveMaskedImage.triggered.connect(lambda x: _save_masked_image(self))
        fileMenu.addAction(self.saveMaskedImage)

        fileMenu.addSeparator()

        # Open Settings
        def _open_settings_dlg(self):
            self.settings_dlg = SettingsWindow(self, self.settings)
            self.settings_dlg.show()

        self.open_settings_dlg = QtGui.QAction(
            self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_TitleBarMenuButton
            ),
            "Settings...",
            self,
        )
        self.open_settings_dlg.setEnabled(True)
        self.open_settings_dlg.triggered.connect(lambda x: _open_settings_dlg(self))
        fileMenu.addAction(self.open_settings_dlg)

        menuBar.addMenu(fileMenu)

        # ----- Edit Menu
        editMenu = QtWidgets.QMenu("&Edit", self)
        MaskMenu = QtWidgets.QMenu("&Mask Tools", self)

        OrientationMenu = QtWidgets.QMenu("&Orientation", self)
        self.rotMask = QtGui.QAction("&Rotate Mask clockwise", self)
        self.rotMask.setEnabled(False)
        OrientationMenu.addAction(self.rotMask)

        # Flip Mask Up Down
        def _mask_flip_up_down(self):
            # Images are rotated 90 degrees so lr and ud are switched
            self.data.nii_seg.array = np.fliplr(self.data.nii_seg.array)
            self.data.nii_seg.calculate_polygons()
            self.setup_image()

        self.maskFlipUpDown = QtGui.QAction("Flip Mask Up-Down", self)
        self.maskFlipUpDown.setEnabled(False)
        self.maskFlipUpDown.triggered.connect(lambda x: _mask_flip_up_down(self))
        OrientationMenu.addAction(self.maskFlipUpDown)

        # Flip Left Right
        def _mask_flip_left_right(self):
            # Images are rotated 90 degrees so lr and ud are switched
            self.data.nii_seg.array = np.flipud(self.data.nii_seg.array)
            self.data.nii_seg.calculate_polygons()
            self.setup_image()

        self.maskFlipLeftRight = QtGui.QAction("Flip Mask Left-Right", self)
        self.maskFlipLeftRight.setEnabled(False)
        self.maskFlipLeftRight.triggered.connect(lambda x: _mask_flip_left_right(self))
        OrientationMenu.addAction(self.maskFlipLeftRight)

        # Flip Back Forth
        def _mask_flip_back_forth(self):
            self.data.nii_seg.array = np.flip(self.data.nii_seg.array, axis=2)
            self.data.nii_seg.calculate_polygons()
            self.setup_image()

        self.maskFlipBackForth = QtGui.QAction("Flip Mask Back-Forth", self)
        self.maskFlipBackForth.setEnabled(False)
        self.maskFlipBackForth.triggered.connect(lambda x: _mask_flip_back_forth(self))
        OrientationMenu.addAction(self.maskFlipBackForth)

        MaskMenu.addMenu(OrientationMenu)

        # Mask to Image
        def _mask2img(self):
            self.data.nii_img_masked = Processing.merge_nii_images(
                self.data.nii_img, self.data.nii_seg
            )
            if self.data.nii_img_masked:
                self.plt_showMaskedImage.setEnabled(True)
                self.saveMaskedImage.setEnabled(True)

        self.mask2img = QtGui.QAction("&Apply on Image", self)
        self.mask2img.setEnabled(False)
        self.mask2img.triggered.connect(lambda x: _mask2img(self))
        MaskMenu.addAction(self.mask2img)

        editMenu.addMenu(MaskMenu)
        menuBar.addMenu(editMenu)

        # ----- Fitting Procedure
        def _fit(self, model: str):
            fit_data: FitData
            dlg_dict = dict()
            if model in ("NNLS", "NNLSreg"):
                fit_data = self.data.fit.NNLS

                # Prepare Dlg Dict
                dlg_dict = {
                    "fit_area": FittingWidgets.ComboBox(
                        "Fitting Area", "Pixel", ["Pixel", "Segmentation"]
                    ),
                    "max_iter": FittingWidgets.EditField(
                        "Maximum Iterations",
                        fit_data.fit_params.max_iter,
                        [0, np.power(10, 6)],
                    ),
                    "boundaries.n_bins": FittingWidgets.EditField(
                        "Number of Bins",
                        fit_data.fit_params.boundaries.n_bins,
                        [0, np.power(10, 6)],
                    ),
                    "boundaries.d_range": FittingWidgets.EditField(
                        "Diffusion Range",
                        fit_data.fit_params.boundaries.d_range,
                        [0, 1],
                    ),
                    "reg_order": FittingWidgets.ComboBox(
                        "Regularisation Order", "0", ["0", "1", "2", "3", "CV"]
                    ),
                    "mu": FittingWidgets.EditField(
                        "Regularisation Factor",
                        fit_data.fit_params.mu,
                        [0.0, 1.0],
                    ),
                    "b_values": FittingWidgets.PushButton(
                        "Load B-Values",
                        str(fit_data.fit_params.b_values),
                        self._load_b_values,
                        "Open File",
                    ),
                }

            if model in ("mono", "mono_t1"):
                if model in "mono":
                    fit_data = self.data.fit.mono
                elif model in "mono_t1":
                    fit_data = self.data.fit.mono_t1
                dlg_dict = {
                    "fit_area": FittingWidgets.ComboBox(
                        "Fitting Area", "Pixel", ["Pixel", "Segmentation"]
                    ),
                    "max_iter": FittingWidgets.EditField(
                        "Maximum Iterations",
                        fit_data.fit_params.max_iter,
                        [0, np.power(10, 6)],
                    ),
                    "boundaries.x0": FittingWidgets.EditField(
                        "Start Values",
                        fit_data.fit_params.boundaries.x0,
                        None,
                    ),
                    "boundaries.lb": FittingWidgets.EditField(
                        "Lower Boundaries",
                        fit_data.fit_params.boundaries.lb,
                        None,
                    ),
                    "boundaries.ub": FittingWidgets.EditField(
                        "Upper Booundaries",
                        fit_data.fit_params.boundaries.ub,
                        None,
                    ),
                }
                if model in "mono_t1":
                    dlg_dict["variables.TM"] = FittingWidgets.EditField(
                        "Mixing Time (TM)",
                        fit_data.fit_params.variables.TM,
                        None,
                        "Set Mixing Time if you want to performe advanced Fitting",
                    )

                dlg_dict["b_values"] = FittingWidgets.PushButton(
                    "Load B-Values",
                    str(fit_data.fit_params.b_values),
                    self._load_b_values,
                    "Open File",
                )
            # Launch Dlg
            self.fit_dlg = FittingWindow(model, dlg_dict)
            self.fit_dlg.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
            self.fit_dlg.exec()

            # Extract Paramters from dlg dict
            fit_data.fit_params.b_values = self._b_values_from_dict()
            self.fit_dlg.dict_to_attributes(fit_data.fit_params)

            if self.fit_dlg.run:
                if (
                    hasattr(fit_data.fit_params, "reg_order")
                    and fit_data.fit_params.reg_order == "CV"
                ):
                    fit_data.fit_params.model = FitModel.NNLS_reg_CV
                elif (
                    hasattr(fit_data.fit_params, "reg_order")
                    and fit_data.fit_params.reg_order != "CV"
                ):
                    fit_data.fit_params.reg_order = int(fit_data.fit_params.reg_order)

                self.mainWidget.setCursor(QtCore.Qt.CursorShape.WaitCursor)

                # Prepare Data
                fit_data.img = self.data.nii_img
                fit_data.seg = self.data.nii_seg

                if fit_data.fit_params.fit_area == "Pixel":
                    fit_data.fitting_pixelwise()
                    self.data.nii_dyn = Nii().from_array(
                        getattr(self.data.fit, model).fit_results.spectrum
                    )

                elif fit_data.fit_area == "Segmentation":
                    fit_data.fitting_segmentation_wise()

                self.mainWidget.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

                self.saveFitImage.setEnabled(True)

        # ----- Fitting Menu
        fitMenu = QtWidgets.QMenu("&Fitting", self)
        fitMenu.setEnabled(True)

        self.fit_NNLS = QtGui.QAction("NNLS", self)
        self.fit_NNLS.triggered.connect(lambda x: _fit(self, "NNLS"))

        fitMenu.addAction(self.fit_NNLS)

        monoMenu = QtWidgets.QMenu("Mono Exponential", self)
        self.fit_mono = QtGui.QAction("Monoexponential", self)
        self.fit_mono.triggered.connect(lambda x: _fit(self, "mono"))
        monoMenu.addAction(self.fit_mono)

        self.fit_mono_t1 = QtGui.QAction("Monoexponential with T1", self)
        self.fit_mono_t1.triggered.connect(lambda x: _fit(self, "mono_t1"))
        monoMenu.addAction(self.fit_mono_t1)
        # monoMenu.setEnabled(False)
        fitMenu.addMenu(monoMenu)
        menuBar.addMenu(fitMenu)

        # ----- View Menu
        viewMenu = QtWidgets.QMenu("&View", self)
        imageMenu = QtWidgets.QMenu("Switch Image", self)

        def _switchImage(self, type: str = "Img"):
            """Switch Image Callback"""
            self.settings.setValue("img_disp_type", type)
            self.setup_image()

        self.plt_showImg = QtGui.QAction("Image", self)
        self.plt_showImg.triggered.connect(lambda x: _switchImage(self, "Img"))
        # imageMenu.addAction(self.plt_showImg)

        self.plt_showMask = QtGui.QAction("Mask", self)
        self.plt_showMask.triggered.connect(lambda x: _switchImage(self, "Mask"))
        # imageMenu.addAction(self.plt_showMask)

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

        self.plt_showMaskedImage = QtGui.QAction("Image with applied Mask")
        self.plt_showMaskedImage.setEnabled(False)
        self.plt_showMaskedImage.setCheckable(True)
        self.plt_showMaskedImage.setChecked(False)
        self.plt_showMaskedImage.toggled.connect(lambda x: _plt_showMaskedImage(self))
        imageMenu.addAction(self.plt_showMaskedImage)

        self.plt_showDyn = QtGui.QAction("Dynamic", self)
        self.plt_showDyn.triggered.connect(lambda x: self._switchImage(self, "Dyn"))
        # imageMenu.addAction(self.plt_showDyn)
        viewMenu.addMenu(imageMenu)

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

        self.plt_show = QtGui.QAction("Show Plot")
        self.plt_show.setEnabled(True)
        self.plt_show.setCheckable(True)
        self.plt_show.triggered.connect(lambda x: _plt_show(self))
        viewMenu.addAction(self.plt_show)
        viewMenu.addSeparator()

        self.plt_DispType_SingleVoxel = QtGui.QAction(
            "Show Single Voxel Spectrum", self
        )
        self.plt_DispType_SingleVoxel.setCheckable(True)
        self.plt_DispType_SingleVoxel.setChecked(True)
        self.settings.setValue("plt_disp_type", "single_voxel")
        self.plt_DispType_SingleVoxel.toggled.connect(
            lambda x: self._switchPlt(self, "single_voxel")
        )
        viewMenu.addAction(self.plt_DispType_SingleVoxel)

        self.plt_DispType_SegSpectrum = QtGui.QAction(
            "Show Segmentation Spectrum", self
        )
        self.plt_DispType_SegSpectrum.setCheckable(True)
        self.plt_DispType_SegSpectrum.toggled.connect(
            lambda x: self._switchPlt(self, "seg_spectrum")
        )
        viewMenu.addAction(self.plt_DispType_SegSpectrum)
        viewMenu.addSeparator()

        def _img_overlay(self):
            """Overlay Callback"""
            self.settings.setValue(
                "img_disp_overlay", True if self.img_overlay.isChecked() else False
            )
            self.setup_image()

        self.img_overlay = QtGui.QAction("Show Mask Overlay", self)
        self.img_overlay.setEnabled(False)
        self.img_overlay.setCheckable(True)
        self.img_overlay.setChecked(False)
        self.settings.setValue("img_disp_overlay", True)
        self.img_overlay.toggled.connect(lambda x: _img_overlay(self))
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
                    position = [round(event.xdata), round(event.ydata)]
                    # correct inverted y-axis
                    position[1] = self.data.nii_img.array.shape[1] - position[1]
                    self.statusBar.showMessage("(%d, %d)" % (position[0], position[1]))
                    if self.settings.value("plt_show", type=bool):
                        if (
                            self.settings.value("plt_disp_type", type=str)
                            == "single_voxel"
                        ):
                            Plotting.show_pixel_spectrum(
                                self.plt_AX, self.plt_canvas, self.data, position
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
                nii_seg = self.data.nii_seg
                colors = ["r", "g", "b", "y"]
                if not nii_seg.polygons:
                    nii_seg.calculate_polygons()
                polygon_patches = nii_seg.polygons[self.data.plt.nslice.value]
                for idx in range(nii_seg.number_segs):
                    if polygon_patches:
                        polygon_patch: patches.Polygon
                        for polygon_patch in polygon_patches:
                            if polygon_patch:
                                polygon_patch.set_edgecolor(colors[idx])
                                polygon_patch.set_alpha(self.data.plt.alpha)
                                polygon_patch.set_linewidth(2)
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

    def _b_values_from_dict(self):
        b_values = self.fit_dlg.fitting_dict.pop("b_values", None).value
        if b_values:
            b_values = np.fromstring(
                b_values.replace("[", "").replace("]", ""), dtype=int, sep="  "
            )
            if b_values.shape != self.data.fit.NNLS.fit_params.b_values.shape:
                b_values = np.reshape(
                    b_values, self.data.fit.NNLS.fit_params.b_values.shape
                )

            return b_values

    def _load_b_values(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            caption="Open B-Value File",
            directory="",
        )[0]

        if path:
            file = Path(path)
            with open(file, "r") as f:
                # find away to decide which one is right
                # self.bvalues = np.array([int(x) for x in f.read().split(" ")])
                b_values = np.array([int(x) for x in f.read().split("\n")])
            return b_values


if __name__ == "__main__":
    freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()  # QtWidgets.QWidget()
    if main_window.settings.value("theme") == "Dark":
        app.setStyle("Fusion")
    main_window.show()
    sys.exit(app.exec())
