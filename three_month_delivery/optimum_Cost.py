import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib.pyplot as plt
import sys
from functools import lru_cache

# ===================== MODEL PARAMETERS =====================
T = 12
LEAD_TIME = 3  # 3-month lead time

class InventoryDPSolver:
    def __init__(self, T, demand, max_storage, initial_inventory,
                 c_order_fixed, c_unit, c_storage,
                 c_emergency_fixed, c_emergency_unit):

        self.T = T
        self.demand = demand
        self.max_storage = max_storage
        self.initial_inventory = initial_inventory

        # cost parameters
        self.c_order_fixed = c_order_fixed
        self.c_unit = c_unit
        self.c_storage = c_storage
        self.c_emergency_fixed = c_emergency_fixed
        self.c_emergency_unit = c_emergency_unit

        # Increase recursion depth just in case, though T=12 is shallow.
        sys.setrecursionlimit(5000)

    def normal_order_cost(self, n):
        return 0 if n == 0 else self.c_order_fixed + self.c_unit * n

    def emergency_order_cost(self, n):
        return 0 if n == 0 else self.c_emergency_fixed + self.c_emergency_unit * n

    def storage_cost(self, n):
        return self.c_storage * n

    def solve(self):
        # Clear cache to ensure fresh run with new parameters
        self._dp.cache_clear()
        
        # Initial State: Time 0, Initial Inv, Pipeline is empty (0,0,0)
        self.min_cost = self._dp(0, self.initial_inventory, 0, 0, 0)

    @lru_cache(maxsize=None)
    def _dp(self, t, current_inv, p1, p2, p3):
        """
        Recursive DP State:
        t: current month (0 to T)
        current_inv: inventory on hand at start of month
        p1: arriving this month (ordered t-3)
        p2: arriving next month (ordered t-2)
        p3: arriving in 2 months (ordered t-1)
        """
        # Base case: End of planning horizon
        if t == self.T:
            return 0

        # 1. Pipeline arrival
        available_stock = current_inv + p1
        
        # 2. Fulfill Demand
        d = self.demand[t]
        
        emergency_qty = 0
        if available_stock >= d:
            ending_inv = available_stock - d
        else:
            # Shortage! Emergency order covers the gap immediately.
            shortage = d - available_stock
            emergency_qty = shortage
            ending_inv = 0  

        # Clamp inventory to max_storage for the state definition
        ending_inv = min(ending_inv, self.max_storage)

        # 3. Calculate Period Costs (Storage + Emergency)
        period_base_cost = (
            self.emergency_order_cost(emergency_qty) + 
            self.storage_cost(ending_inv)
        )

        # 4. Make Decision: Order q (arrives at t+3)
        best_cost = float('inf')
        
        # FIX: Check q <= max_storage to keep state space manageable
        for q in range(self.max_storage + 1):
            order_cost = self.normal_order_cost(q)
            
            # Transition: 
            # p1 becomes p2 (what was arriving next month arrives now)
            # p2 becomes p3
            # p3 becomes q (the new order)
            future_cost = self._dp(t + 1, ending_inv, p2, p3, q)
            
            total_cost = period_base_cost + order_cost + future_cost
            
            if total_cost < best_cost:
                best_cost = total_cost
                
        return best_cost

    def backtrack(self):
        schedule = []
        
        # Start reconstruction
        t = 0
        current_inv = self.initial_inventory
        p1, p2, p3 = 0, 0, 0
        
        total_optimal_cost = 0

        for t in range(self.T):
            available_stock = current_inv + p1
            d = self.demand[t]
            
            emergency_qty = 0
            if available_stock >= d:
                ending_inv = available_stock - d
            else:
                emergency_qty = d - available_stock
                ending_inv = 0
            
            ending_inv = min(ending_inv, self.max_storage)
            
            period_base_cost = (
                self.emergency_order_cost(emergency_qty) + 
                self.storage_cost(ending_inv)
            )

            # Re-evaluate transitions to find the optimal q
            best_q = -1
            
            target_cost = self._dp(t, current_inv, p1, p2, p3)

            for q in range(self.max_storage + 1):
                cost_order = self.normal_order_cost(q)
                future_cost = self._dp(t + 1, ending_inv, p2, p3, q)
                
                # Check for floating point match
                if abs((period_base_cost + cost_order + future_cost) - target_cost) < 1e-7:
                    best_q = q
                    break
            
            period_total_cost = period_base_cost + self.normal_order_cost(best_q)
            
            schedule.append({
                "Period": t,
                "Start": available_stock,
                "Order": best_q,
                "Demand": d,
                "Emergency": emergency_qty,
                "End": ending_inv,
                "Cost": period_total_cost
            })
            
            # Advance State
            current_inv = ending_inv
            p1 = p2
            p2 = p3
            p3 = best_q
            
            total_optimal_cost += period_total_cost

        return schedule, total_optimal_cost

# ===================== TKINTER GUI =====================
class InventoryGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Medical Inventory Optimization (DP - Fixed)")
        self.geometry("1150x780")

        self.current_demand = None
        self.current_schedule = None
        self.current_cost = None
        self.solver = None 

        self._build_inputs()
        self._build_table()
        self._build_log()
        self._build_plots()

    # ---------- INPUTS ----------
    def _build_inputs(self):
        frame = ttk.LabelFrame(self, text="Inputs")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Ordering Fixed Cost:").grid(row=3, column=0, sticky="w")
        self.c_order_fixed = ttk.Entry(frame, width=10)
        self.c_order_fixed.insert(0, "100")
        self.c_order_fixed.grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Ordering Unit Cost:").grid(row=4, column=0, sticky="w")
        self.c_unit = ttk.Entry(frame, width=10)
        self.c_unit.insert(0, "10")
        self.c_unit.grid(row=4, column=1, sticky="w")

        ttk.Label(frame, text="Storage Cost / Unit:").grid(row=5, column=0, sticky="w")
        self.c_storage = ttk.Entry(frame, width=10)
        self.c_storage.insert(0, "2")
        self.c_storage.grid(row=5, column=1, sticky="w")

        ttk.Label(frame, text="Emergency Fixed Cost:").grid(row=6, column=0, sticky="w")
        self.c_emergency_fixed = ttk.Entry(frame, width=10)
        self.c_emergency_fixed.insert(0, "150")
        self.c_emergency_fixed.grid(row=6, column=1, sticky="w")

        ttk.Label(frame, text="Emergency Unit Cost:").grid(row=7, column=0, sticky="w")
        self.c_emergency_unit = ttk.Entry(frame, width=10)
        self.c_emergency_unit.insert(0, "60")
        self.c_emergency_unit.grid(row=7, column=1, sticky="w")

        # FIX: Reduced Max Storage to 30
        ttk.Label(frame, text="Max Storage Capacity:").grid(row=8, column=0, sticky="w")
        self.max_storage = ttk.Entry(frame, width=10)
        self.max_storage.insert(0, "30") 
        self.max_storage.grid(row=8, column=1, sticky="w")

        # FIX: Reduced Demand values to match the capacity of 30
        ttk.Label(frame, text="Demand (12 months):").grid(row=0, column=0, sticky="w")
        self.demand_entry = ttk.Entry(frame, width=80)
        self.demand_entry.insert(0, "15, 12, 35, 20, 10, 40, 15, 10, 10, 25, 15, 10")
        self.demand_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Initial Inventory:").grid(row=1, column=0, sticky="w")
        self.init_inv = ttk.Entry(frame, width=10)
        self.init_inv.insert(0, "10")
        self.init_inv.grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Run Optimization", command=self.run_solver)\
            .grid(row=2, column=1, sticky="w", pady=5)

    # ---------- TABLE ----------
    def _build_table(self):
        frame = ttk.LabelFrame(self, text="Optimal Schedule")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ["Period", "Start", "Order", "Demand", "Emergency", "End", "Cost"]
        self.table = ttk.Treeview(frame, columns=cols, show="headings")

        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, anchor="center")

        self.table.pack(fill="both", expand=True)

    # ---------- SUMMARY ----------
    def _build_log(self):
        frame = ttk.LabelFrame(self, text="Summary")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log = ScrolledText(frame, height=7)
        self.log.pack(fill="both", expand=True)

    # ---------- PLOTS ----------
    def _build_plots(self):
        frame = ttk.LabelFrame(self, text="Visualizations")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Plot Demand", command=self.plot_demand).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Inventory", command=self.plot_inventory).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Emergencies", command=self.plot_emergency).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Costs", command=self.plot_costs).pack(side="left", padx=5)
        ttk.Button(frame, text="Show Backtracking", command=self.show_backtracking).pack(side="left", padx=5)

    # ---------- SOLVER ----------
    def run_solver(self):
        try:
            demand = list(map(int, self.demand_entry.get().split(",")))
            if len(demand) != T:
                raise ValueError("Demand must have 12 values")

            init_inv = int(self.init_inv.get())

            c_order_fixed = float(self.c_order_fixed.get())
            c_unit = float(self.c_unit.get())
            c_storage = float(self.c_storage.get())
            c_emergency_fixed = float(self.c_emergency_fixed.get())
            c_emergency_unit = float(self.c_emergency_unit.get())
            max_storage = int(self.max_storage.get())

        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return

        solver = InventoryDPSolver(
            T, demand, max_storage, init_inv,
            c_order_fixed, c_unit, c_storage,
            c_emergency_fixed, c_emergency_unit
        )

        self.config(cursor="watch")
        self.update()
        
        solver.solve()
        schedule, cost = solver.backtrack()
        
        self.config(cursor="")

        self.current_demand = demand
        self.current_schedule = schedule
        self.current_cost = cost
        self.solver = solver 

        self.table.delete(*self.table.get_children())
        emergency_count = 0

        for s in schedule:
            if s["Emergency"] > 0:
                emergency_count += 1

            self.table.insert("", "end", values=(
                s["Period"], s["Start"], s["Order"],
                s["Demand"],
                f"🚨 {s['Emergency']}" if s["Emergency"] else "-",
                s["End"],
                f"${s['Cost']:.2f}"
            ))

        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, f"Optimal Total Cost: ${cost:,.2f}\n")
        self.log.insert(tk.END, f"Emergency Orders: {emergency_count}\n")
        self.log.insert(tk.END, f"Total Demand: {sum(demand)} units\n")

    # ---------- VISUALIZATION FUNCTIONS ----------
    def _check_data(self):
        if self.current_schedule is None:
            messagebox.showwarning("Run Optimization", "Please run optimization first.")
            return False
        return True

    def plot_demand(self):
        if not self._check_data(): return
        plt.figure()
        plt.plot(self.current_demand, marker="o")
        plt.title("Demand Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()

    def plot_inventory(self):
        if not self._check_data(): return
        inventory = [s["Start"] for s in self.current_schedule]
        inventory.append(self.current_schedule[-1]["End"])
        plt.figure()
        plt.step(range(len(inventory)), inventory, where="post")
        plt.title("Inventory Level Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()

    def plot_emergency(self):
        if not self._check_data(): return
        emergency = [s["Emergency"] for s in self.current_schedule]
        plt.figure()
        plt.bar(range(len(emergency)), emergency)
        plt.title("Emergency Orders Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()

    def plot_costs(self):
        if not self._check_data(): return
        costs = [s["Cost"] for s in self.current_schedule]
        plt.figure()
        plt.plot(costs, marker="o")
        plt.title("Cost Per Period")
        plt.xlabel("Month")
        plt.ylabel("Cost ($)")
        plt.grid(True)
        plt.show()

    def show_backtracking(self):
        if not self._check_data(): return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Top plot: Decision path
        periods = [s["Period"] for s in self.current_schedule]
        inventory_states = [s["Start"] for s in self.current_schedule]
        orders = [s["Order"] for s in self.current_schedule]
        
        ax1.plot(periods, inventory_states, 'o-', linewidth=2, markersize=8, label='Inventory State')
        for i, (p, inv, order) in enumerate(zip(periods, inventory_states, orders)):
            ax1.annotate(f'Order: {order}', 
                        xy=(p, inv), 
                        xytext=(10, 10), 
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Inventory Level')
        ax1.set_title('Backtracking Path: Optimal Decisions')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Bottom plot: Cumulative cost
        cumulative_costs = np.cumsum([s["Cost"] for s in self.current_schedule])
        ax2.plot(periods, cumulative_costs, 's-', linewidth=2, markersize=8, color='red', label='Cumulative Cost')
        ax2.fill_between(periods, cumulative_costs, alpha=0.3, color='red')
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Cumulative Cost ($)')
        ax2.set_title('Cost Accumulation During Backtracking')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()

# ===================== RUN =====================
if __name__ == "__main__":
    app = InventoryGUI()
    app.mainloop()