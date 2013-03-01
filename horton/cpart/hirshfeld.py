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


import numpy as np

from horton.cpart.base import CPart
from horton.cache import just_once, Cache
from horton.log import log
from horton.dpart.linalg import solve_positive, quadratic_solver


__all__ = [
    'HirshfeldCPart', 'HirshfeldICPart', 'HirshfeldECPart',
]


# TODO: maxiter, tolerance parameter
# TODO: reduce duplicate code


class HirshfeldCPart(CPart):
    name = 'h'

    def __init__(self, system, ui_grid, moldens, proatomdb, smooth, scratch):
        '''
           **Arguments:**

           system
                The system to be partitioned.

           ui_grid
                The uniform integration grid based on the cube file.

           moldens
                The all-electron molecular density grid data.

           proatomdb
                The database of proatomic densities.

           smooth
                When set to True, no corrections are included to integrate
                the cusps.

           scratch
                An instance of the class Scratch to store large working arrays
        '''
        self._proatomdb = proatomdb
        CPart.__init__(self, system, ui_grid, moldens, smooth, scratch)

    def _get_proatomdb(self):
        return self._proatomdb

    proatomdb = property(_get_proatomdb)

    @just_once
    def _init_weight_corrections(self):
        funcs = []
        for i in xrange(self._system.natom):
            n = self._system.numbers[i]
            pn = self._system.pseudo_numbers[i]
            pn_expected = self._proatomdb.get_record(n, 0).pseudo_number
            # TODO: move this check to __init__
            if self._proatomdb.get_record(n, 0).pseudo_number != pn:
                raise ValueError('The pseudo number of atom %i does not match with the proatom database (%i!=%i)' % (i, pn, pn_expected))
            funcs.append((
                self._system.coordinates[i],
                [(('isolated_atom', i, 0), self._proatomdb.get_spline(n), float(pn))],
            ))
        self._ui_grid.compute_weight_corrections(funcs, cache=self._scratch)

    def _compute_proatom(self, index):
        if ('isolated_atom', index, 0) in self._scratch:
            self._scratch.rename(('isolated_atom', index, 0), ('at_weights', index))
            proatom = self._scratch.load('at_weights', index)
            proatom += 1e-100
        else:
            if log.do_medium:
                log('Computing proatom %i (%i)' % (index, self.system.natom))
            proatom = self._zeros()
            # Construct the pro-atom
            number = self._system.numbers[index]
            center = self._system.coordinates[index]
            spline = self._proatomdb.get_spline(number)
            self._ui_grid.eval_spline(spline, center, proatom)
            proatom += 1e-100
            self._scratch.dump('at_weights', index, proatom)

    def _compute_promoldens(self):
        promoldens = self._zeros()
        proatom = self._zeros()
        for i in xrange(self._system.natom):
            self._scratch.load('at_weights', i, output=proatom)
            promoldens += proatom
        self._scratch.dump('promoldens', promoldens)

    def _compute_at_weights(self):
        promoldens = self._scratch.load('promoldens')
        proatom = self._zeros()
        for i in xrange(self._system.natom):
            self._scratch.load('at_weights', i, output=proatom)
            proatom /= promoldens
            self._scratch.dump('at_weights', i, proatom)

    @just_once
    def _init_at_weights(self):
        # A) Compute all the pro-atomic densities.
        for i in xrange(self._system.natom):
            self._compute_proatom(i)
        self._compute_promoldens()
        self._compute_at_weights()


class HirshfeldICPart(HirshfeldCPart):
    name = 'hi'

    def _get_isolated_atom(self, i, charge, output):
        key = ('isolated_atom', i, charge)
        if key in self._scratch:
            self._scratch.load(*key, output=output)
        else:
            number = self._system.numbers[i]
            center = self._system.coordinates[i]
            spline = self._proatomdb.get_spline(number, charge)
            if log.do_medium:
                log('Computing isolated atom %i (n=%i, q=%+i)' % (i, number, charge))
            output[:] = 0
            self._ui_grid.eval_spline(spline, center, output)
            self._scratch.dump(*key, data=output)

    def _compute_proatom(self, i, target_charge):
        # Pro-atoms are (temporarily) stored in at_weights for efficiency.
        proatom = self._zeros()
        # Construct the pro-atom
        icharge = int(np.floor(target_charge))
        self._get_isolated_atom(i, icharge, proatom)
        if float(icharge) != target_charge:
            x = target_charge - icharge
            proatom *= 1-x
            ipseudo_pop = self.system.pseudo_numbers[i] - icharge
            if ipseudo_pop > 1:
                tmp = self._zeros()
                self._get_isolated_atom(i, icharge+1, tmp)
                tmp *= x
                proatom += tmp
        proatom += 1e-100 # avoid division by zero
        self._scratch.dump('at_weights', i, proatom)

    @just_once
    def _init_at_weights(self):
        self._local_cache = Cache()

        old_charges = np.zeros(self._system.natom)
        if log.medium:
            log.hline()
            log('Iteration       Change')
            log.hline()
        for counter in xrange(500):
            # Construct pro-atoms
            for i in xrange(self._system.natom):
                self._compute_proatom(i, old_charges[i])
            self._compute_promoldens()
            self._compute_at_weights()
            new_populations = self._compute_populations()
            new_charges = self.system.numbers - new_populations
            change = abs(new_charges - old_charges).max()
            if log.medium:
                log('%9i   %10.5e' % (counter, change))
            if change < 1e-4:
                break

            old_charges = new_charges

        if log.medium:
            log.hline()

        self._cache.dump('populations', new_populations)
        del self._local_cache


class HirshfeldECPart(HirshfeldICPart):
    name = 'he'

    def _get_constant_fn(self, i, output):
        key = ('isolated_atom', i, 0)
        if key in self._scratch:
            self._scratch.load(*key, output=output)
        else:
            number = self._system.numbers[i]
            center = self._system.coordinates[i]
            spline = self._proatomdb.get_spline(number)
            if log.do_medium:
                log('Computing constant fn %i (n=%i)' % (i, number))
            output[:] = 0
            self._ui_grid.eval_spline(spline, center, output)
            self._scratch.dump(*key, data=output)

    def _get_basis_fn(self, i, j, output):
        # A local cache is used that only exists during _init_at_weights:
        key = ('basis', i, j)
        if key in self._scratch:
            self._scratch.load(*key, output=output)
        else:
            number = self._system.numbers[i]
            charges = self._proatomdb.get_charges(number)
            center = self._system.coordinates[i]
            spline = self._proatomdb.get_spline(number, {charges[j+1]: 1, charges[j]: -1})
            if log.do_medium:
                log('Computing basis fn %i_%i (n=%i, q: %+i_%+i)' % (i, j, number, charges[j+1], charges[j]))
            output[:] = 0
            self._ui_grid.eval_spline(spline, center, output)
            self._scratch.dump(*key, data=output)

    def _compute_proatom(self, i, target_charge):
        # Pro-atoms are (temporarily) stored in at_weights for efficiency.
        if ('at_weights', i) not in self._scratch:
            # just use the Hirshfeld definition to get started
            proatom = self._zeros()
            self._get_constant_fn(i, proatom)
            proatom += 1e-100
            self._scratch.dump('at_weights', i, proatom)
        else:
            # 1) construct aim in temporary array
            at_weights = self._scratch.load('at_weights', i)
            aimdens = self._scratch.load('moldens')
            aimdens *= at_weights

            #    rename variables for clarity
            work0 = at_weights
            del at_weights
            work1 = self._zeros()

            # 2) setup equations
            number = self._system.numbers[i]
            charges = np.array(self._proatomdb.get_charges(number, safe=True))
            neq = len(charges)-1

            #    compute A
            A, new = self._cache.load('A', i, alloc=(neq, neq))
            if new:
                for j0 in xrange(neq):
                    self._get_basis_fn(i, j0, work0)
                    for j1 in xrange(j0+1):
                        self._get_basis_fn(i, j1, work1)
                        A[j0,j1] = self._ui_grid.integrate(work0, work1)
                        A[j1,j0] = A[j0,j1]


                #    precondition the equations
                scales = np.diag(A)**0.5
                A /= scales
                A /= scales.reshape(-1, 1)
                if log.do_medium:
                    evals = np.linalg.eigvalsh(A)
                    cn = abs(evals).max()/abs(evals).min()
                    sr = abs(scales).max()/abs(scales).min()
                    log('                   %10i: CN=%.5e SR=%.5e' % (i, cn, sr))
                self._cache.dump('scales', i, scales)
            else:
                scales = self._cache.load('scales', i)

            #    compute B and precondition
            self._get_constant_fn(i, work1)
            aimdens -= work1
            B = np.zeros(neq, float)
            for j0 in xrange(neq):
                self._get_basis_fn(i, j0, work0)
                B[j0] = self._ui_grid.integrate(aimdens, work0)
            B /= scales

            # 3) find solution
            lc_pop = (np.ones(neq)/scales, -target_charge)
            #coeffs = solve_positive(A, B, [lc_pop])
            lcs_par = []
            for j0 in xrange(neq):
                lc = np.zeros(neq)
                lc[j0] = 1.0/scales[j0]
                lcs_par.append((lc, -1))
            coeffs = quadratic_solver(A, B, [lc_pop], lcs_par, rcond=0)
            # correct for scales
            coeffs /= scales

            if log.do_medium:
                log('                   %10i:&%s' % (i, ' '.join('% 6.3f' % c for c in coeffs)))

            # 4) construct the pro-atom
            proatom = work1
            del work1

            for j0 in xrange(neq):
                work0[:] = 0
                self._get_basis_fn(i, j0, work0)
                work0 *= coeffs[j0]
                proatom += work0

            proatom += 1e-100
            self._scratch.dump('at_weights', i, proatom)
