#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Horton is a Density Functional Theory program.
# Copyright (C) 2011-2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Horton.
#
# Horton is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Horton is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--


import sys, argparse, os

import h5py as h5
from horton import System, cpart_schemes, Cell, ProAtomDB, log, ArrayStore
from horton.scripts.common import reduce_data, store_args, parse_pbc, iter_elements


def parse_args():
    parser = argparse.ArgumentParser(prog='horton-cpart.py',
        description='Partition the density from a cube file.')

    parser.add_argument('cube',
        help='The cube file.')
    parser.add_argument('scheme', choices=cpart_schemes.keys(),
        help='The scheme to be used for the partitioning')
    parser.add_argument('atoms',
        help='An HDF5 file with atomic reference densities.')
    parser.add_argument('--reduce', '-r', default=1, type=int,
        help='Reduce the grid by subsamping with the given stride in all three '
             'directions. Zero and negative values are ignored. '
             '[default=%(default)s]')
    parser.add_argument('--overwrite', default=False, action='store_true',
        help='Overwrite existing output in the HDF5 file')
    parser.add_argument('--store', choices=('fake', 'core', 'disk'), default='core',
        help='Controls the storage of large intermediate arrays. fake: disables '
             'storage of such intermediate arrays. core: the arrays are kept in '
             'memory. disk: the arrays are stored in an HDF5 file on disk. For '
             'the last case, see the --tmp option. [default=%(default)s]')
    parser.add_argument('--tmp', type=str, default='.',
        help='A directory where the temporary scratch file can be written. '
             'This is only relevant with option --store=disk. '
             '[default=%(default)s]')
    parser.add_argument('--debug', default=False, action='store_true',
        help='Add additional internal results to a debug subgroup.')
    parser.add_argument('--suffix', default=None, type=str,
        help='Add an additional suffix to the HDF5 output group.')
    parser.add_argument('--pbc', default='111', type=str,
        help='Specify the periodicity. The three digits refer to a, b and c '
             'cell vectors. 1=periodic, 0=aperiodic.')

    parser.add_argument('--wcor', default='1-118', type=str,
        help='The elements for which weight corrections are used. This can be '
             'a comma-separated list of element symbols and/or numbers that '
             'includes ranges. For example, "B,7-9" corresponds to boron, '
             'nitrogen, oxygen and fluorine. The argument 0 will disable '
             'weight corrections entirely.')
    parser.add_argument('--wcor-rcut-max', default=2.0, type=float,
        help='Maximum cutoff radious for weight corrections in Bohr')
    parser.add_argument('--wcor-rcond', default=0.1, type=float,
        help='The regularization strength used for the weight corrections')
    parser.add_argument('--maxiter', '-i', default=500, type=int,
        help='The maximum allowed number of iterations. [default=%(default)s]')
    parser.add_argument('--threshold', '-t', default=1e-6, type=float,
        help='The iterative scheme is converged when the maximum change of '
             'the charges between two iterations drops below this threshold. '
             '[default=%(default)s]')

    return parser.parse_args()


def main():
    args = parse_args()

    # check if the folder is already present in the output file
    fn_h5 = args.cube + '.h5'
    grp_name = '%s_r%i' % (args.scheme, args.reduce)
    if args.suffix is not None:
        grp_name += '_'+args.suffix

    if os.path.isfile(fn_h5):
        with h5.File(fn_h5, 'r') as f:
            if 'cpart/%s' % grp_name in f and not args.overwrite:
                if log.do_warning:
                    log.warn('Skipping because "%s" is already present in the output.' % grp_name)
                return

    # Load the system
    sys = System.from_file(args.cube)
    ui_grid = sys.props['ui_grid']
    ui_grid.pbc[:] = parse_pbc(args.pbc)
    moldens = sys.props['cube_data']

    # Reduce the grid if required
    if args.reduce > 1:
        moldens, ui_grid = reduce_data(moldens, ui_grid, args.reduce)

    # Load the proatomdb
    proatomdb = ProAtomDB.from_file(args.atoms)

    # Pick the ArrayStorage options
    mode = args.store
    if mode == 'fake':
        store_fn = None
    else:
        store_fn = '%s/_scratch-PID-%i.h5' % (args.tmp, os.getpid())
    if mode == 'disk' and log.do_medium:
        log('Using scratch file: %s' % store_fn)

    # List of element numbers for which weight corrections are needed:
    wcor_numbers = list(iter_elements(args.wcor))

    # Run the partitioning
    with ArrayStore.from_mode(mode, store_fn) as store:
        CPartClass = cpart_schemes[args.scheme]
        kwargs = dict((key, val) for key, val in vars(args).iteritems() if key in CPartClass.options)
        cpart = cpart_schemes[args.scheme](
            sys, ui_grid, moldens, proatomdb, store, wcor_numbers,
            args.wcor_rcut_max, args.wcor_rcond, **kwargs)
        names = cpart.do_all()

    # Store the results in an HDF5 file
    with h5.File(fn_h5) as f:
        # Store system
        sys_grp = f.require_group('system')
        del sys.props['cube_data'] # first drop potentially large array
        sys.to_file(sys_grp)

        # Store results
        grp_cpart = f.require_group('cpart')
        if grp_name in grp_cpart:
            del grp_cpart[grp_name]
        grp = grp_cpart.create_group(grp_name)
        for name in names:
            grp[name] = cpart[name]

        # Store command line arguments
        store_args(args, grp)

        if args.debug:
            # Store additional data for debugging
            if 'debug' in grp:
                del grp['debug']
            grp_debug = grp.create_group('debug')
            for debug_key in cpart._cache._store:
                debug_name = '_'.join(str(x) for x in debug_key)
                if debug_name not in names:
                    grp_debug[debug_name] = cpart._cache.load(*debug_key)


if __name__ == '__main__':
    main()
