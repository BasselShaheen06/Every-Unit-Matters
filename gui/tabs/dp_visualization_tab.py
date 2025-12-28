import tkinter as tk
from tkinter import ttk
import numpy as np

class DPVisualizationTab:
    """DP table visualization tab."""
    
    def __init__(self, parent, parent_gui):
        self.parent = parent
        self.gui = parent_gui
        self.frame = ttk.Frame(parent)
        self.build_tab()
    
    def build_tab(self):
        """Build tab components."""
        self.build_dp_table()
        self.build_decision_table()
    
    def build_dp_table(self):
        """Create DP cost table."""
        table_frame = ttk.LabelFrame(self.frame, text="DP Table (Cost-to-Go Values)")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.gui.dp_tree = ttk.Treeview(table_frame, show="headings")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", 
                           command=self.gui.dp_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", 
                           command=self.gui.dp_tree.xview)
        self.gui.dp_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.gui.dp_tree.pack(fill="both", expand=True)
    
    def build_decision_table(self):
        """Create decision table."""
        decision_frame = ttk.LabelFrame(self.frame, 
                                       text="Decision Table (Optimal Order Quantities)")
        decision_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.gui.decision_tree = ttk.Treeview(decision_frame, show="headings")
        
        vsb2 = ttk.Scrollbar(decision_frame, orient="vertical", 
                            command=self.gui.decision_tree.yview)
        hsb2 = ttk.Scrollbar(decision_frame, orient="horizontal", 
                            command=self.gui.decision_tree.xview)
        self.gui.decision_tree.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)
        
        vsb2.pack(side="right", fill="y")
        hsb2.pack(side="bottom", fill="x")
        self.gui.decision_tree.pack(fill="both", expand=True)
    
    def display_tables(self, solver):
        """Display DP tables."""
        if solver is None or solver.dp is None:
            return
        
        self.display_dp_table(solver.dp)
        self.display_decision_table(solver.decision)
    
    def display_dp_table(self, dp):
        """Display DP cost table."""
        dp_display = dp[:-1]
        
        columns = ["t \\ I"] + [str(i) for i in range(dp_display.shape[1])]
        self.gui.dp_tree["columns"] = columns
        
        for c in columns:
            self.gui.dp_tree.heading(c, text=c)
            self.gui.dp_tree.column(c, width=80, anchor="center")
        
        for item in self.gui.dp_tree.get_children():
            self.gui.dp_tree.delete(item)
        
        for t in range(dp_display.shape[0]):
            row = [f"t={t}"]
            for i in range(dp_display.shape[1]):
                val = dp_display[t, i]
                if np.isinf(val):
                    row.append("inf")
                else:
                    row.append(f"{val:.1f}")
            self.gui.dp_tree.insert("", "end", values=row)
    
    def display_decision_table(self, decision):
        """Display decision table."""
        columns = ["t \\ I"] + [str(i) for i in range(decision.shape[1])]
        self.gui.decision_tree["columns"] = columns
        
        for c in columns:
            self.gui.decision_tree.heading(c, text=c)
            self.gui.decision_tree.column(c, width=80, anchor="center")
        
        for item in self.gui.decision_tree.get_children():
            self.gui.decision_tree.delete(item)
        
        for t in range(decision.shape[0]):
            row = [f"t={t}"]
            for i in range(decision.shape[1]):
                row.append(f"{int(decision[t, i])}")
            self.gui.decision_tree.insert("", "end", values=row)
    
    def get_frame(self):
        return self.frame