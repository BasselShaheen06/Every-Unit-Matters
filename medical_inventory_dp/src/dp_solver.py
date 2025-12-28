from .cost_model import CostModel

class DPSolver:
    """
        T: Number of planning periods
        demand: List of demand values for each period
        max_storage: Maximum inventory capacity
        cost_model: CostModel instance for cost calculations
        dp_table: Memoization table for DP values
        decision_table: Optimal decisions for each (t, I) state
    """
    
    def __init__(self, T, demand, max_storage, cost_model, initial_inventory):

        assert T > 0, "Planning horizon must be positive"
        assert len(demand) == T, f"Demand list length must equal T ({T})"
        assert max_storage > 0, "Storage capacity must be positive"
        assert initial_inventory >= 0, "Initial inventory must be non-negative"
        assert initial_inventory <= max_storage, "Initial inventory exceeds capacity"
        
        self.T = T
        self.demand = demand
        self.max_storage = max_storage
        self.cost_model = cost_model
        self.initial_inventory = initial_inventory
        
        # DP tables: indexed by (period, inventory)
        # dp_table[t][I] = minimum cost from period t to T with inventory I
        self.dp_table = {}  #dict{tuple(int, int), float}

        # decision_table[t][I] = optimal order ((quantity)) at period t with inventory I
        self.decision_table = {} #dict{tuple(int, int), float}
        
        self._solved = False
    
    def compute_dp(self, t, inventory):
        """ 
        returns:
            minimum cost from period t to the end
        """
        state = (t, inventory)
        
        if state in self.dp_table:
            return self.dp_table[state]
        
        demand_t = self.demand[t]   #demand = [10,21,11,2,11]
        best_cost = float('inf') # any number will be better than inf.
        best_order = 0
        
        # Try all feasible order quantities
        # Order quantity is limited by remaining storage capacity
        max_order = self.max_storage - inventory
        
        for q in range(0, max_order + 1):
            # Compute immediate cost and next state
            period_cost, next_inventory, shortage = self.cost_model.compute_period_cost(q,inventory,demand_t)

            # Get future cost (0 if last period)
            if t == self.T - 1:
                future_cost = 0.0
            else:
                future_cost = self._get_future_cost(t + 1, next_inventory)
            
            total_cost = period_cost + future_cost
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_order = q
        
        self.dp_table[state] = best_cost
        self.decision_table[state] = best_order
        
        return best_cost

    
    
    def _get_future_cost(self, t, inventory):
        """
        get the DP value for a future state.
            
        returns:
            DP value if computed, infinity otherwise
        """
        state = (t, inventory)
        if state in self.dp_table:
            return self.dp_table[state]
        # If not computed yet, compute it (should be computed in backward pass)
        return self._compute_dp(t, inventory)
    
    def solve(self):

        # backward induction: start from period T-1 (0-indexed) to 0
        for t in range(self.T - 1, -1, -1): 
            for I in range(self.max_storage + 1):
                self.compute_dp(t, I)
        
        self._solved = True
        return self.dp_table.get((0, self.initial_inventory))


    def get_optimal_decision(self, t, inventory):
        """
        Get the optimal order quantity for a given state.
        
        Args:
            t: Period
            inventory: Inventory level
            
        Returns:
            Optimal order quantity, or None if state not computed
        """
        return self.decision_table.get((t, inventory))
    
    def get_minimum_cost(self) -> float:
        """
        Get the minimum total cost.
        
        Returns:
            Minimum cost starting from initial inventory
        """
        if not self._solved:
            self.solve()
        return self.dp_table.get((0, self.initial_inventory), float('inf'))
    
    def is_solved(self) -> bool:
        """Check if the DP has been solved."""
        return self._solved
