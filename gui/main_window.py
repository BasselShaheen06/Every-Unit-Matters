# gui/main_window.py
"""
Main application window and solver orchestration.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from models.inventory_solver import InventoryDPSolver
from gui.tabs.main_tab import MainTab
from gui.tabs.dp_visualization_tab import DPVisualizationTab
from gui.tabs.comparison_tab import ComparisonTab
from gui.widgets.plot_manager import PlotManager
from Utils.constant import *


class InventoryGUI(tk.Tk):
    """Main GUI application for medical inventory optimization."""
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.title("Medical Inventory Optimization (DP)")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # State variables
        self.current_demand = None
        self.current_schedule = None
        self.current_cost = None
        self.solver = None
        self.greedy_schedule = None
        self.greedy_cost = None

        # Widget references (will be set by tabs)
        self.demand_entry = None
        self.init_inv = None
        self.c_order_fixed = None
        self.c_unit = None
        self.c_storage = None
        self.c_emergency_fixed = None
        self.c_emergency_unit = None
        self.max_storage = None
        self.table = None
        self.log = None
        self.dp_tree = None
        self.decision_tree = None
        self.comparison_text = None
        self.dp_comparison_table = None
        self.greedy_comparison_table = None

        # Initialize plot manager
        self.plot_manager = PlotManager(self)

        # Create notebook and tabs
        self.setup_tabs()
    
    def setup_tabs(self):
        """Create notebook and all tabs."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Create tabs
        self.main_tab = MainTab(self.notebook, self)
        self.dp_viz_tab = DPVisualizationTab(self.notebook, self)
        self.comparison_tab = ComparisonTab(self.notebook, self)
        
        # Add tabs to notebook
        self.notebook.add(self.main_tab.get_frame(), text="Main Optimization")
        self.notebook.add(self.dp_viz_tab.get_frame(), text="DP Table Visualization")
        self.notebook.add(self.comparison_tab.get_frame(), text="DP vs Greedy Comparison")
    
    def run_solver(self):
        """
        Main solver orchestration: parse inputs, solve with DP and Greedy,
        update all displays.
        """
        # Parse and validate inputs
        try:
            demand = list(map(int, self.demand_entry.get().split(",")))
            if len(demand) != T:
                raise ValueError(f"Demand must have {T} values")

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

        # Create solver
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

        # Update state
        self.current_demand = demand
        self.current_schedule = schedule
        self.current_cost = cost
        self.solver = solver
        self.greedy_schedule = greedy_schedule
        self.greedy_cost = greedy_cost

        # Update displays
        self.update_main_table(schedule, cost, demand)
        self.dp_viz_tab.display_tables(solver)
        self.comparison_tab.display_comparison(
            schedule, cost, greedy_schedule, greedy_cost
        )
    
    def update_main_table(self, schedule, cost, demand):
        """Update the main results table and summary."""
        # Clear table
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

        # Update log
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, f"Optimal Total Cost: ${cost:,.2f}\n")
        self.log.insert(tk.END, f"Emergency Orders: {emergency_count}\n")
        self.log.insert(tk.END, f"Total Demand: {sum(demand)} units\n")