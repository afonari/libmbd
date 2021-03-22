import numpy as np
import pytest

from pymbd import ang
from pymbd.fortran import with_mpi, with_scalapack


def pytest_collection_modifyitems(config, items):
    if with_scalapack:
        skip = pytest.mark.skip(reason="doesn't support ScaLAPACK")
        for item in items:
            if 'no_scalapack' in item.keywords:
                item.add_marker(skip)


if with_mpi:
    from functools import wraps

    import py._io.terminalwriter
    from mpi4py import MPI

    rank = MPI.COMM_WORLD.Get_rank()
    _write_out = py._io.terminalwriter.write_out

    @wraps(_write_out)
    def write_out_wrapper(*args, **kwargs):
        if rank == 0:
            _write_out(*args, **kwargs)

    py._io.terminalwriter.write_out = write_out_wrapper


# fmt: off
@pytest.fixture
def benzene_dimer():
    return [
        (np.array([
            (-1.047, -1.421, 0.000), (-1.454, -0.855, 1.206),
            (-1.454, -0.855, -1.206), (-2.266, 0.277, 1.206),
            (-2.671, 0.845, 0.000), (-2.266, 0.277, -1.206),
            (-1.133, -1.292, -2.142), (-2.582, 0.716, -2.143),
            (-3.303, 1.723, 0.000), (-2.582, 0.716, 2.143),
            (-1.133, -1.292, 2.142), (-0.406, -2.291, 0.000)]) * ang,
            6 * ['C'] + 6 * ['H'],
            [0.825, 0.821, 0.821, 0.815, 0.814, 0.815,
             0.624, 0.611, 0.610, 0.611, 0.624, 0.643]),
        (np.array([
            (1.047, 1.421, 0.000), (1.454, 0.855, -1.206),
            (1.454, 0.855, 1.206), (2.266, -0.277, -1.206),
            (2.671, -0.845, 0.000), (2.266, -0.277, 1.206),
            (0.406, 2.291, 0.000), (1.133, 1.292, 2.142),
            (2.582, -0.716, 2.143), (3.303, -1.723, 0.000),
            (2.582, -0.716, -2.143), (1.133, 1.292, -2.142)]) * ang,
            6 * ['C'] + 6 * ['H'],
            [0.825, 0.821, 0.821, 0.815, 0.814, 0.815,
             0.643, 0.624, 0.611, 0.610, 0.611, 0.624])]


@pytest.fixture
def ethylcarbamate():
    return [
        (np.array([
            (4.083, 5.700, 2.856), (0.568, 0.095, 4.217), (0.470, 4.774, 3.551),
            (4.181, 1.022, 3.522), (5.572, 5.587, 1.892), (-0.920, 0.209, 5.181),
            (3.663, 3.255, 2.585), (0.988, 2.541, 4.488), (3.834, 4.011, 0.979),
            (0.816, 1.785, 6.094), (2.223, 1.314, 1.108), (2.428, 4.481, 5.965),
            (1.177, 0.092, 0.406), (3.474, 5.703, 6.667), (4.911, 5.036, 2.573),
            (-0.260, 0.759, 4.500), (4.358, 3.787, 1.918), (0.293, 2.009, 5.155),
            (0.205, 1.729, 1.101), (4.446, 4.067, 5.972), (1.285, 0.947, 0.957),
            (3.366, 4.848, 6.116), (0.485, 2.901, 1.709), (4.165, 2.895, 5.364),
            (4.066, 1.426, 0.670), (0.585, 4.369, 6.403)]) * ang,
         np.array([
             (5.008, 0.018, -0.070),
             (1.630, 6.759, 0.064),
             (-1.987, -0.981, 7.079)]) * ang,
         (2, 2, 2),
         list('HHHHHHHHHHHHHHCCCCCCNNOOOO'),
         [0.703, 0.703, 0.726, 0.726, 0.731, 0.731,
          0.727, 0.727, 0.754, 0.754, 0.750, 0.750,
          0.755, 0.755, 0.809, 0.809, 0.827, 0.827,
          0.834, 0.834, 0.840, 0.840, 0.886, 0.886,
          0.892, 0.892]),
        (np.array([
            (4.088, 5.753, 2.783), (5.625, 5.562, 1.906), (3.652, 3.273, 2.592),
            (3.854, 3.998, 0.981), (5.422, 4.834, 3.521), (6.213, 0.125, 0.386),
            (7.201, 1.360, 1.112), (4.913, 5.058, 2.573), (4.366, 3.792, 1.934),
            (5.167, 1.729, 1.084), (6.291, 0.963, 0.938), (4.042, 1.399, 0.752),
            (5.490, 2.915, 1.682)]) * ang,
         None,
         None,
         list('HHHHHHHCCCNOO'),
         [0.581, 0.607, 0.642, 0.646, 0.607, 0.596,
          0.597, 0.762, 0.799, 0.845, 0.824, 0.974,
          0.896]),
    ]


@pytest.fixture
def argon_crystal():
    return (
        np.array([(0.3, 0.1, 0.2), (4.1, -0.2, -0.1)]) * ang,
        np.array([(8.1, 0.1, -0.2), (0.3, 3.9, -0.1), (-0.1, 0.2, 4.2)]) * ang,
        (4, 4, 4),
        ['Ar', 'Ar'],
        [1.0, 1.0],
    )


@pytest.fixture
def peptide_meoh():
    return [
        (np.array([
            (2.137, 0.252, 0.453), (2.857, 0.879, 0.544),
            (2.656, -1.053, 0.687), (1.823, -1.742, 0.582),
            (3.422, -1.322, -0.039), (3.064, -1.154, 1.693)]) * ang,
         list('OHCHHH'),
         [0.9114, 0.5960, 0.7523, 0.5886, 0.5850, 0.5850]),
        (np.array([
            (-0.849, -0.339, 2.491), (0.184, -0.011, 2.416),
            (-0.882, -1.342, 2.912), (-1.390, 0.316, 3.168),
            (-1.564, -0.353, 1.159), (-2.749, -0.651, 1.056),
            (-0.801, -0.027, 0.088), (0.161, 0.240, 0.218),
            (-1.385, -0.002, -1.234), (-1.891, -0.942, -1.440),
            (-2.119, 0.796, -1.330), (-0.594, 0.149, -1.963)]) * ang,
         list('CHHHCONHCHHH'),
         [0.7657, 0.6027, 0.6062, 0.6077, 0.8343, 0.9815,
          0.8325, 0.5931, 0.7592, 0.6286, 0.6133, 0.5698]),
        (np.array([
            (-0.849, -0.339, 2.491), (0.184, -0.011, 2.416),
            (-0.882, -1.342, 2.912), (-1.390, 0.316, 3.168),
            (-1.564, -0.353, 1.159), (-2.749, -0.651, 1.056),
            (-0.801, -0.027, 0.088), (0.161, 0.240, 0.218),
            (-1.385, -0.002, -1.234), (-1.891, -0.942, -1.440),
            (-2.119, 0.796, -1.330), (-0.594, 0.149, -1.963),
            (2.137, 0.252, 0.453), (2.857, 0.879, 0.544),
            (2.656, -1.053, 0.687), (1.823, -1.742, 0.582),
            (3.422, -1.322, -0.039), (3.064, -1.154, 1.693)]) * ang,
         list('CHHHCONHCHHHOHCHHH'),
         [0.7767, 0.6594, 0.6193, 0.6167, 0.8414, 0.9898,
          0.8462, 0.7213, 0.7668, 0.6367, 0.6211, 0.5915,
          0.8615, 0.5511, 0.7415, 0.6022, 0.5701, 0.5759])
    ]


@pytest.fixture
def bulk_lithium():
    return (
        np.array([(0.0, 0.0, 0.0)]) * ang,
        np.array([
            (-1.7385, 1.7385, 1.7385), (1.7385, -1.7385, 1.7385),
            (1.7385, 1.7385, -1.7385)]) * ang,
        (4, 4, 4),
        ['Li'],
        [1.0],
    )
