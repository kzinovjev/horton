# -*- coding: utf-8 -*-
# HORTON: Helpful Open-source Research TOol for N-fermion systems.
# Copyright (C) 2011-2017 The HORTON Development Team
#
# This file is part of HORTON.
#
# HORTON is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# HORTON is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --

from collections import OrderedDict

import numpy as np
from ..overlap import fac2, binom, compute_overlap
from . common import get_fn


def test_fac2():
    assert fac2(-20) == 1
    assert fac2(0) == 1
    assert fac2(1) == 1
    assert fac2(2) == 2
    assert fac2(3) == 3
    assert fac2(4) == 8
    assert fac2(5) == 15


def test_binom():
    assert binom(1, 1) == 1
    assert binom(5, 3) == 10
    assert binom(3, 2) == 3
    assert binom(10, 4) == 210
    assert binom(18, 14) == 3060
    assert binom(5, 1) == 5
    assert binom(5, 0) == 1
    assert binom(0, 0) == 1
    assert binom(5, 5) == 1


def test_load_fchk_hf_sto3g_num():
    ref = np.load(get_fn("load_fchk_hf_sto3g_num.npy"))
    d = OrderedDict([('centers', np.array([[0., 0., 0.19048439],
                                           [0., 0., -1.71435955]])),
                     ('shell_map', np.array([0, 0, 0, 1])),
                     ('nprims', np.array([3, 3, 3, 3])), ('shell_types', np.array([0, 0, 1, 0])),
                     ('alphas', np.array([166.679134, 30.3608123, 8.21682067, 6.46480325,
                                          1.50228124, 0.48858849, 6.46480325, 1.50228124,
                                          0.48858849, 3.42525091, 0.62391373, 0.1688554])),
                     ('con_coeffs',
                      np.array([0.15432897, 0.53532814, 0.44463454, -0.09996723, 0.39951283,
                                0.70011547, 0.15591627, 0.60768372, 0.39195739, 0.15432897,
                                0.53532814, 0.44463454]))])

    assert np.allclose(ref, compute_overlap(*d.values()))


def test_load_fchk_o2_cc_pvtz_pure_num():
    ref = np.load(get_fn("load_fchk_o2_cc_pvtz_pure_num.npy"))
    d = OrderedDict([('centers', np.array([[0.00000000e+00, 0.00000000e+00, 1.09122830e+00],
                                           [1.33636924e-16, 0.00000000e+00, -1.09122830e+00]])), (
                         'shell_map',
                         np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])), (
                         'nprims',
                         np.array([7, 7, 1, 1, 3, 1, 1, 1, 1, 1, 7, 7, 1, 1, 3, 1, 1, 1, 1, 1])),
                     ('shell_types', np.array([0, 0, 0, 0, 1, 1, 1, -2, -2, -3, 0, 0, 0, 0, 1, 1, 1,
                                               -2, -2, -3])),
                     ('alphas', np.array([1.53300000e+04, 2.29900000e+03, 5.22400000e+02,
                                          1.47300000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 1.53300000e+04, 2.29900000e+03,
                                          5.22400000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 6.88200000e-01, 1.75200000e+00,
                                          2.38400000e-01, 3.44600000e+01, 7.74900000e+00,
                                          2.28000000e+00, 7.15600000e-01, 2.14000000e-01,
                                          2.31400000e+00, 6.45000000e-01, 1.42800000e+00,
                                          1.53300000e+04, 2.29900000e+03, 5.22400000e+02,
                                          1.47300000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 1.53300000e+04, 2.29900000e+03,
                                          5.22400000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 6.88200000e-01, 1.75200000e+00,
                                          2.38400000e-01, 3.44600000e+01, 7.74900000e+00,
                                          2.28000000e+00, 7.15600000e-01, 2.14000000e-01,
                                          2.31400000e+00, 6.45000000e-01, 1.42800000e+00])),
                     ('con_coeffs', np.array([5.19808943e-04, 4.02025621e-03, 2.07128267e-02,
                                              8.10105536e-02, 2.35962985e-01, 4.42653446e-01,
                                              3.57064423e-01, 9.13376623e-06, 6.07362596e-05,
                                              2.68782282e-04, -6.96940030e-03, -6.06456900e-02,
                                              -1.65519536e-01, 1.07151369e+00, 1.00000000e+00,
                                              1.00000000e+00, 4.11634896e-02, 2.57762836e-01,
                                              8.02419274e-01, 1.00000000e+00, 1.00000000e+00,
                                              1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                                              5.19808943e-04, 4.02025621e-03, 2.07128267e-02,
                                              8.10105536e-02, 2.35962985e-01, 4.42653446e-01,
                                              3.57064423e-01, 9.13376623e-06, 6.07362596e-05,
                                              2.68782282e-04, -6.96940030e-03, -6.06456900e-02,
                                              -1.65519536e-01, 1.07151369e+00, 1.00000000e+00,
                                              1.00000000e+00, 4.11634896e-02, 2.57762836e-01,
                                              8.02419274e-01, 1.00000000e+00, 1.00000000e+00,
                                              1.00000000e+00, 1.00000000e+00, 1.00000000e+00]))])
    assert np.allclose(ref, compute_overlap(*d.values()))


def test_load_fchk_o2_cc_pvtz_cart_num():
    ref = np.load(get_fn("load_fchk_o2_cc_pvtz_cart_num.npy"))
    d = OrderedDict([('centers', np.array([[0.00000000e+00, 0.00000000e+00, 1.09122830e+00],
                                           [1.33636924e-16, 0.00000000e+00, -1.09122830e+00]])), (
                         'shell_map',
                         np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])), (
                         'nprims',
                         np.array([7, 7, 1, 1, 3, 1, 1, 1, 1, 1, 7, 7, 1, 1, 3, 1, 1, 1, 1, 1])), (
                         'shell_types',
                         np.array([0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 0, 0, 0, 0, 1, 1, 1, 2, 2, 3])),
                     ('alphas', np.array([1.53300000e+04, 2.29900000e+03, 5.22400000e+02,
                                          1.47300000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 1.53300000e+04, 2.29900000e+03,
                                          5.22400000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 6.88200000e-01, 1.75200000e+00,
                                          2.38400000e-01, 3.44600000e+01, 7.74900000e+00,
                                          2.28000000e+00, 7.15600000e-01, 2.14000000e-01,
                                          2.31400000e+00, 6.45000000e-01, 1.42800000e+00,
                                          1.53300000e+04, 2.29900000e+03, 5.22400000e+02,
                                          1.47300000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 1.53300000e+04, 2.29900000e+03,
                                          5.22400000e+02, 4.75500000e+01, 1.67600000e+01,
                                          6.20700000e+00, 6.88200000e-01, 1.75200000e+00,
                                          2.38400000e-01, 3.44600000e+01, 7.74900000e+00,
                                          2.28000000e+00, 7.15600000e-01, 2.14000000e-01,
                                          2.31400000e+00, 6.45000000e-01, 1.42800000e+00])),
                     ('con_coeffs', np.array([5.19808943e-04, 4.02025621e-03, 2.07128267e-02,
                                              8.10105536e-02, 2.35962985e-01, 4.42653446e-01,
                                              3.57064423e-01, 9.13376623e-06, 6.07362596e-05,
                                              2.68782282e-04, -6.96940030e-03, -6.06456900e-02,
                                              -1.65519536e-01, 1.07151369e+00, 1.00000000e+00,
                                              1.00000000e+00, 4.11634896e-02, 2.57762836e-01,
                                              8.02419274e-01, 1.00000000e+00, 1.00000000e+00,
                                              1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                                              5.19808943e-04, 4.02025621e-03, 2.07128267e-02,
                                              8.10105536e-02, 2.35962985e-01, 4.42653446e-01,
                                              3.57064423e-01, 9.13376623e-06, 6.07362596e-05,
                                              2.68782282e-04, -6.96940030e-03, -6.06456900e-02,
                                              -1.65519536e-01, 1.07151369e+00, 1.00000000e+00,
                                              1.00000000e+00, 4.11634896e-02, 2.57762836e-01,
                                              8.02419274e-01, 1.00000000e+00, 1.00000000e+00,
                                              1.00000000e+00, 1.00000000e+00, 1.00000000e+00]))])

    assert np.allclose(ref, compute_overlap(*d.values()), atol=1e-8)
