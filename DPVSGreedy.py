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

    def solve_greedy(self):
        """Greedy approach: Order exactly the demand each period"""
        schedule = []
        total_cost = 0
        I = self.initial_inventory
        
        for t in range(self.T):
            d = self.demand[t]
            
            # Greedy: order exactly demand (ignore current inventory for simplicity)
            q = d
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
        self.greedy_schedule = None
        self.greedy_cost = None

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.dp_viz_tab = ttk.Frame(self.notebook)
        self.comparison_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="Main Optimization")
        self.notebook.add(self.dp_viz_tab, text="DP Table Visualization")
        self.notebook.add(self.comparison_tab, text="DP vs Greedy Comparison")

        self._build_main_tab()
        self._build_dp_viz_tab()
        self._build_comparison_tab()

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
        self.demand_entry.insert(0, "100,20,100,20,100,20,100,20,100,20,100,20")
        self.demand_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Initial Inventory:").grid(row=1, column=0, sticky="w")
        self.init_inv = ttk.Entry(frame, width=10)
        self.init_inv.insert(0, "0")
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

    # ---------- COMPARISON TAB ----------
    def _build_comparison_tab(self):
        # Summary comparison
        summary_frame = ttk.LabelFrame(self.comparison_tab, text="Cost Comparison Summary")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.comparison_text = ScrolledText(summary_frame, height=8)
        self.comparison_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Side-by-side tables
        tables_frame = ttk.Frame(self.comparison_tab)
        tables_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # DP Schedule
        dp_frame = ttk.LabelFrame(tables_frame, text="Dynamic Programming Schedule")
        dp_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        cols = ["Period", "Order", "Emergency", "Cost"]
        self.dp_comparison_table = ttk.Treeview(dp_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.dp_comparison_table.heading(c, text=c)
            self.dp_comparison_table.column(c, anchor="center", width=100)
        self.dp_comparison_table.pack(fill="both", expand=True)
        
        # Greedy Schedule
        greedy_frame = ttk.LabelFrame(tables_frame, text="Greedy Approach Schedule")
        greedy_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.greedy_comparison_table = ttk.Treeview(greedy_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.greedy_comparison_table.heading(c, text=c)
            self.greedy_comparison_table.column(c, anchor="center", width=100)
        self.greedy_comparison_table.pack(fill="both", expand=True)
        
        # Visualization button
        viz_frame = ttk.Frame(self.comparison_tab)
        viz_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(viz_frame, text="Plot Comparison", command=self.plot_comparison).pack()

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

        # Solve with DP
        solver.solve()
        schedule, cost = solver.backtrack()

        # Solve with Greedy
        greedy_schedule, greedy_cost = solver.solve_greedy()

        self.current_demand = demand
        self.current_schedule = schedule
        self.current_cost = cost
        self.solver = solver
        self.greedy_schedule = greedy_schedule
        self.greedy_cost = greedy_cost

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
        
        # Update comparison tab
        self.display_comparison()

    # ---------- COMPARISON DISPLAY ----------
    def display_comparison(self):
        if self.greedy_schedule is None:
            return
        
        # Clear tables
        self.dp_comparison_table.delete(*self.dp_comparison_table.get_children())
        self.greedy_comparison_table.delete(*self.greedy_comparison_table.get_children())
        
        # Fill DP table
        for s in self.current_schedule:
            self.dp_comparison_table.insert("", "end", values=(
                s["Period"], s["Order"], 
                f"🚨 {s['Emergency']}" if s["Emergency"] else "-",
                f"${s['Cost']:.2f}"
            ))
        
        # Fill Greedy table
        for s in self.greedy_schedule:
            self.greedy_comparison_table.insert("", "end", values=(
                s["Period"], s["Order"],
                f"🚨 {s['Emergency']}" if s["Emergency"] else "-",
                f"${s['Cost']:.2f}"
            ))
        
        # Update summary text
        self.comparison_text.delete("1.0", tk.END)
        
        savings = self.greedy_cost - self.current_cost
        improvement = (savings / self.greedy_cost) * 100 if self.greedy_cost > 0 else 0
        
        dp_orders = sum(1 for s in self.current_schedule if s["Order"] > 0)
        greedy_orders = sum(1 for s in self.greedy_schedule if s["Order"] > 0)
        
        dp_emergencies = sum(1 for s in self.current_schedule if s["Emergency"] > 0)
        greedy_emergencies = sum(1 for s in self.greedy_schedule if s["Emergency"] > 0)
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              ALGORITHM COMPARISON RESULTS                    ║
╚══════════════════════════════════════════════════════════════╝

Dynamic Programming (Optimal):
  • Total Cost: ${self.current_cost:,.2f}
  • Number of Orders: {dp_orders}
  • Emergency Orders: {dp_emergencies}

Greedy Approach (Baseline):
  • Total Cost: ${self.greedy_cost:,.2f}
  • Number of Orders: {greedy_orders}
  • Emergency Orders: {greedy_emergencies}

Performance Improvement:
  • Cost Savings: ${savings:,.2f}
  • Percentage Improvement: {improvement:.2f}%
  • Orders Reduced: {greedy_orders - dp_orders}

Conclusion:
  {"✅ DP significantly outperforms Greedy!" if improvement > 5 else "✅ DP finds optimal solution."}
  {"  DP consolidates orders to minimize fixed costs." if dp_orders < greedy_orders else ""}
"""
        self.comparison_text.insert("1.0", summary)

    def plot_comparison(self):
        if self.greedy_schedule is None:
            messagebox.showwarning("No Data", "Please run optimization first.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        periods = list(range(T))
        
        # Plot 1: Cost per period
        dp_costs = [s["Cost"] for s in self.current_schedule]
        greedy_costs = [s["Cost"] for s in self.greedy_schedule]
        
        ax1.plot(periods, dp_costs, 'o-', label='DP', linewidth=2, markersize=8)
        ax1.plot(periods, greedy_costs, 's--', label='Greedy', linewidth=2, markersize=8)
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Cost ($)')
        ax1.set_title('Cost Per Period Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cumulative cost
        dp_cumulative = np.cumsum(dp_costs)
        greedy_cumulative = np.cumsum(greedy_costs)
        
        ax2.plot(periods, dp_cumulative, 'o-', label='DP', linewidth=2, markersize=8)
        ax2.plot(periods, greedy_cumulative, 's--', label='Greedy', linewidth=2, markersize=8)
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Cumulative Cost ($)')
        ax2.set_title('Cumulative Cost Comparison')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Orders per period
        dp_orders = [s["Order"] for s in self.current_schedule]
        greedy_orders = [s["Order"] for s in self.greedy_schedule]
        
        x = np.arange(len(periods))
        width = 0.35
        
        ax3.bar(x - width/2, dp_orders, width, label='DP', alpha=0.8)
        ax3.bar(x + width/2, greedy_orders, width, label='Greedy', alpha=0.8)
        ax3.set_xlabel('Period')
        ax3.set_ylabel('Order Quantity')
        ax3.set_title('Order Quantities Comparison')
        ax3.set_xticks(x)
        ax3.set_xticklabels(periods)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Summary bar chart
        metrics = ['Total Cost', 'Num Orders', 'Emergencies']
        dp_metrics = [
            self.current_cost / 100,  # Scale for visibility
            sum(1 for s in self.current_schedule if s["Order"] > 0),
            sum(1 for s in self.current_schedule if s["Emergency"] > 0)
        ]
        greedy_metrics = [
            self.greedy_cost / 100,
            sum(1 for s in self.greedy_schedule if s["Order"] > 0),
            sum(1 for s in self.greedy_schedule if s["Emergency"] > 0)
        ]
        
        x = np.arange(len(metrics))
        ax4.bar(x - width/2, dp_metrics, width, label='DP', alpha=0.8)
        ax4.bar(x + width/2, greedy_metrics, width, label='Greedy', alpha=0.8)
        ax4.set_ylabel('Value')
        ax4.set_title('Overall Metrics Comparison')
        ax4.set_xticks(x)
        ax4.set_xticklabels(metrics)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()

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