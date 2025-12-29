"""
Visualization and plotting functions for inventory optimization results.
"""

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
    
    def plot_demand(self):
        """Plot demand over time."""
        if not self.check_data():
            return
            
        plt.figure()
        plt.plot(self.parent.current_demand, marker="o")
        plt.title("Demand Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()
    
    def plot_inventory(self):
        """Plot inventory levels over time."""
        if not self.check_data():
            return
            
        inventory = [s["Start"] for s in self.parent.current_schedule]
        inventory.append(self.parent.current_schedule[-1]["End"])
        
        plt.figure()
        plt.step(range(len(inventory)), inventory, where="post")
        plt.title("Inventory Level Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()
    
    def plot_emergency(self):
        """Plot emergency orders over time."""
        if not self.check_data():
            return
            
        emergency = [s["Emergency"] for s in self.parent.current_schedule]
        
        plt.figure()
        plt.bar(range(len(emergency)), emergency)
        plt.title("Emergency Orders Over Time")
        plt.xlabel("Month")
        plt.ylabel("Units")
        plt.grid(True)
        plt.show()
    
    def plot_costs(self):
        """Plot costs per period."""
        if not self.check_data():
            return
            
        costs = [s["Cost"] for s in self.parent.current_schedule]
        
        plt.figure()
        plt.plot(costs, marker="o")
        plt.title("Cost Per Period")
        plt.xlabel("Month")
        plt.ylabel("Cost ($)")
        plt.grid(True)
        plt.show()
    
    def show_backtracking(self):
        """Visualize the backtracking path through the DP solution."""
        if not self.check_data():
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        periods = [s["Period"] for s in self.parent.current_schedule]
        inventory_states = [s["Start"] for s in self.parent.current_schedule]
        orders = [s["Order"] for s in self.parent.current_schedule]
        
        # Plot inventory states with order annotations
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
        
        # Plot cumulative costs
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
        """Plot comprehensive comparison between DP and Greedy approaches."""
        if self.parent.greedy_schedule is None:
            messagebox.showwarning("No Data", "Please run optimization first.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        from Utils.constant import T
        periods = list(range(T))
        
        # Plot 1: Cost per period
        dp_costs = [s["Cost"] for s in self.parent.current_schedule]
        greedy_costs = [s["Cost"] for s in self.parent.greedy_schedule]
        
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