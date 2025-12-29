import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from Utils.constant import COMPARISON_COLUMNS, TABLE_HEIGHT

class ComparisonTab:
    """DP vs Greedy comparison tab with differences highlighted."""

    def __init__(self, parent, parent_gui):
        self.parent = parent_gui
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

        self.parent.comparison_text = ScrolledText(summary_frame, height=8)
        self.parent.comparison_text.pack(fill="both", expand=True, padx=5, pady=5)

    def build_tables(self):
        """Create comparison tables for DP, Greedy, and differences."""
        tables_frame = ttk.Frame(self.frame)
        tables_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # DP Schedule
        dp_frame = ttk.LabelFrame(tables_frame, text="Dynamic Programming Schedule")
        dp_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.parent.dp_comparison_table = self._create_treeview(dp_frame)

        # Greedy Schedule
        greedy_frame = ttk.LabelFrame(tables_frame, text="Greedy Schedule")
        greedy_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.parent.greedy_comparison_table = self._create_treeview(greedy_frame)

        # Differences
        diff_frame = ttk.LabelFrame(tables_frame, text="DP vs Greedy Differences")
        diff_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.parent.diff_comparison_table = self._create_treeview(diff_frame)

    def _create_treeview(self, parent_frame):
        tree = ttk.Treeview(parent_frame, columns=COMPARISON_COLUMNS, show="headings", height=TABLE_HEIGHT)
        for c in COMPARISON_COLUMNS:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=100)
        tree.pack(fill="both", expand=True)
        return tree

    def build_visualization(self):
        """Create plot button."""
        viz_frame = ttk.Frame(self.frame)
        viz_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(viz_frame, text="Plot Comparison", command=self.parent.plot_manager.plot_comparison).pack()

    def display_comparison(self, dp_schedule, dp_cost, greedy_schedule, greedy_cost):
        """Update tables and summary with DP, Greedy, and differences."""
        self._clear_tables()
        differences = []

        for dp, g in zip(dp_schedule, greedy_schedule):
            # Populate DP table
            self.parent.dp_comparison_table.insert("", "end", values=(
                dp["Period"],
                dp["Order"],
                f"🚨 {dp['Emergency']}" if dp["Emergency"] else "-",
                f"${dp['Cost']:.2f}"
            ))

            # Populate Greedy table
            self.parent.greedy_comparison_table.insert("", "end", values=(
                g["Period"],
                g["Order"],
                f"🚨 {g['Emergency']}" if g["Emergency"] else "-",
                f"${g['Cost']:.2f}"
            ))

            # Compute difference
            diff_order = dp["Order"] - g["Order"]
            diff_emergency = dp["Emergency"] - g["Emergency"]
            diff_cost = dp["Cost"] - g["Cost"]

            differences.append((dp["Period"], diff_order, f"🚨 {diff_emergency}" if diff_emergency else "-", f"${diff_cost:.2f}"))

        # Populate differences table
        for d in differences:
            self.parent.diff_comparison_table.insert("", "end", values=d)

        self._update_summary(dp_schedule, dp_cost, greedy_schedule, greedy_cost)

    def _clear_tables(self):
        """Clear all comparison tables."""
        for table in [self.parent.dp_comparison_table, self.parent.greedy_comparison_table, self.parent.diff_comparison_table]:
            table.delete(*table.get_children())

    def _update_summary(self, dp_schedule, dp_cost, greedy_schedule, greedy_cost):
        """Generate summary text highlighting differences."""
        self.parent.comparison_text.delete("1.0", tk.END)

        savings = greedy_cost - dp_cost
        improvement = (savings / greedy_cost) * 100 if greedy_cost > 0 else 0

        dp_orders = sum(s["Order"] for s in dp_schedule)
        greedy_orders = sum(s["Order"] for s in greedy_schedule)

        dp_emergencies = sum(s["Emergency"] for s in dp_schedule)
        greedy_emergencies = sum(s["Emergency"] for s in greedy_schedule)

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              ALGORITHM COMPARISON RESULTS                    ║
╚══════════════════════════════════════════════════════════════╝

Dynamic Programming (Optimal):
  • Total Cost: ${dp_cost:,.2f}
  • Total Orders: {dp_orders}
  • Emergency Orders: {dp_emergencies}

Greedy Approach (Baseline):
  • Total Cost: ${greedy_cost:,.2f}
  • Total Orders: {greedy_orders}
  • Emergency Orders: {greedy_emergencies}

Performance Improvement:
  • Cost Savings: ${savings:,.2f}
  • Percentage Improvement: {improvement:.2f}%
  • Orders Reduced: {greedy_orders - dp_orders}
  • Emergencies Avoided: {greedy_emergencies - dp_emergencies}

Conclusion:
  {"DP significantly outperforms Greedy!" if improvement > 5 else "✅ DP finds optimal solution."}
"""
        self.parent.comparison_text.insert("1.0", summary)

    def get_frame(self):
        return self.frame
