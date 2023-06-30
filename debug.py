# from PineappleUI import startAppUI
from pathlib import Path
import utils as ut
import fit  # , imantics

# import matplotlib.pyplot as plt
# import matplotlib.patches as patches  #
# from PIL import Image

# from plotting import Plot
import numpy as np
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    img = ut.Nii(Path(r"data/01_img.nii"))
    # img = ut.Nii(Path(r"data/pat16_img.nii.gz"))
    # seg = ut.Nii_seg(Path(r"data/pat16_seg_test.nii.gz"))
    seg = ut.Nii_seg(Path(r"data/01_prostate.nii.gz"))
    # dyn = ut.Nii(Path(r"data/01_img_AmplDyn.nii"))

    fit_data = fit.FitData("NNLSreg", img, seg)
    fit_data.fit_params.max_iter = 10000
    fit_data.fit_params.reg_order = 3
    # fit_data.fitting_pixelwise(debug=False)
    results = fit_data.fitting_segmentation_wise(seg_number=1,debug=True)
    print("Done")
