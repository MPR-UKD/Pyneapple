from pathlib import Path
from multiprocessing import freeze_support

from src.utils import Nii, NiiSeg
from src.fit import fit


def test_nnls_multithreading():
    freeze_support()
    img = Nii(Path(r"../data/01_img.nii"))
    seg = NiiSeg(Path(r"../data/01_prostate.nii.gz"))

    fit_data = fit.FitData("NNLS", img, seg)
    fit_data.fit_params.max_iter = 10000
    fit_data.fit_params.reg_order = 3
    fit_data.fit_pixel_wise(multi_threading=False)
    # results = fit_data.fitting_segmentation_wise(seg_number=1)
    assert True
