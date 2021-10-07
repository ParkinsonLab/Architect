# This is a copy of the original gapfilling.py that Nirvana Nursimulu modified
# for Architect's specific purposes.

from __future__ import division
from __future__ import print_function
from carveme.reconstruction.utils import medium_to_constraints
from framed.model.transformation import disconnected_metabolites
from framed.solvers import solver_instance
from framed.solvers.solver import VarType, Status


def gapFill(model, universe, constraints=None, min_growth=0.1, scores=None, inplace=True, bigM=1e3, abstol=1e-9,
            solver=None, tag=None, pool_size=0, pool_gap=None, int_constr=None):
    """ Gap Fill a metabolic model by adding reactions from a reaction universe

    Args:
        model (CBModel): original model
        universe (CBModel): universe model
        constraints (dict): additional constraints (optional)
        min_growth (float): minimum growth rate (default: 0.1)
        scores (dict): reaction scores (optional, see notes)
        inplace (bool): modify given model in place (default: True)
        bigM (float): maximal reaction flux (default: 1000)
        abstol (float): minimum threshold to consider a reaction active (default: 1e-9)
        solver (Solver): solver instance (optional)
        tag (str): add a metadata tag to gapfilled reactions (optional)
        pool_size (int): solution pool of given size (optional)
        pool_gap (float): for MIP algo; maximum relative gap for solutions in pool (optional)

    Returns:
        lists_of_added_reactions: added reactions

    Notes:
        Scores can be used to make some reactions more likely to be included.
        Scored reactions have a penalty of 1/(1+score), which varies between [0, 1].
        Unscored reactions have a penalty of 1.
    """

    new_reactions = set(universe.reactions) - set(model.reactions)

    model = merge_models(model, universe, inplace, tag=tag)

    for r_id in new_reactions:
        if r_id.startswith('R_EX'):
            model.set_lower_bound(r_id, 0)

    if not solver:
        solver = solver_instance(model)

    if not scores:
        scores = {}

    if not hasattr(solver, '_gapfill_flag'):
        solver._gapfill_flag = True

        for r_id in new_reactions:
            solver.add_variable('y_' + r_id, 0, 1, vartype=VarType.BINARY, update_problem=False)

        solver.update()

        for r_id in new_reactions:
            solver.add_constraint('lb_' + r_id, {r_id: 1, 'y_'+r_id: bigM}, '>', 0, update_problem=False)
            solver.add_constraint('ub_' + r_id, {r_id: 1, 'y_'+r_id: -bigM}, '<', 0, update_problem=False)

        biomass = model.biomass_reaction
        solver.add_constraint('min_growth', {biomass: 1}, '>', min_growth, update_problem=False)

        solver.update()

    objective = {'y_'+r_id: 1.0 / (1.0 + scores.get(r_id, 0.0)) for r_id in new_reactions}

    if int_constr is not None:
        solution = solver.solve(linear=objective, minimize=True, constraints=constraints, pool_size=pool_size, pool_gap=pool_gap, int_constr=int_constr)
    else:
        solution = solver.solve(linear=objective, minimize=True, constraints=constraints, pool_size=pool_size, pool_gap=pool_gap)

    solutions = []
    if pool_size == 0:
        if solution.status != Status.OPTIMAL:
            raise RuntimeError('Failed to gapfill model for medium {}'.format(tag))		
        solutions.append(solution)
    else:
        solutions = solution	

    lists_of_added_reactions = []		
    for i, solution in enumerate(solutions):

        inactive = [r_id for r_id in new_reactions if abs(solution.values[r_id]) < abstol]
        added_reactions = new_reactions - set(inactive)
        lists_of_added_reactions.append(added_reactions)

    return lists_of_added_reactions	



def multiGapFill(model, universe, media, media_db, min_growth=0.1, max_uptake=10, scores=None, inplace=True, bigM=1e3,
                 exchange_format=None, pool_size=0, pool_gap=None, int_constr=0.00000001):
    """ Gap Fill a metabolic model for multiple environmental conditions

    Args:
        model (CBModel): original model
        universe (CBModel): universe model
        media (list): list of growth media ids
        media_db (dict): growth media database (see notes)
        min_growth (float): minimum growth rate (default: 0.1)
        max_uptake (float): maximum uptake rate (default: 10)
        scores (dict): reaction scores (optional, see *gapFill* for details)
        inplace (bool): modify given model in place (default: True)
        bigM (float): maximal reaction flux (default: 1000)
        pool_size (int): solution pool of given size (optional)
        pool_gap (float): for MIP algo; maximum relative gap for solutions in pool (optional)
		
    Returns:
        CBModel: gap filled model (if inplace=False)

    Notes:
        *media_db* is a dict from medium name to the list of respective compounds.
    """
	
    if not inplace:
        model = model.copy()

    new_reactions = set(universe.reactions) - set(model.reactions)

    for r_id in new_reactions:
        if r_id.startswith('R_EX'):
            universe.set_lower_bound(r_id, 0)

    merged_model = merge_models(model, universe, inplace=False)
    solver = solver_instance(merged_model)

    # For Architect: Needed to fix this so that we use only one medium.  Actual value of media does not matter.
    for medium_name in media:
        if medium_name in media_db:
            compounds = media_db[medium_name]
            constraints = medium_to_constraints(merged_model, compounds, max_uptake=max_uptake, inplace=False,
                                                exchange_format=exchange_format, verbose=False)
            lists_of_added_reactions = gapFill(model, universe, constraints=constraints, min_growth=min_growth,
                    scores=scores, inplace=True, bigM=bigM, solver=solver, tag=medium_name, pool_size=pool_size, pool_gap=pool_gap, int_constr=int_constr)
            return lists_of_added_reactions
        else:
            print('Medium {} not in database, ignored.'.format(medium_name))


def merge_models(model1, model2, inplace=True, tag=None):

    if not inplace:
        model1 = model1.copy()

    for c_id, comp in model2.compartments.items():
        if c_id not in model1.compartments:
            model1.compartments[c_id] = comp

    for m_id, met in model2.metabolites.items():
        if m_id not in model1.metabolites:
            model1.metabolites[m_id] = met

    for r_id, rxn in model2.reactions.items():
        if r_id not in model1.reactions:
            model1.reactions[r_id] = rxn
            if tag:
                rxn.metadata['GAP_FILL'] = tag

    return model1
