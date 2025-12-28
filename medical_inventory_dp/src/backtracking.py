# Backtracking Module - Medical Supply Chain Inventory Optimization
"""
Reconstructs optimal ordering schedule from the DP solution.
"""

from typing import TYPE_CHECKING
from .cost_model import CostModel

if TYPE_CHECKING:
    from .dp_solver import DPSolver


def reconstruct_schedule(solver: 'DPSolver') -> list[int]:
    """
    Reconstruct the optimal ordering schedule from the DP solution.
    
    Args:
        solver: Solved DPSolver instance
        
    Returns:
        List of optimal order quantities for each period
    """
    if not solver.is_solved():
        solver.solve()
    
    schedule = []
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
            current_inventory = min(available - demand_t, solver.max_storage)
        else:
            current_inventory = 0
    
    return schedule


def compute_inventory_trajectory(schedule: list[int], demand: list[int], 
                                  initial_inventory: int, 
                                  max_storage: int) -> list[int]:
    """
    Compute inventory levels over time given an ordering schedule.
    
    Args:
        schedule: Order quantities for each period
        demand: Demand for each period
        initial_inventory: Starting inventory
        max_storage: Maximum storage capacity
        
    Returns:
        List of ending inventory levels for each period
    """
    T = len(schedule)
    assert len(demand) == T, "Schedule and demand must have same length"
    
    trajectory = []
    current_inventory = initial_inventory
    
    for t in range(T):
        available = current_inventory + schedule[t]
        
        if available >= demand[t]:
            ending_inventory = min(available - demand[t], max_storage)
        else:
            ending_inventory = 0
        
        trajectory.append(ending_inventory)
        current_inventory = ending_inventory
    
    return trajectory


def compute_shortage_trajectory(schedule: list[int], demand: list[int],
                                 initial_inventory: int) -> list[int]:
    """
    Compute shortages over time given an ordering schedule.
    
    Args:
        schedule: Order quantities for each period
        demand: Demand for each period
        initial_inventory: Starting inventory
        
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


def compute_cost_breakdown(schedule: list[int], demand: list[int],
                            initial_inventory: int, max_storage: int,
                            cost_model: CostModel) -> dict:
    """
    Compute detailed cost breakdown for a schedule.
    
    Args:
        schedule: Order quantities for each period
        demand: Demand for each period
        initial_inventory: Starting inventory
        max_storage: Maximum storage capacity
        cost_model: CostModel instance
        
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
            ending_inventory = min(available - d, max_storage)
            shortage = 0
        else:
            ending_inventory = 0
            shortage = d - available
        
        # Storage and shortage costs
        total_storage += cost_model.compute_storage_cost(ending_inventory)
        total_shortage += cost_model.compute_shortage_cost(shortage)
        
        current_inventory = ending_inventory
    
    return {
        "ordering": total_ordering,
        "storage": total_storage,
        "shortage": total_shortage,
        "total": total_ordering + total_storage + total_shortage
    }


def generate_solution_report(solver: 'DPSolver') -> dict:
    """
    Generate a complete solution report.
    
    Args:
        solver: Solved DPSolver instance
        
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
