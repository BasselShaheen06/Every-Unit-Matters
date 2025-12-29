import numpy as np

class InventoryDPSolver:
    """
    Dynamic Programming solver for medical inventory optimization.
    Supports both optimal DP solution and greedy baseline comparison.
    """
    
    def __init__(self, T, demand, max_storage, initial_inventory,
                 c_order_fixed, c_unit, c_storage,
                 c_emergency_fixed, c_emergency_unit):
        """Initialize the solver with problem parameters."""
        self.T = T
        self.demand = demand
        self.max_storage = max_storage
        self.initial_inventory = initial_inventory

        # Cost parameters
        self.c_order_fixed = c_order_fixed
        self.c_unit = c_unit
        self.c_storage = c_storage
        self.c_emergency_fixed = c_emergency_fixed
        self.c_emergency_unit = c_emergency_unit

        self.dp = None
        self.decision = None
    
    def normal_order_cost(self, n):
        """Calculate cost of a normal order."""
        return 0 if n == 0 else self.c_order_fixed + self.c_unit * n

    def emergency_order_cost(self, n):
        """Calculate cost of an emergency order."""
        return 0 if n == 0 else self.c_emergency_fixed + self.c_emergency_unit * n

    def storage_cost(self, n):
        """Calculate storage cost."""
        return self.c_storage * n

    def solve(self):
        """Solve using Dynamic Programming."""
        INF = float('inf')
        self.dp = np.full((self.T + 1, self.max_storage + 1), INF)
        self.decision = np.zeros((self.T + 1, self.max_storage + 1), dtype=int)
        
        # Terminal condition
        self.dp[self.T, :] = 0

        # Backward induction
        for t in range(self.T - 1, -1, -1):
            for I in range(self.max_storage + 1):
                best = INF
                best_q = 0
                
                for q in range(self.max_storage - I + 1):
                    cost, nxt = self._period_cost(I, q, t)
                    val = cost + self.dp[t + 1, nxt]
                    
                    if val < best:
                        best = val
                        best_q = q
                        
                self.dp[t, I] = best
                self.decision[t, I] = best_q

    def _period_cost(self, I, q, t):
        """Calculate cost for a single period."""
        demand = self.demand[t]
        inv = I + q
        cost = self.normal_order_cost(q)

        if inv >= demand:
            rem = inv - demand
            cost += self.storage_cost(rem)
        else:
            shortage = demand - inv
            cost += self.emergency_order_cost(shortage)
            rem = 0

        return cost, rem

    def backtrack(self):
        """Generate optimal schedule from DP solution."""
        schedule = []
        I = self.initial_inventory
        
        for t in range(self.T):
            q = self.decision[t, I]
            inv = I + q
            d = self.demand[t]

            if inv >= d:
                emergency = 0
                end = inv - d
            else:
                emergency = d - inv
                end = 0

            schedule.append({
                "Period": t,
                "Start": I,
                "Order": q,
                "Demand": d,
                "Emergency": emergency,
                "End": end,
                "Cost": (
                    self.normal_order_cost(q)
                    + self.emergency_order_cost(emergency)
                    + self.storage_cost(end)
                )
            })

            I = end

        return schedule, self.dp[0, self.initial_inventory]

    def solve_greedy(self):
        """Greedy baseline: Order exactly the demand each period."""
        schedule = []
        total_cost = 0
        I = self.initial_inventory
        
        for t in range(self.T):
            d = self.demand[t]
            q = min(d, self.max_storage - I)
            inv = I + q
            
            cost = self.normal_order_cost(q)
            
            if inv >= d:
                emergency = 0
                end = inv - d
            else:
                emergency = d - inv
                cost += self.emergency_order_cost(emergency)
                end = 0
            
            cost += self.storage_cost(end)
            total_cost += cost
            
            schedule.append({
                "Period": t,
                "Start": I,
                "Order": q,
                "Demand": d,
                "Emergency": emergency,
                "End": end,
                "Cost": cost
            })
            
            I = end
        
        return schedule, total_cost