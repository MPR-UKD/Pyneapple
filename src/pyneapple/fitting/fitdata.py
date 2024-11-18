"""
Module combining fitting methods for pixel- and segmentation-wise fitting.
Main interface for fitting methods.

Classes:
    FitData: Fitting class for (multithreaded) pixel- and segmentation-wise fitting.
"""

from __future__ import annotations

from typing import Union
from pathlib import Path
import json

import numpy as np

from radimgarray import RadImgArray, SegImgArray
from .. import (
    Parameters,
    IVIMParams,
    IVIMSegmentedParams,
    NNLSParams,
    NNLSCVParams,
    IDEALParams,
)
from . import fit
from .. import Results, IVIMResults, IVIMSegmentedResults, NNLSResults


class FitData:
    """Fitting class for (multithreaded) pixel-, segmentation-wise and segmented fitting.

    Attributes:
        img (RadImgArray): RadImgArray object with image data (4D).
        seg (SegImgArray): SegImgArray object with segmentation data (4D).
        params_json (str, Path): Path to json file with fitting parameters.

    Methods:
        fit_pixel_wise(multi_threading: bool | None = True)
            Fits every pixel inside the segmentation individually.
            Multi-threading possible to boost performance.
        fit_segmentation_wise()
            Fits mean signal of segmentation(s).
        fit_ivim_segmented(multi_threading: bool = False, debug: bool = False)
            IVIM Segmented Fitting Interface.
    """

    model: Parameters
    results: Results

    def __init__(
        self,
        img: RadImgArray,  # Maybe Change signature later
        seg: SegImgArray,
        params_json: str | Path,
    ):
        """Initializes Fitting Class.

        Args:
            model (str): Model name for fitting.
            params_json (str, Path): Path to json file with fitting parameters.
            img (RadImgArray): RadImgArray object with image data.
            seg (SegImgArray): SegImgArray object with segmentation data.
        """
        self.json = params_json
        self.img = img
        self.seg = seg
        self._get_model()

        self.params = self.model(self.json)
        self._init_results()

        self.flags = dict()
        self.set_default_flags()

    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, file: str | Path):
        if json is None:
            self._json = None
        else:
            self._json = Path(file)

    def _get_model(self):
        if self.json is not None:
            with self.json.open("r") as file:
                data = json.load(file)
                if "Class" not in data.keys():
                    raise ValueError("Error: Missing Class identifier!")
                else:
                    self.model = self._get_params_class(data["Class"], Parameters)

    @staticmethod
    def _get_params_class(
        class_name: str,
        union_type: Union[IVIMParams, IVIMSegmentedParams, NNLSParams, NNLSCVParams],
    ) -> object:
        for cls in union_type.__args__:
            if cls.__name__ == class_name:
                return cls
        raise ValueError("Error: Invalid Class identifier!")

    def _init_results(self):
        if isinstance(self.params, IVIMSegmentedParams):
            self.results = IVIMSegmentedResults(self.params)
        elif isinstance(self.params, IVIMParams):
            self.results = IVIMResults(self.params)
        elif isinstance(self.params, (NNLSParams, NNLSCVParams)):
            self.results = NNLSResults(self.params)
        elif isinstance(self.params, IDEALParams):
            self.results = IVIMResults(self.params)
        else:
            raise ValueError("Error: Invalid Parameter Class Identifier!")

    def set_default_flags(self):
        """Sets default flags for fitting class."""
        self.flags["did_fit"] = False

    def fit_pixel_wise(self, multi_threading: bool | None = True):
        """Fits every pixel inside the segmentation individually.

        Args:
            multi_threading (bool | None): If True, multi-threading is used.
        """

        results = fit.fit_pixel_wise(self.img, self.seg, self.params, multi_threading)
        if results is not None:
            self.results.eval_results(results)

    def fit_segmentation_wise(self):
        """Fits mean signal of segmentation(s), computed of all pixels signals."""
        if self.img is None or self.seg is None:
            raise ValueError("No valid data for fitting selected!")
        results = fit.fit_segmentation_wise(self.img, self.seg, self.params)

        seg_indices = dict()
        for seg_number in self.seg.seg_values:
            indices = np.squeeze(self.seg, axis=3).get_seg_indices(seg_number)
            seg_indices.update(
                {
                    key: value
                    for (key, value) in zip(indices, [seg_number * 1] * len(indices))
                }
            )

        self.results.set_segmentation_wise(seg_indices)
        self.results.eval_results(results)

    def fit_ivim_segmented(self, multi_threading: bool = False, debug: bool = False):
        """IVIM Segmented Fitting Interface.
        Args:
            multi_threading (bool): If True, multi-threading is used.
            debug (bool): If True, debug output is printed.
        """
        if not isinstance(self.params, IVIMSegmentedParams):
            raise ValueError("Invalid Parameter Class for IVIM Segmented Fitting!")

        fixed_component, results = fit.fit_ivim_segmented(
            self.img, self.seg, self.params, multi_threading, debug
        )
        # Evaluate Results
        self.results.eval_results(results, fixed_component=fixed_component)

    def fit_IDEAL(self, multi_threading: bool = False, debug: bool = False):
        """IDEAL Fitting Interface.
        Args:
            multi_threading (bool): If True, multi-threading is used.
            debug (bool): If True, debug output is printed.
        """

        if not isinstance(self.params, IDEALParams):
            raise ValueError("Invalid Parameter Class for IDEAL Fitting!")

        fit_results = fit.fit_IDEAL(self.img, self.seg, self.params, multi_threading)
        self.results.eval_results(fit_results)