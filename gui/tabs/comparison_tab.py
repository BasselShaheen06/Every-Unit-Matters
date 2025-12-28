import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from Utils.constant import COMPARISON_COLUMNS, TABLE_HEIGHT

class ComparisonTab:
    """DP vs Greedy comparison tab."""
    
    def __init__(self, parent, parent_gui):
        self.parent = parent
        self.gui = parent_gui
        self.frame = ttk.Frame(parent)
        self.build_tab()
    
    def build_tab(self):
        """Build tab components."""
        self.build_summary()
        self.build_tables()
        self.build_visualization()
    
    def build_summary(self):
        """Create summary section."""
        summary_frame = ttk.LabelFrame(self.frame, text="Cost Comparison Summary")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.gui.comparison_text = ScrolledText(summary_frame, height=8)
        self.gui.comparison_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def build_tables(self):
        """Create comparison tables."""
        tables_frame = ttk.Frame(self.frame)
        tables_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # DP Schedule
        dp_frame = ttk.LabelFrame(tables_frame, text="Dynamic Programming Schedule")
        dp_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.gui.dp_comparison_table = ttk.Treeview(
            dp_frame, columns=COMPARISON_COLUMNS, 
            show="headings", height=TABLE_HEIGHT
        )
        
        for c in COMPARISON_COLUMNS:
            self.gui.dp_comparison_table.heading(c, text=c)
            self.gui.dp_comparison_table.column(c, anchor="center", width=100)
        
        self.gui.dp_comparison_table.pack(fill="both", expand=True)
        
        # Greedy Schedule
        greedy_frame = ttk.LabelFrame(tables_frame, text="Greedy Approach Schedule")
        greedy_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.gui.greedy_comparison_table = ttk.Treeview(
            greedy_frame, columns=COMPARISON_COLUMNS, 
            show="headings", height=TABLE_HEIGHT
        )
        
        for c in COMPARISON_COLUMNS:
            self.gui.greedy_comparison_table.heading(c, text=c)
            self.gui.greedy_comparison_table.column(c, anchor="center", width=100)
        
        self.gui.greedy_comparison_table.pack(fill="both", expand=True)
    
    def build_visualization(self):
        """Create plot button."""
        viz_frame = ttk.Frame(self.frame)
        viz_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(viz_frame, text="Plot Comparison", 
                  command=self.gui.plot_manager.plot_comparison).pack()
    
    def display_comparison(self, dp_schedule, dp_cost, greedy_schedule, greedy_cost):
        """Update comparison display."""
        # Clear tables
        self.gui.dp_comparison_table.delete(*self.gui.dp_comparison_table.get_children())
        self.gui.greedy_comparison_table.delete(
            *self.gui.greedy_comparison_table.get_children()
        )
        
        # Fill tables
        for s in dp_schedule:
            self.gui.dp_comparison_table.insert("", "end", values=(
                s["Period"], s["Order"], 
                f"🚨 {s['Emergency']}" if s["Emergency"] else "-",
                f"${s['Cost']:.2f}"
            ))
        
        for s in greedy_schedule:
            self.gui.greedy_comparison_table.insert("", "end", values=(
                s["Period"], s["Order"],
                f"🚨 {s['Emergency']}" if s["Emergency"] else "-",
                f"${s['Cost']:.2f}"
            ))
        
        # Update summary
        self._update_summary(dp_schedule, dp_cost, greedy_schedule, greedy_cost)
    
    def _update_summary(self, dp_schedule, dp_cost, greedy_schedule, greedy_cost):
        """Generate summary text."""
        self.gui.comparison_text.delete("1.0", tk.END)
        
        savings = greedy_cost - dp_cost
        improvement = (savings / greedy_cost) * 100 if greedy_cost > 0 else 0
        
        dp_orders = sum(1 for s in dp_schedule if s["Order"] > 0)
        greedy_orders = sum(1 for s in greedy_schedule if s["Order"] > 0)
        
        dp_emergencies = sum(1 for s in dp_schedule if s["Emergency"] > 0)
        greedy_emergencies = sum(1 for s in greedy_schedule if s["Emergency"] > 0)
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              ALGORITHM COMPARISON RESULTS                    ║
╚══════════════════════════════════════════════════════════════╝

Dynamic Programming (Optimal):
  • Total Cost: ${dp_cost:,.2f}
  • Number of Orders: {dp_orders}
  • Emergency Orders: {dp_emergencies}

Greedy Approach (Baseline):
  • Total Cost: ${greedy_cost:,.2f}
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
        self.gui.comparison_text.insert("1.0", summary)
    
    def get_frame(self):
        return self.frame
