import random

import numpy as np
import pytest
from pyneapple.fit import parameters
from test_toolbox import ParameterTools


# @pytest.mark.order(after="test_parameters.py::TestParameters::test_load_b_values")
class TestIVIMParameters:
    def test_init_ivim_parameters(self):
        assert parameters.IVIMParams()

    def test_ivim_json_save(self, ivim_tri_params, out_json, capsys):
        # Test IVIM
        ivim_tri_params.save_to_json(out_json)
        test_params = parameters.IVIMParams(out_json)
        attributes = ParameterTools.compare_parameters(ivim_tri_params, test_params)
        ParameterTools.compare_attributes(ivim_tri_params, test_params, attributes)
        capsys.readouterr()
        assert True

    def test_ivim_boundaries(self, ivim_tri_params, capsys):
        bins = ivim_tri_params.get_bins()
        assert [round(min(bins), 5), round(max(bins), 5)] == [
            min(ivim_tri_params.boundaries.dict["D"]["slow"]),
            max(ivim_tri_params.boundaries.dict["D"]["fast"]),
        ]


class TestIVIMSegmentedParameters:
    def test_init_ivim_parameters(self):
        assert parameters.IVIMFixedComponentParams()

    @pytest.fixture
    def fixed_parameters(self):
        shape = (2, 2, 2)
        d_slow_map = np.random.rand(*shape)
        t1_map = np.random.randint(1, 2500, shape)
        return d_slow_map, t1_map

    def test_get_pixel_args(self, img, seg_reduced, fixed_parameters):
        params = parameters.IVIMFixedComponentParams()
        params.get_pixel_args(img, seg_reduced, *fixed_parameters)
