import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox

class PlotManager:
    """Manages all plotting and visualization."""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
    
    def check_data(self):
        """Verify optimization has been run."""
        if self.parent.current_schedule is None:
            messagebox.showwarning("Run Optimization", "Please run optimization first.")
            return False
        return True
    
    def plot_demand(self):
        """Plot demand over time."""
        if not self.check_data():
            return
            
        # FIX: Generate periods dynamically based on data length
        demands = self.parent.current_demand
        periods = range(1, len(demands) + 1)

        plt.figure()
        plt.plot(periods, demands, marker="o")
        plt.title("Demand Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.xticks(periods)  # Ensure integer ticks
        plt.grid(True)
        plt.show()
    
    def plot_inventory(self):
        """Plot inventory levels."""
        if not self.check_data():
            return
            
        inventory = [s["Start"] for s in self.parent.current_schedule]
        # Append the final end inventory for the step plot
        inventory.append(self.parent.current_schedule[-1]["End"])
        
        plt.figure()
        plt.step(range(1, len(inventory) + 1), inventory, where="post")
        plt.title("Inventory Level Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()
    
    def plot_emergency(self):
        """Plot emergency orders."""
        if not self.check_data():
            return
            
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
        if not self.check_data():
            return
            
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
        """Visualize backtracking path."""
        if not self.check_data():
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        periods = [s["Period"] for s in self.parent.current_schedule]
        inventory_states = [s["Start"] for s in self.parent.current_schedule]
        orders = [s["Order"] for s in self.parent.current_schedule]
        
        ax1.plot(periods, inventory_states, 'o-', linewidth=2, markersize=8, 
                label='Inventory State')
        
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
        
        cumulative_costs = np.cumsum([s["Cost"] for s in self.parent.current_schedule])
        ax2.plot(periods, cumulative_costs, 's-', linewidth=2, markersize=8, 
                color='red', label='Cumulative Cost')
        ax2.fill_between(periods, cumulative_costs, alpha=0.3, color='red')
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Cumulative Cost ($)')
        ax2.set_title('Cost Accumulation During Backtracking')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
    
    def plot_comparison(self):
        """Plot DP vs Greedy comparison."""
        if self.parent.greedy_schedule is None:
            messagebox.showwarning("No Data", "Please run optimization first.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # FIX: Define periods dynamically from the actual data
        periods = [s["Period"] for s in self.parent.current_schedule]
        
        # Cost per period
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
        
        # Cumulative cost
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
        
        # Orders per period
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
        
        # Summary metrics
        metrics = ['Total Cost', 'Num Orders', 'Emergencies']
        dp_metrics = [
            self.parent.current_cost / 100, # Keeping your scaling logic
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