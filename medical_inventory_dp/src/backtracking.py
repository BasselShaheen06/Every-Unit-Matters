from .cost_model import CostModel
from .dp_solver import DPSolver

def reconstruct_schedule(solver) -> list[int]:
    """
    Reconstruct the optimal ordering schedule from the DP solution.
    
    Args:
        solver: Solved DPSolver instance
        
    Returns:
        List of optimal order quantities for each period
    """
    if not solver.is_solved():
        solver.solve()
    
    schedule = [] # we will put the best order quantity for each period here
    current_inventory = solver.initial_inventory
    
    for t in range(solver.T):
        # Get optimal order for this state
        optimal_order = solver.get_optimal_decision(t, current_inventory)
        
        if optimal_order is None:
            # Fallback: order exactly what's needed
            optimal_order = max(0, solver.demand[t] - current_inventory)
        
        schedule.append(optimal_order)
        
        # Update inventory for next period
        available = current_inventory + optimal_order
        demand_t = solver.demand[t]
        
        if available >= demand_t:
            current_inventory = available - demand_t
        else:
            current_inventory = 0
    
    return schedule # e.g [15, 10, 8]


def compute_inventory_trajectory(schedule, demand, initial_inventory,  max_storage) -> list[int]:
    """
    Compute inventory levels over time given an ordering schedule.
    
    Returns:
        List of ending inventory levels for each period
    """
    T = len(schedule)
    assert len(demand) == T # if this condition was not true, then the error will be raised
    , "Schedule and demand must have same length" 
    
    trajectory = []
    current_inventory = initial_inventory
    
    for t in range(T):
        available = current_inventory + schedule[t]
        
        if available >= demand[t]:
            ending_inventory = available - demand[t]
        else:
            ending_inventory = 0
        
        trajectory.append(ending_inventory)
        current_inventory = ending_inventory
    
    return trajectory


def compute_shortage_trajectory(schedule, demand, initial_inventory) -> list[int]:
    """
    Compute shortages over time given an ordering schedule.
    
    Returns:
        List of shortage amounts for each period
    """
    T = len(schedule)
    shortages = []
    current_inventory = initial_inventory
    
    for t in range(T):
        available = current_inventory + schedule[t]
        
        if available >= demand[t]:
            shortage = 0
            current_inventory = available - demand[t]
        else:
            shortage = demand[t] - available
            current_inventory = 0
        
        shortages.append(shortage)
    
    return shortages


def compute_cost_breakdown(schedule, demand, initial_inventory, max_storage, cost_model) -> dict:
    """
    Compute detailed cost breakdown for a schedule.
        
    Returns:
        Dictionary with ordering, storage, shortage costs and total
    """
    T = len(schedule)
    
    total_ordering = 0.0
    total_storage = 0.0
    total_shortage = 0.0
    
    current_inventory = initial_inventory
    
    for t in range(T):
        q = schedule[t]
        d = demand[t]
        
        # Ordering cost
        total_ordering += cost_model.compute_ordering_cost(q)
        
        # Compute ending inventory and shortage
        available = current_inventory + q
        
        if available >= d:
            ending_inventory = available - d
            shortage = 0
        else:
            ending_inventory = 0
            shortage = d - available
        
        # Storage and shortage costs
        total_storage += cost_model.compute_storage_cost(ending_inventory)
        total_shortage += cost_model.compute_shortage_cost(shortage)
        
        current_inventory = ending_inventory #update inventory for next period
    
    return {
        "ordering": total_ordering,
        "storage": total_storage,
        "shortage": total_shortage,
        "total": total_ordering + total_storage + total_shortage
    }


def generate_solution_report(solver) -> dict:
    """
    Generate a complete solution report.
        
    Returns:
        Dictionary with full solution details
    """
    schedule = reconstruct_schedule(solver)
    trajectory = compute_inventory_trajectory(
        schedule, solver.demand, solver.initial_inventory, solver.max_storage
    )
    shortages = compute_shortage_trajectory(
        schedule, solver.demand, solver.initial_inventory
    )
    cost_breakdown = compute_cost_breakdown(
        schedule, solver.demand, solver.initial_inventory, 
        solver.max_storage, solver.cost_model
    )
    
    return {
        "order_schedule": schedule,
        "inventory_levels": trajectory,
        "shortages": shortages,
        "total_cost": cost_breakdown["total"],
        "cost_breakdown": cost_breakdown,
        "parameters": {
            "T": solver.T,
            "demand": solver.demand,
            "initial_inventory": solver.initial_inventory,
            "max_storage": solver.max_storage,
            "costs": solver.cost_model.to_dict()
        }
    }
