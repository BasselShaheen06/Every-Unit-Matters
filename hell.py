import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

# ===================== MODEL PARAMETERS =====================
T = 12

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
        self.dp[self.T, :] = 0

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

# ===================== TKINTER GUI =====================
class InventoryGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Medical Inventory Optimization (DP)")
        self.geometry("1200x850")

        self.current_demand = None
        self.current_schedule = None
        self.current_cost = None
        self.solver = None

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.dp_viz_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="Main Optimization")
        self.notebook.add(self.dp_viz_tab, text="DP Table Visualization")

        self._build_main_tab()
        self._build_dp_viz_tab()

    # ---------- MAIN TAB ----------
    def _build_main_tab(self):
        self._build_inputs(self.main_tab)
        self._build_table(self.main_tab)
        self._build_log(self.main_tab)
        self._build_plots(self.main_tab)

    # ---------- INPUTS ----------
    def _build_inputs(self, parent):
        frame = ttk.LabelFrame(parent, text="Inputs")
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

        ttk.Label(frame, text="Max Storage Capacity:").grid(row=8, column=0, sticky="w")
        self.max_storage = ttk.Entry(frame, width=10)
        self.max_storage.insert(0, "500")
        self.max_storage.grid(row=8, column=1, sticky="w")

        ttk.Label(frame, text="Demand (12 months):").grid(row=0, column=0, sticky="w")
        self.demand_entry = ttk.Entry(frame, width=80)
        self.demand_entry.insert(0, "710,500,200,400,900,800,200,20,394,1000,700,122")
        self.demand_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Initial Inventory:").grid(row=1, column=0, sticky="w")
        self.init_inv = ttk.Entry(frame, width=10)
        self.init_inv.insert(0, "50")
        self.init_inv.grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Run Optimization", command=self.run_solver)\
            .grid(row=2, column=1, sticky="w", pady=5)

    # ---------- TABLE ----------
    def _build_table(self, parent):
        frame = ttk.LabelFrame(parent, text="Optimal Schedule")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ["Period", "Start", "Order", "Demand", "Emergency", "End", "Cost"]
        self.table = ttk.Treeview(frame, columns=cols, show="headings")

        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, anchor="center")

        self.table.pack(fill="both", expand=True)

    # ---------- SUMMARY ----------
    def _build_log(self, parent):
        frame = ttk.LabelFrame(parent, text="Summary")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log = ScrolledText(frame, height=7)
        self.log.pack(fill="both", expand=True)

    # ---------- PLOTS ----------
    def _build_plots(self, parent):
        frame = ttk.LabelFrame(parent, text="Visualizations")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Plot Demand", command=self.plot_demand).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Inventory", command=self.plot_inventory).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Emergencies", command=self.plot_emergency).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Costs", command=self.plot_costs).pack(side="left", padx=5)
        ttk.Button(frame, text="Show Backtracking", command=self.show_backtracking).pack(side="left", padx=5)

    # ---------- DP VISUALIZATION TAB ----------
    def _build_dp_viz_tab(self):
        # DP Table display
        table_frame = ttk.LabelFrame(self.dp_viz_tab, text="DP Table (Cost-to-Go Values)")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview for DP table
        self.dp_tree = ttk.Treeview(table_frame, show="headings")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.dp_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.dp_tree.xview)
        self.dp_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.dp_tree.pack(fill="both", expand=True)
        
        # Decision table display
        decision_frame = ttk.LabelFrame(self.dp_viz_tab, text="Decision Table (Optimal Order Quantities)")
        decision_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.decision_tree = ttk.Treeview(decision_frame, show="headings")
        
        # Add scrollbars
        vsb2 = ttk.Scrollbar(decision_frame, orient="vertical", command=self.decision_tree.yview)
        hsb2 = ttk.Scrollbar(decision_frame, orient="horizontal", command=self.decision_tree.xview)
        self.decision_tree.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)
        
        vsb2.pack(side="right", fill="y")
        hsb2.pack(side="bottom", fill="x")
        self.decision_tree.pack(fill="both", expand=True)

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

        solver.solve()
        schedule, cost = solver.backtrack()

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

        # Update DP table display
        self.display_dp_tables()

    # ---------- DP TABLE DISPLAY FUNCTIONS ----------
    def display_dp_tables(self):
        if self.solver is None or self.solver.dp is None:
            return
        
        # Display DP cost table
        dp = self.solver.dp[:-1]  # Exclude terminal period
        
        # Setup columns
        columns = ["t \\ I"] + [str(i) for i in range(dp.shape[1])]
        self.dp_tree["columns"] = columns
        
        for c in columns:
            self.dp_tree.heading(c, text=c)
            self.dp_tree.column(c, width=80, anchor="center")
        
        # Clear existing data
        for item in self.dp_tree.get_children():
            self.dp_tree.delete(item)
        
        # Fill DP table
        for t in range(dp.shape[0]):
            row = [f"t={t}"]
            for i in range(dp.shape[1]):
                val = dp[t, i]
                if np.isinf(val):
                    row.append("inf")
                else:
                    row.append(f"{val:.1f}")
            self.dp_tree.insert("", "end", values=row)
        
        # Display Decision table
        decision = self.solver.decision
        
        # Setup columns
        columns = ["t \\ I"] + [str(i) for i in range(decision.shape[1])]
        self.decision_tree["columns"] = columns
        
        for c in columns:
            self.decision_tree.heading(c, text=c)
            self.decision_tree.column(c, width=80, anchor="center")
        
        # Clear existing data
        for item in self.decision_tree.get_children():
            self.decision_tree.delete(item)
        
        # Fill Decision table
        for t in range(decision.shape[0]):
            row = [f"t={t}"]
            for i in range(decision.shape[1]):
                row.append(f"{int(decision[t, i])}")
            self.decision_tree.insert("", "end", values=row)

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