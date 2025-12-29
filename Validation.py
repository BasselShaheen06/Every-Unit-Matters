import numpy as np

# ==========================================
# 🎨 COLOR CODES
# ==========================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'  # Best Decision
    GRAY = '\033[90m'   # Suboptimal
    FAIL = '\033[91m'   # Infeasible (X)
    BOLD = '\033[1m'
    END = '\033[0m'

class ClassicDPVerifier:
    def __init__(self, T, demand, max_storage, initial_inventory,
                 c_order_fixed, c_unit, c_storage,
                 c_emergency_fixed, c_emergency_unit):
        
        self.T = T
        self.demand = demand
        self.max_storage = max_storage
        self.initial_inventory = initial_inventory
        
        # Costs
        self.c_order_fixed = c_order_fixed
        self.c_unit = c_unit
        self.c_storage = c_storage
        self.c_emergency_fixed = c_emergency_fixed
        self.c_emergency_unit = c_emergency_unit
        
        # DP Tables
        self.dp = np.full((self.T + 1, self.max_storage + 1), float('inf'))
        self.decision = np.zeros((self.T + 1, self.max_storage + 1), dtype=int)

    def _calc_total_cost(self, I, q, t):
        """
        Calculates the Total Cost = Immediate Cost + Future Cost
        Returns: (Total Cost, Is_Feasible)
        """
        # --- 1. LOGIC CHECK: RECEIVING LIMIT ---
        # (Matches your InventoryDPSolver)
        theoretical_max = self.demand[t] + self.max_storage - I
        receiving_limit = self.max_storage
        max_allowed_q = max(0, min(theoretical_max, receiving_limit))

        # Constraint A: Cannot order more than allowed logic
        if q > max_allowed_q:
            return float('inf'), False

        # --- 2. COST CALCULATION ---
        demand = self.demand[t]
        inv_after = I + q
        
        # Constraint B: Physics - Warehouse Capacity
        # Even if logic allows ordering, does it fit?
        if inv_after - demand > self.max_storage:
             # Note: Usually we check inv_after > max, but strictly 
             # ending inventory is what matters for storage cost.
             # However, physically fitting the shipment matters too.
             # We stick to your logic: "next_inv > max_storage" check.
             pass 

        # Immediate Cost
        order_cost = (self.c_order_fixed + self.c_unit * q) if q > 0 else 0
        
        if inv_after >= demand:
            shortage = 0
            emergency_cost = 0
            next_inv = inv_after - demand
        else:
            shortage = demand - inv_after
            emergency_cost = self.c_emergency_fixed + (self.c_emergency_unit * shortage)
            next_inv = 0
            
        holding_cost = next_inv * self.c_storage
        immediate_cost = order_cost + emergency_cost + holding_cost
        
        # Future Cost
        if next_inv > self.max_storage:
            return float('inf'), False
            
        future_cost = self.dp[t+1, next_inv]
        
        return immediate_cost + future_cost, True

    def solve(self):
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"CLASSIC DP TABLE VISUALIZATION")
        print(f"{'='*60}{Colors.END}")
        
        # Step 0: Terminal Condition
        self.dp[self.T, :] = 0
        print(f"\n{Colors.BLUE}Stage t={self.T} (Terminal):{Colors.END} Future Costs = 0")

        # Step 1: Backward Induction
        for t in range(self.T - 1, -1, -1):
            print(f"\n{Colors.HEADER}{'='*80}")
            print(f"STAGE t={t} | Demand = {self.demand[t]}")
            print(f"{'='*80}{Colors.END}")
            
            # --- PRINT TABLE HEADER ---
            # Columns are possible Order Quantities (0 to Max Storage)
            q_cols = range(self.max_storage + 1) 
            
            # Header Row
            header = f"{'State (Inv)':<12} | {'Opt Q*':<8} | {'Min Cost':<10} ||"
            for q in q_cols:
                header += f" Q={q:<3} |"
            print(f"{Colors.BOLD}{header}{Colors.END}")
            print("-" * len(header))

            # --- PROCESS EACH STATE ---
            for I in range(self.max_storage + 1):
                best_cost = float('inf')
                best_q = -1
                row_values = [] # Store text for printing later
                
                # Check every possible Q for this row
                for q in q_cols:
                    cost, feasible = self._calc_total_cost(I, q, t)
                    
                    if feasible:
                        if cost < best_cost:
                            best_cost = cost
                            best_q = q
                        row_values.append(cost)
                    else:
                        row_values.append(None) # Marker for infeasible
                
                # Save DP Result
                self.dp[t, I] = best_cost
                self.decision[t, I] = best_q

                # --- PRINT ROW ---
                # 1. Left Side (Summary)
                row_str = f"{Colors.BLUE}{I:<12}{Colors.END} | {Colors.GREEN}{best_q:<8}{Colors.END} | {Colors.BOLD}{best_cost:<10.0f}{Colors.END} ||"
                
                # 2. Right Side (The Search Matrix)
                for i, q in enumerate(q_cols):
                    val = row_values[i]
                    if val is None:
                        # Infeasible (X)
                        row_str += f" {Colors.FAIL}  X  {Colors.END} |"
                    elif q == best_q:
                        # The Winner (Green)
                        row_str += f" {Colors.GREEN}{val:>5.0f}{Colors.END} |"
                    else:
                        # Suboptimal (Gray)
                        row_str += f" {Colors.GRAY}{val:>5.0f}{Colors.END} |"
                
                print(row_str)

# ==========================================
# RUNNER
# ==========================================
if __name__ == "__main__":
    # SETUP with SMALL NUMBERS for visual clarity
    verifier = ClassicDPVerifier(
        T=3,                 # Periods 0, 1, 2
        demand=[3, 2, 5],    # Small demand
        max_storage=5,       # Small capacity (Fits in terminal width)
        initial_inventory=1, 
        c_order_fixed=50,
        c_unit=5,
        c_storage=2,
        c_emergency_fixed=80,
        c_emergency_unit=10
    )

    verifier.solve()
    
    print("\n" + "="*50)
    print("FINAL SOLUTION")
    print("="*50)
    print(f"Start Inventory: {verifier.initial_inventory}")
    print(f"Optimal First Order: {verifier.decision[0, verifier.initial_inventory]}")
    print(f"Total Expected Cost: ${verifier.dp[0, verifier.initial_inventory]:.2f}")