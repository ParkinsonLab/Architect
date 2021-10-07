""" This module implements the Dynamic Flux Balance Analysis with support for multi-organism communities.
This multi-organism version of the dFBA is derived from the Dynamic Multi-species Metabolic Modeling (DyMMM) framework.

For dFBA, please cite:
    Mahadevan et al. 2002. Dynamic flux balance analysis of diauxic growth in Escherichia coli.

For DyMMM, please cite:
    Zhuang et al. 2011. Genome-scale dynamic modeling of the competition between Rhodoferax and Geobacter in anoxic
        subsurface environments.
    Zhuang et al. 2012. The design of long-term effective uranium bioremediation strategy using a community metabolic
        model.

@TODO: implement the analytical solver

@author: Kai Zhuang

"""

__author__ = 'kaizhuang'

from collections import OrderedDict


def dFBAm(bioreactor, t0, tf, dt, initial_conditions=None, solver='dopri5', verbose=False):
    """
    Dynamic Flux Balance Analysis with Multi-organism support

    Arguments:
        bioreactor (Bioreactor): a bioreactor instance with defined organisms and metabolites
        t0 (float): initial time
        tf (float): final time
        dt (float): time step
        initial_conditions (list of float): the initial conditions in the order of V0, X0, S0 (default: None)
        solver (str): ODE solver.  (default: 'dopri5')
        verbose (bool): Verbosity control.  (default: False).

    Returns:
        results (OrderedDict): simulation results
    """
    t, y = bioreactor.integrate(t0, tf, dt, initial_conditions, solver, verbose)

    result = OrderedDict()
    result['time'] = t
    result['volume'] = y[:, 0]
    i = 0
    for organism in bioreactor.organisms:
        i += 1
        result[organism.id] = y[:, i]

    for metabolite in bioreactor.metabolites:
        i += 1
        result[metabolite] = y[:, i]

    return result


def dFBA(bioreactor, t0, tf, dt, initial_conditions=None, solver='dopri5', verbose=False):
    """
    dFBA() is a alias for dFBAm().
    It is intended to provide legacy support for the name "dFBA"
    """
    result = dFBAm(bioreactor, t0, tf, dt, initial_conditions, solver, verbose)
    return result


def DyMMM(bioreactor, t0, tf, dt, initial_conditions=None, solver='dopri5', verbose=False):
    """
    DyMMM() is a alias for dFBAm()
    It is intended to provide legacy support for the name "DyMMM"
    """
    result = dFBAm(bioreactor, t0, tf, dt, initial_conditions, solver, verbose)

    return result


def dFBA_combination(organisms, bioreactors, t0, tf, dt, initial_conditions=None, solver='dopri5', verbose=False):
    """
    Run dFBA for all possible combinations of the given organisms and reactors.

    For example, given two organisms "ecoli" and "scerevisiae", and two reactors "batch" and "fedbatch",
    the call dFBA_combination([ecoli, scerevisiae], [batch, fedbatch], t0, ft, dt] will perform four simulations:
        1. ecoli in batch
        2. ecoli in fedbatch
        3. scerevisiae in batch
        4. scerevisiae in fedbtach

    Arguments:
        organisms: list of Organism
        bioreactors: list of Bioreactor
        t0 (float): initial time
        tf (float): final time
        dt (float): time step
        initial_conditions (list of float): the initial conditions in the order of V0, X0, S0 (default: None)
        solver (str): ODE solver.  (default: 'dopri5')
        verbose (bool): Verbosity control.  (default: False).

    Returns:
        result (OrderedDict): a dictionary of dfba results
    """

    result = OrderedDict()

    for organism in organisms:
        for bioreactor in bioreactors:
            bioreactor.set_organisms([organism])
            dfba_result = dFBA(bioreactor, t0, tf, dt, initial_conditions, solver=solver, verbose=verbose)
            result[organism.id, bioreactor.id] = dfba_result

    return result