import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox

class PlotManager:
    """Manages all plotting and visualization for the inventory optimization system."""
    
    def __init__(self, parent_gui):
        """
        Initialize plot manager.
        
        Args:
            parent_gui: Reference to parent InventoryGUI instance
        """
        self.parent = parent_gui
    
    def check_data(self):
        """Verify that optimization has been run before plotting."""
        if self.parent.current_schedule is None:
            messagebox.showwarning("Run Optimization", "Please run optimization first.")
            return False
        return True

    def _get_max_capacity(self):
        """Helper to safely get max storage from the GUI input for scaling."""
        try:
            # Try to fetch from the Entry widget in the GUI
            return int(self.parent.max_storage.get())
        except (ValueError, AttributeError):
            # Fallback: find the highest number in the current data
            max_inv = 0
            if self.parent.current_schedule:
                max_inv = max(s['Start'] for s in self.parent.current_schedule)
            return max(max_inv, 10) # Default minimum of 10

    def plot_demand(self):
        """Plot demand over time."""
        if not self.check_data(): return
        
        demands = self.parent.current_demand
        periods = range(1, len(demands) + 1)
            
        plt.figure()
        plt.plot(periods, demands, marker="o")
        plt.title("Demand Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.xticks(periods)
        plt.grid(True)
        plt.show()
    
    def plot_inventory(self):
        """Plot inventory levels over time."""
        if not self.check_data(): return
            
        inventory = [s["Start"] for s in self.parent.current_schedule]
        # Append end state for the step plot
        inventory.append(self.parent.current_schedule[-1]["End"])
        periods = range(1, len(inventory) + 1)

        # Get max capacity for plotting limits
        max_cap = self._get_max_capacity()

        plt.figure()
        plt.step(periods, inventory, where="post")
        
        # Set Y-limit to show full warehouse capacity
        plt.ylim(0, max_cap * 1.1) 
        plt.axhline(y=max_cap, color='r', linestyle='--', label='Max Capacity')
        
        plt.title("Inventory Level vs Capacity")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_emergency(self):
        """Plot emergency orders over time."""
        if not self.check_data(): return
            
        emergency = [s["Emergency"] for s in self.parent.current_schedule]
        periods = [s["Period"] for s in self.parent.current_schedule]
        
        plt.figure()
        plt.bar(periods, emergency)
        plt.title("Emergency Orders Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.xticks(periods)
        plt.grid(True)
        plt.show()
    
    def plot_costs(self):
        """Plot costs per period."""
        if not self.check_data(): return
            
        costs = [s["Cost"] for s in self.parent.current_schedule]
        periods = [s["Period"] for s in self.parent.current_schedule]
        
        plt.figure()
        plt.plot(periods, costs, marker="o")
        plt.title("Cost Per Period")
        plt.xlabel("Month")
        plt.ylabel("Cost ($)")
        plt.xticks(periods)
        plt.grid(True)
        plt.show()
    
    def show_backtracking(self):
        """Visualize the backtracking path: Start -> After Order -> End Inventory."""
        if not self.check_data():
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # Access data from parent
        schedule = self.parent.current_schedule
        max_storage = self._get_max_capacity()

        periods = [s["Period"] for s in schedule]
        start_inv = [s["Start"] for s in schedule]
        orders = [s["Order"] for s in schedule]
        end_inv = [s["End"] for s in schedule]
        
        # Calculate 'After Order' level (clamped by max storage for visualization)
        after_order = [
            min(s["Start"] + s["Order"], max_storage)
            for s in schedule
        ]

        # Plot lines
        ax.plot(periods, start_inv, 'o-', label='Start Inventory', linewidth=2, color='blue')
        ax.plot(periods, after_order, 's-', label='After Order', linewidth=2, color='green')
        ax.plot(periods, end_inv, '^-', label='End Inventory', linewidth=2, color='orange')

        # Capacity line
        ax.axhline(
            max_storage,
            linestyle='--',
            color='red',
            alpha=0.5,
            label='Max Storage'
        )

        # Annotate orders
        for i, (p, q) in enumerate(zip(periods, orders)):
            if q > 0:
                ax.annotate(
                    f'+{q}',
                    xy=(p, after_order[i]),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7)
                )

        ax.set_xlabel('Period')
        ax.set_ylabel('Inventory Level')
        ax.set_title('DP Backtracking Path (Start → Order → End)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)  # Ensure y-axis starts at 0

        plt.tight_layout()
        plt.show()
    
    def plot_comparison(self):
        """Plot comprehensive comparison between DP and Greedy approaches."""
        if self.parent.greedy_schedule is None:
            messagebox.showwarning("No Data", "Please run optimization first.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        periods = [s["Period"] for s in self.parent.current_schedule]
        
        # Plot 1: Cost per period
        dp_costs = [s["Cost"] for s in self.parent.current_schedule]
        greedy_costs = [s["Cost"] for s in self.parent.greedy_schedule]
        
        ax1.plot(periods, dp_costs, 'o-', label='DP', linewidth=2, markersize=8)
        ax1.plot(periods, greedy_costs, 's--', label='Greedy', linewidth=2, markersize=8)
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Cost ($)')
        ax1.set_title('Cost Per Period Comparison')
        ax1.set_xticks(periods)
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
        ax2.set_xticks(periods)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Orders per period
        dp_orders = [s["Order"] for s in self.parent.current_schedule]
        greedy_orders = [s["Order"] for s in self.parent.greedy_schedule]
        
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
            self.parent.current_cost / 100,  # Scale for visibility
            sum(1 for s in self.parent.current_schedule if s["Order"] > 0),
            sum(1 for s in self.parent.current_schedule if s["Emergency"] > 0)
        ]
        greedy_metrics = [
            self.parent.greedy_cost / 100,
            sum(1 for s in self.parent.greedy_schedule if s["Order"] > 0),
            sum(1 for s in self.parent.greedy_schedule if s["Emergency"] > 0)
        ]
        
        x_metrics = np.arange(len(metrics))
        ax4.bar(x_metrics - width/2, dp_metrics, width, label='DP', alpha=0.8)
        ax4.bar(x_metrics + width/2, greedy_metrics, width, label='Greedy', alpha=0.8)
        ax4.set_ylabel('Value (Cost Scaled /100)')
        ax4.set_title('Overall Metrics Comparison')
        ax4.set_xticks(x_metrics)
        ax4.set_xticklabels(metrics)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()