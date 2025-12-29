"""
Visualization and plotting functions with comprehensive error handling.
"""

import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
import traceback


class PlotManager:
    """Manages all plotting and visualization with error handling."""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
    
    def check_data(self):
        """Verify that optimization has been run before plotting."""
        if self.parent.current_schedule is None:
            messagebox.showwarning("No Data", "Please run optimization first.")
            return False
        
        if len(self.parent.current_schedule) == 0:
            messagebox.showwarning("No Data", "Schedule is empty.")
            return False
        
        return True
    
    def safe_plot(self, plot_function, error_title="Plot Error"):
        """
        Wrapper for safe plotting with error handling.
        
        Args:
            plot_function: Function that creates the plot
            error_title: Title for error dialog
        """
        try:
            plot_function()
        except Exception as e:
            error_msg = f"Failed to create plot:\n{str(e)}"
            messagebox.showerror(error_title, error_msg)
            traceback.print_exc()
    
    def plot_demand(self):
        """Plot demand over time with error handling."""
        if not self.check_data():
            return
        
        def create_plot():
            if self.parent.current_demand is None or len(self.parent.current_demand) == 0:
                raise ValueError("No demand data available")
            
            plt.figure(figsize=(10, 6))
            periods = list(range(len(self.parent.current_demand)))
            plt.plot(periods, self.parent.current_demand, marker="o", linewidth=2, markersize=8)
            plt.title("Demand Over Time", fontsize=14, fontweight='bold')
            plt.xlabel("Period (Month)", fontsize=12)
            plt.ylabel("Demand (Units)", fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add value labels
            for i, d in enumerate(self.parent.current_demand):
                plt.annotate(f'{d}', (i, d), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=9)
            
            plt.tight_layout()
            plt.show()
        
        self.safe_plot(create_plot, "Demand Plot Error")
    
    def plot_inventory(self):
        """Plot inventory levels with error handling."""
        if not self.check_data():
            return
        
        def create_plot():
            inventory = [s["Start"] for s in self.parent.current_schedule]
            inventory.append(self.parent.current_schedule[-1]["End"])
            
            if len(inventory) == 0:
                raise ValueError("No inventory data available")
            
            plt.figure(figsize=(10, 6))
            periods = list(range(len(inventory)))
            plt.step(periods, inventory, where="post", linewidth=2)
            plt.fill_between(periods, inventory, alpha=0.3, step="post")
            plt.title("Inventory Level Over Time", fontsize=14, fontweight='bold')
            plt.xlabel("Period (Month)", fontsize=12)
            plt.ylabel("Inventory (Units)", fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add horizontal line at zero
            plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Zero Inventory')
            plt.legend()
            
            plt.tight_layout()
            plt.show()
        
        self.safe_plot(create_plot, "Inventory Plot Error")
    
    def plot_emergency(self):
        """Plot emergency orders with error handling."""
        if not self.check_data():
            return
        
        def create_plot():
            emergency = [s["Emergency"] for s in self.parent.current_schedule]
            
            plt.figure(figsize=(10, 6))
            periods = list(range(len(emergency)))
            colors = ['red' if e > 0 else 'lightgray' for e in emergency]
            plt.bar(periods, emergency, color=colors, alpha=0.7, edgecolor='black')
            plt.title("Emergency Orders Over Time", fontsize=14, fontweight='bold')
            plt.xlabel("Period (Month)", fontsize=12)
            plt.ylabel("Emergency Units", fontsize=12)
            plt.grid(True, alpha=0.3, axis='y')
            
            # Add count
            emergency_count = sum(1 for e in emergency if e > 0)
            plt.text(0.02, 0.98, f'Emergency Periods: {emergency_count}', 
                    transform=plt.gca().transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            plt.show()
        
        self.safe_plot(create_plot, "Emergency Plot Error")
    
    def plot_costs(self):
        """Plot costs per period with error handling."""
        if not self.check_data():
            return
        
        def create_plot():
            costs = [s["Cost"] for s in self.parent.current_schedule]
            
            if len(costs) == 0:
                raise ValueError("No cost data available")
            
            plt.figure(figsize=(10, 6))
            periods = list(range(len(costs)))
            plt.plot(periods, costs, marker="o", linewidth=2, markersize=8)
            plt.fill_between(periods, costs, alpha=0.3)
            plt.title("Cost Per Period", fontsize=14, fontweight='bold')
            plt.xlabel("Period (Month)", fontsize=12)
            plt.ylabel("Cost ($)", fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add statistics
            avg_cost = np.mean(costs)
            max_cost = max(costs)
            plt.axhline(y=avg_cost, color='g', linestyle='--', alpha=0.5, 
                       label=f'Average: ${avg_cost:.2f}')
            plt.legend()
            
            plt.tight_layout()
            plt.show()
        
        self.safe_plot(create_plot, "Cost Plot Error")
    
    def show_backtracking(self):
        """Visualize backtracking path with error handling."""
        if not self.check_data():
            return
        
        def create_plot():
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            periods = [s["Period"] for s in self.parent.current_schedule]
            inventory_states = [s["Start"] for s in self.parent.current_schedule]
            orders = [s["Order"] for s in self.parent.current_schedule]
            
            if len(periods) == 0:
                raise ValueError("No backtracking data available")
            
            # Plot 1: Inventory states with orders
            ax1.plot(periods, inventory_states, 'o-', linewidth=2, markersize=8, 
                    label='Inventory State')
            
            for i, (p, inv, order) in enumerate(zip(periods, inventory_states, orders)):
                if order > 0:
                    ax1.annotate(f'Order: {order}', 
                                xy=(p, inv), 
                                xytext=(10, 10), 
                                textcoords='offset points',
                                fontsize=8,
                                bbox=dict(boxstyle='round,pad=0.3', 
                                        facecolor='yellow', alpha=0.7),
                                arrowprops=dict(arrowstyle='->', 
                                              connectionstyle='arc3,rad=0'))
            
            ax1.set_xlabel('Period', fontsize=12)
            ax1.set_ylabel('Inventory Level', fontsize=12)
            ax1.set_title('Backtracking Path: Optimal Decisions', 
                         fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Plot 2: Cumulative costs
            cumulative_costs = np.cumsum([s["Cost"] for s in self.parent.current_schedule])
            ax2.plot(periods, cumulative_costs, 's-', linewidth=2, markersize=8, 
                    color='red', label='Cumulative Cost')
            ax2.fill_between(periods, cumulative_costs, alpha=0.3, color='red')
            ax2.set_xlabel('Period', fontsize=12)
            ax2.set_ylabel('Cumulative Cost ($)', fontsize=12)
            ax2.set_title('Cost Accumulation During Backtracking', 
                         fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # Add final cost annotation
            final_cost = cumulative_costs[-1]
            ax2.text(0.98, 0.02, f'Total: ${final_cost:,.2f}', 
                    transform=ax2.transAxes, 
                    horizontalalignment='right',
                    verticalalignment='bottom',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
                    fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            plt.show()
        
        self.safe_plot(create_plot, "Backtracking Visualization Error")
    
    def plot_comparison(self):
        """Plot DP vs Greedy comparison with error handling."""
        if self.parent.greedy_schedule is None:
            messagebox.showwarning("No Data", 
                                 "Greedy solution not available. Please run optimization first.")
            return
        
        def create_plot():
            from utils.constants import T
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            
            periods = list(range(T))
            
            # Plot 1: Cost per period
            dp_costs = [s["Cost"] for s in self.parent.current_schedule]
            greedy_costs = [s["Cost"] for s in self.parent.greedy_schedule]
            
            ax1.plot(periods, dp_costs, 'o-', label='DP (Optimal)', 
                    linewidth=2, markersize=8, color='blue')
            ax1.plot(periods, greedy_costs, 's--', label='Greedy', 
                    linewidth=2, markersize=8, color='red')
            ax1.set_xlabel('Period', fontsize=11)
            ax1.set_ylabel('Cost ($)', fontsize=11)
            ax1.set_title('Cost Per Period Comparison', fontsize=12, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Cumulative cost
            dp_cumulative = np.cumsum(dp_costs)
            greedy_cumulative = np.cumsum(greedy_costs)
            
            ax2.plot(periods, dp_cumulative, 'o-', label='DP', 
                    linewidth=2, markersize=8, color='blue')
            ax2.plot(periods, greedy_cumulative, 's--', label='Greedy', 
                    linewidth=2, markersize=8, color='red')
            ax2.set_xlabel('Period', fontsize=11)
            ax2.set_ylabel('Cumulative Cost ($)', fontsize=11)
            ax2.set_title('Cumulative Cost Comparison', fontsize=12, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Add savings annotation
            savings = greedy_cumulative[-1] - dp_cumulative[-1]
            ax2.text(0.98, 0.5, f'Savings: ${savings:,.2f}', 
                    transform=ax2.transAxes, 
                    horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
                    fontsize=10, fontweight='bold')
            
            # Plot 3: Orders per period
            dp_orders = [s["Order"] for s in self.parent.current_schedule]
            greedy_orders = [s["Order"] for s in self.parent.greedy_schedule]
            
            x = np.arange(len(periods))
            width = 0.35
            
            ax3.bar(x - width/2, dp_orders, width, label='DP', alpha=0.8, color='blue')
            ax3.bar(x + width/2, greedy_orders, width, label='Greedy', alpha=0.8, color='red')
            ax3.set_xlabel('Period', fontsize=11)
            ax3.set_ylabel('Order Quantity', fontsize=11)
            ax3.set_title('Order Quantities Comparison', fontsize=12, fontweight='bold')
            ax3.set_xticks(x)
            ax3.set_xticklabels(periods)
            ax3.legend()
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Plot 4: Summary metrics
            metrics = ['Total Cost\n(÷100)', 'Orders', 'Emergencies']
            dp_metrics = [
                self.parent.current_cost / 100,
                sum(1 for s in self.parent.current_schedule if s["Order"] > 0),
                sum(1 for s in self.parent.current_schedule if s["Emergency"] > 0)
            ]
            greedy_metrics = [
                self.parent.greedy_cost / 100,
                sum(1 for s in self.parent.greedy_schedule if s["Order"] > 0),
                sum(1 for s in self.parent.greedy_schedule if s["Emergency"] > 0)
            ]
            
            x = np.arange(len(metrics))
            ax4.bar(x - width/2, dp_metrics, width, label='DP', alpha=0.8, color='blue')
            ax4.bar(x + width/2, greedy_metrics, width, label='Greedy', alpha=0.8, color='red')
            ax4.set_ylabel('Value', fontsize=11)
            ax4.set_title('Overall Metrics Comparison', fontsize=12, fontweight='bold')
            ax4.set_xticks(x)
            ax4.set_xticklabels(metrics, fontsize=10)
            ax4.legend()
            ax4.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.show()
        
        self.safe_plot(create_plot, "Comparison Plot Error")