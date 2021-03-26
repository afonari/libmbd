#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from itertools import dropwhile

import numpy as np

from pymbd import ang
from pymbd.fortran import MBDGeom, with_mpi

__all__ = ()

# fmt: off
unit_cell = (
    np.array([
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
    list('HHHHHHHHHHHHHHCCCCCCNNOOOO'),
    [0.703, 0.703, 0.726, 0.726, 0.731, 0.731,
     0.727, 0.727, 0.754, 0.754, 0.750, 0.750,
     0.755, 0.755, 0.809, 0.809, 0.827, 0.827,
     0.834, 0.834, 0.840, 0.840, 0.886, 0.886,
     0.892, 0.892])
# fmt: on

RANK = None


def parse(output):
    blocks = [
        [l.split() for l in block.strip().split('\n')]
        for block in output.split('--------------')[1:-1]
    ]
    n_atoms = int(blocks[0][0][-1])
    timing = [
        {
            'id': int(words[0]),
            'level': int(words[1]),
            'label': ' '.join(words[2:-2]),
            'count': int(words[-2]),
            'time': float(words[-1]),
        }
        for words in list(dropwhile(lambda ws: ws[0] != 'id', blocks[1]))[1:]
    ]
    energy = float(blocks[2][0][-1])
    return {'n_atoms': n_atoms, 'timing': timing, 'energy': energy}


def make_supercell(coords, lattice, species, vol_ratios, sc):
    sc = np.array(sc)
    n_uc = np.product(sc)
    c = np.stack(
        np.meshgrid(range(sc[0]), range(sc[1]), range(sc[2])), axis=-1
    ).reshape(-1, 3)
    coords = ((c @ lattice)[:, None, :] + coords).reshape(-1, 3)
    lattice = lattice * sc[:, None]
    species = n_uc * species
    vol_ratios = n_uc * vol_ratios
    return coords, lattice, species, vol_ratios


def _print(*args):
    if not RANK:
        print(*args)


def run(supercell, k_grid, finite, force):
    if with_mpi:
        from mpi4py import MPI

        global RANK
        RANK = MPI.COMM_WORLD.Get_rank()
    _print('--------------')
    coords, lattice, species, vol_ratios = make_supercell(*unit_cell, supercell)
    _print('number of atoms:', len(coords))
    _print('--------------')
    geom = MBDGeom(coords) if finite else MBDGeom(coords, lattice, k_grid)
    with geom:
        ene, grad, *_ = geom.mbd_energy_species(species, vol_ratios, 0.83, force=force)
        geom.print_timing()
    ene = ene / len(coords)
    grad = grad[0]
    _print('--------------')
    _print('energy:', ene)
    _print('grad[0]:', grad)
    _print('--------------')


def main(args):
    parser = ArgumentParser()
    parser.add_argument(
        '--supercell',
        nargs=3,
        type=int,
        default=[1, 1, 1],
        metavar='N',
        help='supercell definition',
    )
    parser.add_argument(
        '--k-grid',
        nargs=3,
        type=int,
        default=[1, 1, 1],
        metavar='N',
        help='k-grid definition',
    )
    parser.add_argument(
        '--finite',
        action='store_true',
        help='run a finite system',
    )
    parser.add_argument(
        '--no-force',
        action='store_false',
        dest='force',
        help='switch off calculation of gradients',
    )
    args = parser.parse_args(args)
    run(**vars(args))


if __name__ == '__main__':
    main(sys.argv[1:])