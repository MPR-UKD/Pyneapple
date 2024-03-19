import pytest
from pathlib import Path
from multiprocessing import freeze_support

from src.utils import Nii, NiiSeg
from src.fit import fit


@pytest.fixture
def fit_data(capsys):
    freeze_support()
    img = Nii(Path(r"../data/test_img_176_176.nii"))
    seg = NiiSeg(Path(r"../data/test_mask.nii.gz"))

    fit_data = fit.FitData(
        "NNLS", Path(r"resources/fitting/default_params_NNLS.json"), img, seg
    )
    fit_data.fit_params.max_iter = 250

    return fit_data


@pytest.fixture
def fit_data_reg():
    freeze_support()
    img = Nii(Path(r"../data/test_img_176_176.nii"))
    seg = NiiSeg(Path(r"../data/test_mask.nii.gz"))

    fit_data = fit.FitData(
        "NNLSreg", Path(r"resources/fitting/default_params_NNLS.json"), img, seg
    )
    fit_data.fit_params.max_iter = 250

    return fit_data


def test_nnls_pixel_sequential_reg_0(fit_data, capsys):
    fit_data.fit_params.reg_order = 0
    fit_data.fit_pixel_wise(multi_threading=False)

    nii_dyn = Nii().from_array(fit_data.fit_results.spectrum)
    nii_dyn.save(r"nnls_pixel_seq_reg_0.nii")
    apsys.readouterr()
    assert True


def test_nnls_pixel_sequential_reg_1(fit_data_reg, capsys):
    fit_data_reg.fit_params.reg_order = 1
    fit_data_reg.fit_pixel_wise(multi_threading=False)

    fit_data_reg.fit_results.save_peaks_to_excel(r"test.xlsx")

    nii_dyn = Nii().from_array(fit_data_reg.fit_results.spectrum)
    nii_dyn.save(r"nnls_pixel_seq_reg_1.nii")

    capsys.readouterr()
    assert True


def test_nnls_pixel_sequential_reg_2(fit_data_reg, capsys):
    fit_data_reg.fit_params.reg_order = 2
    fit_data_reg.fit_pixel_wise(multi_threading=False)

    fit_data_reg.fit_results.save_peaks_to_excel(r"test.xlsx")

    nii_dyn = Nii().from_array(fit_data_reg.fit_results.spectrum)
    nii_dyn.save(r"nnls_pixel_seq_reg_2.nii")

    capsys.readouterr()
    assert True
