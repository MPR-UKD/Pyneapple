import sys  # , os
import numpy as np
from utils import *
from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QPixmap, QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from UI import ui_NNLSDynApp


class appData:
    def __init__(self):
        self.plt_boundries: np.ndarray = np.array([0.0001, 0.2])
        self.plt_nslice: nslice = nslice(0)
        self.plt_scaling: int = 2
        self.imgMain: nifti_img = nifti_img()
        self.imgDyn: nifti_img = nifti_img()


class MainWindow(QtWidgets.QMainWindow, ui_NNLSDynApp.Ui_MainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        # Setup App
        self.setupUi(self)
        self.setWindowTitle("NNLSDynApp")
        self.AXImgDyn.setPixmap(
            QPixmap(Path("ui", "resources", "image-not-available.jpg").__str__())
        )
        self.BttnImgDynLoad.setIcon(
            QIcon(Path("ui", "resources", "openFolder.png").__str__())
        )
        self.menubar.setEnabled(False)

        # Figure Initiation
        figPltDyn = Figure()
        self.figPltDynCanvas = FigureCanvas(figPltDyn)
        self.AXPltDyn = figPltDyn.add_subplot(111)
        self.hLayout_Main.addWidget(self.figPltDynCanvas)

        # Prepare Classes
        self.appdata = appData()
        self.appdata.plt_nslice.number = self.spnBx_nSlice.value()
        self.MouseTracker = MouseTracker(self.AXImgDyn)
        self.MouseTracker.positionChanged.connect(self.on_positionChanged)

        # Setup Callbacks
        self.BttnImgDynLoad.clicked.connect(self.callback_BttnImgDynLoad)
        self.spnBx_nSlice.valueChanged.connect(self.callback_spnBX_nSlice_changed)
        self.Sldr_nSlice.valueChanged.connect(self.callback_Sldr_nSlice_changed)

    def callback_BttnImgDynLoad(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self,
        )[0]
        # fname = "pat01_img_AmplDyn.nii"
        self.appdata.imgDyn.load(fname)
        self.appdata.plt_nslice.number = self.spnBx_nSlice.value()
        self.AXImgDyn.setPixmap(
            self.appdata.imgDyn.QPixmap(
                self.appdata.plt_nslice.value, self.appdata.plt_scaling
            )
        )
        # Setup Slice in UI
        self.spnBx_nSlice.setEnabled(True)
        self.spnBx_nSlice.setMaximum(self.appdata.imgDyn.size[2])
        self.Sldr_nSlice.setEnabled(True)
        self.Sldr_nSlice.setMaximum(self.appdata.imgDyn.size[2])
        self.AXImgDyn.setMouseTracking(True)
        # Scale AXImgDyn
        self.AXImgDyn.setMaximumSize(
            self.appdata.imgDyn.size[0] * self.appdata.plt_scaling,
            self.appdata.imgDyn.size[1] * self.appdata.plt_scaling,
        )
        self.AXImgDyn.setMinimumSize(
            self.appdata.imgDyn.size[0] * self.appdata.plt_scaling,
            self.appdata.imgDyn.size[1] * self.appdata.plt_scaling,
        )

    def callback_spnBX_nSlice_changed(self):
        self.appdata.plt_nslice.number = self.spnBx_nSlice.value()
        self.Sldr_nSlice.setValue(self.spnBx_nSlice.value())
        self.AXImgDyn.setPixmap(
            self.appdata.imgDyn.QPixmap(
                self.appdata.plt_nslice.value, self.appdata.plt_scaling
            )
        )

    def callback_Sldr_nSlice_changed(self):
        self.appdata.plt_nslice.number = self.Sldr_nSlice.value()
        self.spnBx_nSlice.setValue(self.Sldr_nSlice.value())
        self.AXImgDyn.setPixmap(
            self.appdata.imgDyn.QPixmap(
                self.appdata.plt_nslice.value, self.appdata.plt_scaling
            )
        )

    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_positionChanged(self, pos):
        ypos = self.MouseTracker.lbl2npcoord(
            pos.y(), self.appdata.imgDyn.size[1], self.appdata.plt_scaling
        )
        msg = "(%d, %d)" % (pos.x(), ypos)
        self.statusbar.showMessage(msg)
        try:
            self.plt_spectrum(pos)
        except IndexError:
            pass

    def plt_spectrum(self, pos):
        x, y = self.MouseTracker.np2lblcoord(
            pos.x(),
            pos.y(),
            self.appdata.imgDyn.size[0],
            self.appdata.imgDyn.size[1],
            self.appdata.plt_scaling,
        )
        ydata = self.appdata.imgDyn.array[
            x,
            y,
            self.appdata.plt_nslice.value,
            :,
        ]
        nbins = np.shape(ydata)
        xdata = np.logspace(0.0001, 0.2, num=nbins[0])
        self.AXPltDyn.clear()
        self.AXPltDyn.plot(xdata, ydata)
        self.figPltDynCanvas.draw()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()