import tkinter as tk
from tkinter import ttk
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

class MainTab:
    """Main optimization tab."""
    
    def __init__(self, parent, parent_gui):
        self.parent = parent
        self.gui = parent_gui
        self.frame = ttk.Frame(parent)
        self.build_tab()
    
    def build_tab(self):
        """Build tab components."""
        self.build_inputs()
        self.build_table()
        self.build_log()
        self.build_plots()
    
    def build_inputs(self):
        """Create input fields."""
        frame = ttk.LabelFrame(self.frame, text="Inputs")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Demand (12 months):").grid(row=0, column=0, sticky="w")
        self.gui.demand_entry = ttk.Entry(frame, width=80)
        self.gui.demand_entry.insert(0, DEFAULT_DEMAND)
        self.gui.demand_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Initial Inventory:").grid(row=1, column=0, sticky="w")
        self.gui.init_inv = ttk.Entry(frame, width=10)
        self.gui.init_inv.insert(0, str(DEFAULT_INITIAL_INVENTORY))
        self.gui.init_inv.grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Run Optimization", command=self.gui.run_solver)\
            .grid(row=2, column=1, sticky="w", pady=5)

        ttk.Label(frame, text="Ordering Fixed Cost:").grid(row=3, column=0, sticky="w")
        self.gui.c_order_fixed = ttk.Entry(frame, width=10)
        self.gui.c_order_fixed.insert(0, str(DEFAULT_ORDER_FIXED))
        self.gui.c_order_fixed.grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Ordering Unit Cost:").grid(row=4, column=0, sticky="w")
        self.gui.c_unit = ttk.Entry(frame, width=10)
        self.gui.c_unit.insert(0, str(DEFAULT_UNIT_COST))
        self.gui.c_unit.grid(row=4, column=1, sticky="w")

        ttk.Label(frame, text="Storage Cost / Unit:").grid(row=5, column=0, sticky="w")
        self.gui.c_storage = ttk.Entry(frame, width=10)
        self.gui.c_storage.insert(0, str(DEFAULT_STORAGE_COST))
        self.gui.c_storage.grid(row=5, column=1, sticky="w")

        ttk.Label(frame, text="Emergency Fixed Cost:").grid(row=6, column=0, sticky="w")
        self.gui.c_emergency_fixed = ttk.Entry(frame, width=10)
        self.gui.c_emergency_fixed.insert(0, str(DEFAULT_EMERGENCY_FIXED))
        self.gui.c_emergency_fixed.grid(row=6, column=1, sticky="w")

        ttk.Label(frame, text="Emergency Unit Cost:").grid(row=7, column=0, sticky="w")
        self.gui.c_emergency_unit = ttk.Entry(frame, width=10)
        self.gui.c_emergency_unit.insert(0, str(DEFAULT_EMERGENCY_UNIT))
        self.gui.c_emergency_unit.grid(row=7, column=1, sticky="w")

        ttk.Label(frame, text="Max Storage Capacity:").grid(row=8, column=0, sticky="w")
        self.gui.max_storage = ttk.Entry(frame, width=10)
        self.gui.max_storage.insert(0, str(DEFAULT_MAX_STORAGE))
        self.gui.max_storage.grid(row=8, column=1, sticky="w")
    
    def build_table(self):
        """Create results table."""
        frame = ttk.LabelFrame(self.frame, text="Optimal Schedule")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.gui.table = ttk.Treeview(frame, columns=SCHEDULE_COLUMNS, show="headings")

        for c in SCHEDULE_COLUMNS:
            self.gui.table.heading(c, text=c)
            self.gui.table.column(c, anchor="center")

        self.gui.table.pack(fill="both", expand=True)
    
    def build_log(self):
        """Create summary section."""
        frame = ttk.LabelFrame(self.frame, text="Summary")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.gui.log = ScrolledText(frame, height=7)
        self.gui.log.pack(fill="both", expand=True)
    
    def build_plots(self):
        """Create plot buttons."""
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