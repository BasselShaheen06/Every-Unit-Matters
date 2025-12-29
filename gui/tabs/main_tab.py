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
    SCHEDULE_COLUMNS
)

# Explicitly restoring T to 12 as requested
T = 12

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
        """
        Builds input fields matching the layout of the reference code:
        Demand -> Init Inv -> Button -> Costs -> Max Storage
        """
        frame = ttk.LabelFrame(self.frame, text="Inputs")
        frame.pack(fill="x", padx=10, pady=5)

        # --- Row 0: Demand ---
        ttk.Label(frame, text=f"Demand ({T} months):").grid(row=0, column=0, sticky="w")
        self.gui.demand_entry = ttk.Entry(frame, width=80)
        self.gui.demand_entry.insert(0, DEFAULT_DEMAND)
        self.gui.demand_entry.grid(row=0, column=1, padx=5, sticky="w")

        # --- Row 1: Initial Inventory ---
        ttk.Label(frame, text="Initial Inventory:").grid(row=1, column=0, sticky="w")
        self.gui.init_inv = ttk.Entry(frame, width=10)
        self.gui.init_inv.insert(0, str(DEFAULT_INITIAL_INVENTORY))
        self.gui.init_inv.grid(row=1, column=1, sticky="w")

        # --- Row 2: Run Button ---
        ttk.Button(frame, text="Run Optimization", command=self.validate_and_run)\
            .grid(row=2, column=1, sticky="w", pady=5)

        # --- Row 3: Ordering Fixed Cost ---
        ttk.Label(frame, text="Ordering Fixed Cost:").grid(row=3, column=0, sticky="w")
        self.gui.c_order_fixed = ttk.Entry(frame, width=10)
        self.gui.c_order_fixed.insert(0, str(DEFAULT_ORDER_FIXED))
        self.gui.c_order_fixed.grid(row=3, column=1, sticky="w")

        # --- Row 4: Ordering Unit Cost ---
        ttk.Label(frame, text="Ordering Unit Cost:").grid(row=4, column=0, sticky="w")
        self.gui.c_unit = ttk.Entry(frame, width=10)
        self.gui.c_unit.insert(0, str(DEFAULT_UNIT_COST))
        self.gui.c_unit.grid(row=4, column=1, sticky="w")

        # --- Row 5: Storage Cost ---
        ttk.Label(frame, text="Storage Cost / Unit:").grid(row=5, column=0, sticky="w")
        self.gui.c_storage = ttk.Entry(frame, width=10)
        self.gui.c_storage.insert(0, str(DEFAULT_STORAGE_COST))
        self.gui.c_storage.grid(row=5, column=1, sticky="w")

        # --- Row 6: Emergency Fixed Cost ---
        ttk.Label(frame, text="Emergency Fixed Cost:").grid(row=6, column=0, sticky="w")
        self.gui.c_emergency_fixed = ttk.Entry(frame, width=10)
        self.gui.c_emergency_fixed.insert(0, str(DEFAULT_EMERGENCY_FIXED))
        self.gui.c_emergency_fixed.grid(row=6, column=1, sticky="w")

        # --- Row 7: Emergency Unit Cost ---
        ttk.Label(frame, text="Emergency Unit Cost:").grid(row=7, column=0, sticky="w")
        self.gui.c_emergency_unit = ttk.Entry(frame, width=10)
        self.gui.c_emergency_unit.insert(0, str(DEFAULT_EMERGENCY_UNIT))
        self.gui.c_emergency_unit.grid(row=7, column=1, sticky="w")

        # --- Row 8: Max Storage Capacity ---
        ttk.Label(frame, text="Max Storage Capacity:").grid(row=8, column=0, sticky="w")
        self.gui.max_storage = ttk.Entry(frame, width=10)
        self.gui.max_storage.insert(0, str(DEFAULT_MAX_STORAGE))
        self.gui.max_storage.grid(row=8, column=1, sticky="w")
    
    def validate_and_run(self):
        """
        Validates inputs matching the logic from the reference code.
        Strictly enforces that demand length is T (12) and values are non-negative.
        """
        try:
            # 1. Parse Demand
            try:
                raw_text = self.gui.demand_entry.get().split(',')
                # Filter out empty strings from trailing commas
                demands = [int(x.strip()) for x in raw_text if x.strip()]
            except ValueError:
                raise ValueError("Demand must be a comma-separated list of integers.")

            # 2. Strict Check: Demand length must be exactly T (12)
            if len(demands) != T:
                raise ValueError(f"Demand must have exactly {T} values (you provided {len(demands)}).")

            # 3. Strict Check: Negative Demand
            if any(d < 0 for d in demands):
                raise ValueError("Demand values cannot be negative.")

            # 4. Validate Initial Inventory
            try:
                inv = int(self.gui.init_inv.get())
                if inv < 0:
                     raise ValueError("Initial Inventory cannot be negative.")
            except ValueError:
                raise ValueError("Initial Inventory must be a valid integer.")

            # 5. Validate Costs (Floats) and Max Storage (Int)
            inputs_to_check = [
                (self.gui.c_order_fixed, "Ordering Fixed Cost", float),
                (self.gui.c_unit, "Ordering Unit Cost", float),
                (self.gui.c_storage, "Storage Cost", float),
                (self.gui.c_emergency_fixed, "Emergency Fixed Cost", float),
                (self.gui.c_emergency_unit, "Emergency Unit Cost", float),
                (self.gui.max_storage, "Max Storage Capacity", int)
            ]

            for entry, name, type_func in inputs_to_check:
                try:
                    val = type_func(entry.get())
                    if val < 0:
                        raise ValueError(f"{name} cannot be negative.")
                except ValueError:
                    raise ValueError(f"{name} must be a valid number.")

            # ------------------------------------
            # Validation Passed
            # Pass T=12 into the main GUI context for the solver to use
            # ------------------------------------
            self.gui.current_t = T
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