import numpy as np

# ===================== SIMPLE 3-PERIOD DP =====================

class Simple3PeriodDP:
    def __init__(self, demand, max_storage, initial_inventory,
                 c_order_fixed, c_unit, c_storage,
                 c_emergency_fixed, c_emergency_unit):
        
        self.T = 3  # Fixed at 3 periods
        self.demand = demand
        self.max_storage = max_storage
        self.initial_inventory = initial_inventory
        
        self.c_order_fixed = c_order_fixed
        self.c_unit = c_unit
        self.c_storage = c_storage
        self.c_emergency_fixed = c_emergency_fixed
        self.c_emergency_unit = c_emergency_unit
        
        self.dp = None
        self.decision = None
    
    def normal_order_cost(self, n):
        return 0 if n == 0 else self.c_order_fixed + self.c_unit * n
    
    def emergency_order_cost(self, n):
        return 0 if n == 0 else self.c_emergency_fixed + self.c_emergency_unit * n
    
    def storage_cost(self, n):
        return self.c_storage * n
    
    def solve(self):
        INF = float('inf')
        self.dp = np.full((self.T + 1, self.max_storage + 1), INF)
        self.decision = np.zeros((self.T + 1, self.max_storage + 1), dtype=int)
        
        # Boundary condition: No cost after final period
        self.dp[self.T, :] = 0
        
        print("="*70)
        print("BACKWARD INDUCTION - BUILDING DP TABLE")
        print("="*70)
        
        # Backward induction
        for t in range(self.T - 1, -1, -1):
            print(f"\n--- PERIOD t={t} (Demand = {self.demand[t]}) ---")
            
            for I in range(self.max_storage + 1):
                best_cost = INF
                best_order = 0
                
                print(f"\n  State I={I}:")
                
                # Try all possible orders
                for q in range(self.max_storage - I + 1):
                    cost, next_inv = self._period_cost(I, q, t)
                    total_cost = cost + self.dp[t + 1, next_inv]
                    
                    print(f"    Order q={q}: period_cost=${cost:.2f}, next_inv={next_inv}, future_cost=${self.dp[t+1, next_inv]:.2f}, total=${total_cost:.2f}")
                    
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_order = q
                
                self.dp[t, I] = best_cost
                self.decision[t, I] = best_order
                
                print(f"  ➜ BEST: Order q={best_order}, Total Cost=${best_cost:.2f}")
    
    def _period_cost(self, I, q, t):
        """Calculate cost for this period and return next state"""
        demand = self.demand[t]
        inv_after_order = I + q
        
        # Regular order cost
        cost = self.normal_order_cost(q)
        
        # Check if we can meet demand
        if inv_after_order >= demand:
            # No shortage
            remaining = inv_after_order - demand
            cost += self.storage_cost(remaining)
            emergency = 0
        else:
            # Shortage - need emergency order
            shortage = demand - inv_after_order
            cost += self.emergency_order_cost(shortage)
            remaining = 0
            emergency = shortage
        
        return cost, remaining
    
    def backtrack(self):
        """Trace back optimal decisions"""
        print("\n" + "="*70)
        print("BACKTRACKING - FINDING OPTIMAL SOLUTION")
        print("="*70)
        
        schedule = []
        I = self.initial_inventory
        
        for t in range(self.T):
            q = self.decision[t, I]
            inv_after_order = I + q
            d = self.demand[t]
            
            # Calculate what happens
            if inv_after_order >= d:
                emergency = 0
                end_inv = inv_after_order - d
            else:
                emergency = d - inv_after_order
                end_inv = 0
            
            # Calculate costs
            order_cost = self.normal_order_cost(q)
            emerg_cost = self.emergency_order_cost(emergency)
            store_cost = self.storage_cost(end_inv)
            period_cost = order_cost + emerg_cost + store_cost
            
            schedule.append({
                "Period": t,
                "Start_Inv": I,
                "Order": q,
                "Demand": d,
                "Emergency": emergency,
                "End_Inv": end_inv,
                "Order_Cost": order_cost,
                "Emergency_Cost": emerg_cost,
                "Storage_Cost": store_cost,
                "Total_Cost": period_cost
            })
            
            print(f"\nPeriod {t}:")
            print(f"  Start Inventory: {I}")
            print(f"  Decision: Order {q} units (cost: ${order_cost:.2f})")
            print(f"  Inventory after order: {inv_after_order}")
            print(f"  Demand: {d}")
            if emergency > 0:
                print(f"  🚨 Emergency order: {emergency} units (cost: ${emerg_cost:.2f})")
            print(f"  End Inventory: {end_inv} (storage cost: ${store_cost:.2f})")
            print(f"  Period Total Cost: ${period_cost:.2f}")
            
            I = end_inv
        
        total_cost = self.dp[0, self.initial_inventory]
        
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        print(f"Total Optimal Cost: ${total_cost:.2f}")
        print(f"Verification: Sum of period costs = ${sum(s['Total_Cost'] for s in schedule):.2f}")
        print(f"Match: {'✅ YES' if abs(total_cost - sum(s['Total_Cost'] for s in schedule)) < 0.01 else '❌ NO'}")
        
        return schedule, total_cost
    
    def print_full_dp_table(self):
        """Print complete DP table for manual verification"""
        print("\n" + "="*70)
        print("COMPLETE DP TABLE")
        print("="*70)
        
        for t in range(self.T + 1):
            print(f"\nPeriod t={t}:")
            print("Inventory | Cost-to-Go | Optimal Order")
            print("-" * 45)
            for I in range(self.max_storage + 1):
                if not np.isinf(self.dp[t, I]):
                    print(f"   {I:3d}    |  ${self.dp[t, I]:8.2f}  |      {self.decision[t, I]:3d}")
    
    def print_decision_table(self):
        """Print decision table"""
        print("\n" + "="*70)
        print("DECISION TABLE (Optimal Order Quantity)")
        print("="*70)
        
        for t in range(self.T):
            print(f"\nPeriod t={t} (Demand = {self.demand[t]}):")
            print("Start_Inventory | Optimal_Order")
            print("-" * 35)
            for I in range(self.max_storage + 1):
                print(f"      {I:3d}       |      {self.decision[t, I]:3d}")


# ===================== TEST CASES =====================

def test_tiny_case():
    """Tiny test case for easy manual verification"""
    print("\n" + "#"*70)
    print("# TEST CASE 1: Tiny Problem (Max Capacity = 6)")
    print("#"*70)
    print("\nProblem Setup:")
    print("  Demand: [2, 3, 2]")
    print("  Max Storage: 6")
    print("  Initial Inventory: 0")
    print("  Order Fixed Cost: $10")
    print("  Order Unit Cost: $5")
    print("  Storage Cost per unit: $1")
    print("  Emergency Fixed Cost: $20")
    print("  Emergency Unit Cost: $15")
    print("="*70)
    
    solver = Simple3PeriodDP(
        demand=[2, 3, 2],
        max_storage=6,
        initial_inventory=0,
        c_order_fixed=10,
        c_unit=5,
        c_storage=1,
        c_emergency_fixed=20,
        c_emergency_unit=15
    )
    
    solver.solve()
    schedule, total_cost = solver.backtrack()
    solver.print_full_dp_table()
    solver.print_decision_table()
    
    return solver


def test_constant_demand():
    """Constant demand test case"""
    print("\n" + "#"*70)
    print("# TEST CASE 2: Constant Demand (Max Capacity = 6)")
    print("#"*70)
    print("\nProblem Setup:")
    print("  Demand: [3, 3, 3]")
    print("  Max Storage: 6")
    print("  Initial Inventory: 1")
    print("  Order Fixed Cost: $8")
    print("  Order Unit Cost: $4")
    print("  Storage Cost per unit: $1")
    print("  Emergency Fixed Cost: $25")
    print("  Emergency Unit Cost: $20")
    print("="*70)
    
    solver = Simple3PeriodDP(
        demand=[3, 3, 3],
        max_storage=6,
        initial_inventory=1,
        c_order_fixed=8,
        c_unit=4,
        c_storage=1,
        c_emergency_fixed=25,
        c_emergency_unit=20
    )
    
    solver.solve()
    schedule, total_cost = solver.backtrack()
    solver.print_full_dp_table()
    solver.print_decision_table()
    
    return solver


# ===================== RUN ALL TESTS =====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("3-PERIOD DYNAMIC PROGRAMMING - HAND VERIFICATION VERSION")
    print("="*70)
    
    # Run test case 1
    solver1 = test_tiny_case()
    
    # Run test case 2
    solver2 = test_constant_demand()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)
    print("\n📝 MANUAL VERIFICATION GUIDE:")
    print("="*70)
    print("1. Start at Period t=2 (last period before terminal)")
    print("2. For each inventory state I, try all possible orders q")
    print("3. Calculate: order_cost + storage_cost + emergency_cost + future_cost")
    print("4. Pick the q that gives minimum total cost")
    print("5. Move to Period t=1, repeat")
    print("6. Move to Period t=0, repeat")
    print("7. Trace forward from initial inventory using optimal decisions")
    print("\nWith max_storage=6, there are only 7 states (0-6) per period!")
    print("This makes hand verification very manageable.")