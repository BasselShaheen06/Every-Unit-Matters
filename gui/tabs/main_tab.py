import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from Utils.constant import (
    DEFAULT_DEMAND, 
    DEFAULT_INITIAL_INVENTORY,
    DEFAULT_ORDER_FIXED,
    DEFAULT_UNIT_COST,
    DEFAULT_STORAGE_COST,
    DEFAULT_EMERGENCY_FIXED,
    DEFAULT_EMERGENCY_UNIT,
    DEFAULT_MAX_STORAGE,
    SCHEDULE_COLUMNS,
    T as DEFAULT_T
)

class MainTab:
    """Main optimization tab."""
    
    def __init__(self, parent, parent_gui):
        self.parent = parent
        self.gui = parent_gui
        self.frame = ttk.Frame(parent)
        self.build_tab()
    
    def build_tab(self):
        self.build_inputs()
        self.build_table()
        self.build_log()
        self.build_plots()
    
    def build_inputs(self):
        frame = ttk.LabelFrame(self.frame, text="Inputs")
        frame.pack(fill="x", padx=10, pady=5)

        # Time Horizon T
        ttk.Label(frame, text="Time Horizon (T):").grid(row=0, column=0, sticky="w")
        self.gui.t_entry = ttk.Entry(frame, width=10)
        self.gui.t_entry.insert(0, str(DEFAULT_T))
        self.gui.t_entry.grid(row=0, column=1, sticky="w")

        # Demand
        ttk.Label(frame, text="Demand Sequence:").grid(row=1, column=0, sticky="w")
        self.gui.demand_entry = ttk.Entry(frame, width=80)
        self.gui.demand_entry.insert(0, DEFAULT_DEMAND)
        self.gui.demand_entry.grid(row=1, column=1, padx=5)

        # Initial Inventory
        ttk.Label(frame, text="Initial Inventory:").grid(row=2, column=0, sticky="w")
        self.gui.init_inv = ttk.Entry(frame, width=10)
        self.gui.init_inv.insert(0, str(DEFAULT_INITIAL_INVENTORY))
        self.gui.init_inv.grid(row=2, column=1, sticky="w")

        # Run Button (CHANGED command to validate_and_run)
        ttk.Button(frame, text="Run Optimization", command=self.validate_and_run)\
            .grid(row=3, column=1, sticky="w", pady=5)

        # Costs
        ttk.Label(frame, text="Ordering Fixed Cost:").grid(row=4, column=0, sticky="w")
        self.gui.c_order_fixed = ttk.Entry(frame, width=10)
        self.gui.c_order_fixed.insert(0, str(DEFAULT_ORDER_FIXED))
        self.gui.c_order_fixed.grid(row=4, column=1, sticky="w")

        ttk.Label(frame, text="Ordering Unit Cost:").grid(row=5, column=0, sticky="w")
        self.gui.c_unit = ttk.Entry(frame, width=10)
        self.gui.c_unit.insert(0, str(DEFAULT_UNIT_COST))
        self.gui.c_unit.grid(row=5, column=1, sticky="w")

        ttk.Label(frame, text="Storage Cost / Unit:").grid(row=6, column=0, sticky="w")
        self.gui.c_storage = ttk.Entry(frame, width=10)
        self.gui.c_storage.insert(0, str(DEFAULT_STORAGE_COST))
        self.gui.c_storage.grid(row=6, column=1, sticky="w")

        ttk.Label(frame, text="Emergency Fixed Cost:").grid(row=7, column=0, sticky="w")
        self.gui.c_emergency_fixed = ttk.Entry(frame, width=10)
        self.gui.c_emergency_fixed.insert(0, str(DEFAULT_EMERGENCY_FIXED))
        self.gui.c_emergency_fixed.grid(row=7, column=1, sticky="w")

        ttk.Label(frame, text="Emergency Unit Cost:").grid(row=8, column=0, sticky="w")
        self.gui.c_emergency_unit = ttk.Entry(frame, width=10)
        self.gui.c_emergency_unit.insert(0, str(DEFAULT_EMERGENCY_UNIT))
        self.gui.c_emergency_unit.grid(row=8, column=1, sticky="w")

        ttk.Label(frame, text="Max Storage Capacity:").grid(row=9, column=0, sticky="w")
        self.gui.max_storage = ttk.Entry(frame, width=10)
        self.gui.max_storage.insert(0, str(DEFAULT_MAX_STORAGE))
        self.gui.max_storage.grid(row=9, column=1, sticky="w")
    
    def validate_and_run(self):
        """Validates all inputs before running the solver."""
        try:
            # 1. Validate Time Horizon (Positive Integer)
            try:
                t_val = int(self.gui.t_entry.get())
                if t_val <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Time Horizon (T) must be a positive integer.")

            # 2. Validate Demand (List of Non-Negative Integers)
            try:
                demands = [int(x.strip()) for x in self.gui.demand_entry.get().split(',')]
                if any(d < 0 for d in demands):
                    raise ValueError("Demand values cannot be negative.")
                
                if len(demands) != t_val:
                    raise ValueError(f"Demand count ({len(demands)}) does not match Time Horizon T ({t_val}).")
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError("Demand must be a comma-separated list of integers.")
                raise e

            # 3. Validate Initial Inventory (Integer, Negative Allowed)
            try:
                int(self.gui.init_inv.get())
            except ValueError:
                raise ValueError("Initial Inventory must be an integer.")

            # 4. Validate Costs (Non-Negative Floats)
            cost_inputs = [
                (self.gui.c_order_fixed, "Ordering Fixed Cost"),
                (self.gui.c_unit, "Ordering Unit Cost"),
                (self.gui.c_storage, "Storage Cost"),
                (self.gui.c_emergency_fixed, "Emergency Fixed Cost"),
                (self.gui.c_emergency_unit, "Emergency Unit Cost")
            ]

            for entry, name in cost_inputs:
                try:
                    val = float(entry.get())
                    if val < 0:
                        raise ValueError(f"{name} cannot be negative.")
                except ValueError:
                    raise ValueError(f"{name} must be a valid number.")

            # 5. Validate Max Storage (Positive Integer)
            try:
                ms = int(self.gui.max_storage.get())
                if ms <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Max Storage Capacity must be a positive integer.")

            # If all validations pass, run the solver
            self.gui.run_solver()

        except ValueError as ve:
            messagebox.showerror("Input Validation Error", str(ve))

    def build_table(self):
        frame = ttk.LabelFrame(self.frame, text="Optimal Schedule")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.gui.table = ttk.Treeview(frame, columns=SCHEDULE_COLUMNS, show="headings")

        for c in SCHEDULE_COLUMNS:
            self.gui.table.heading(c, text=c)
            self.gui.table.column(c, anchor="center")

        self.gui.table.pack(fill="both", expand=True)
    
    def build_log(self):
        frame = ttk.LabelFrame(self.frame, text="Summary")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.gui.log = ScrolledText(frame, height=7)
        self.gui.log.pack(fill="both", expand=True)
    
    def build_plots(self):
        frame = ttk.LabelFrame(self.frame, text="Visualizations")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Plot Demand", 
                  command=self.gui.plot_manager.plot_demand).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Inventory", 
                  command=self.gui.plot_manager.plot_inventory).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Emergencies", 
                  command=self.gui.plot_manager.plot_emergency).pack(side="left", padx=5)
        ttk.Button(frame, text="Plot Costs", 
                  command=self.gui.plot_manager.plot_costs).pack(side="left", padx=5)
        ttk.Button(frame, text="Show Backtracking", 
                  command=self.gui.plot_manager.show_backtracking).pack(side="left", padx=5)
    
    def get_frame(self):
        return self.frame