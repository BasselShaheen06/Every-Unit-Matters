#!/usr/bin/env python3
"""
Medical Inventory Optimization - GUI Interface
===============================================
Graphical interface for scenario selection and optimization.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cost_model import CostModel
from src.dp_solver import DPSolver
from src.backtracking import generate_solution_report


class InventoryOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Inventory Optimizer")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Load scenarios
        self.scenarios = self.load_scenarios()
        self.current_solution = None
        
        self.setup_ui()
    
    def load_scenarios(self):
        """Load scenarios from JSON file."""
        scenarios_path = os.path.join(
            os.path.dirname(__file__), 'data', 'scenarios.json'
        )
        with open(scenarios_path, 'r') as f:
            data = json.load(f)
        return data.get('scenarios', data)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title = tk.Label(
            self.root, 
            text="Medical Inventory Optimization",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0'
        )
        title.pack(pady=15)
        
        # Scenario selection frame
        select_frame = tk.Frame(self.root, bg='#f0f0f0')
        select_frame.pack(pady=10)
        
        tk.Label(
            select_frame, 
            text="Select Scenario:",
            font=('Arial', 12),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=5)
        
        self.scenario_var = tk.StringVar()
        self.scenario_combo = ttk.Combobox(
            select_frame,
            textvariable=self.scenario_var,
            values=list(self.scenarios.keys()),
            state='readonly',
            width=25,
            font=('Arial', 11)
        )
        self.scenario_combo.pack(side=tk.LEFT, padx=5)
        self.scenario_combo.bind('<<ComboboxSelected>>', self.on_scenario_selected)
        
        # Run button
        self.run_btn = tk.Button(
            select_frame,
            text="Run Optimization",
            command=self.run_optimization,
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            padx=15,
            pady=5
        )
        self.run_btn.pack(side=tk.LEFT, padx=15)
        
        # Scenario description
        self.desc_label = tk.Label(
            self.root,
            text="",
            font=('Arial', 10, 'italic'),
            bg='#f0f0f0',
            fg='#666'
        )
        self.desc_label.pack(pady=5)
        
        # Results frame
        results_frame = tk.LabelFrame(
            self.root,
            text="Results",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Results text area
        self.results_text = tk.Text(
            results_frame,
            font=('Consolas', 11),
            wrap=tk.WORD,
            height=20
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        
        self.charts_btn = tk.Button(
            btn_frame,
            text="Open Charts Folder",
            command=self.open_charts,
            font=('Arial', 11),
            bg='#2196F3',
            fg='white',
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.charts_btn.pack(side=tk.LEFT, padx=10)
        
        # Select first scenario
        if self.scenarios:
            self.scenario_combo.current(0)
            self.on_scenario_selected(None)
    
    def on_scenario_selected(self, event):
        """Handle scenario selection."""
        scenario_name = self.scenario_var.get()
        if scenario_name in self.scenarios:
            desc = self.scenarios[scenario_name].get('description', '')
            T = self.scenarios[scenario_name].get('T', '?')
            self.desc_label.config(text=f"{desc} (T={T} periods)")
    
    def run_optimization(self):
        """Run the optimization for selected scenario."""
        scenario_name = self.scenario_var.get()
        if not scenario_name:
            messagebox.showwarning("Warning", "Please select a scenario first!")
            return
        
        scenario = self.scenarios[scenario_name]
        
        try:
            # Extract parameters
            T = scenario['T']
            demand = scenario['demand']
            initial_inventory = scenario.get('initial_inventory', 0)
            max_storage = scenario['MAX_STORAGE']
            c_order = scenario['c_order']
            c_unit = scenario.get('c_unit', 0)
            c_storage = scenario['c_storage']
            c_shortage = scenario['c_shortage']
            
            # Create cost model and solver
            cost_model = CostModel(c_order, c_storage, c_shortage, c_unit)
            solver = DPSolver(
                T=T,
                demand=demand,
                max_storage=max_storage,
                cost_model=cost_model,
                initial_inventory=initial_inventory
            )
            
            # Solve
            solver.solve()
            solution = generate_solution_report(solver)
            self.current_solution = solution
            
            # Display results
            self.display_results(scenario_name, solution)
            
            # Save plots
            self.save_plots(scenario_name, solution)
            
            # Enable charts button
            self.charts_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")
    
    def display_results(self, scenario_name, solution):
        """Display optimization results."""
        self.results_text.delete(1.0, tk.END)
        
        params = solution['parameters']
        breakdown = solution['cost_breakdown']
        
        text = f"""
{'='*55}
  OPTIMIZATION RESULTS - {scenario_name}
{'='*55}

SCENARIO PARAMETERS
  Planning Horizon: {params['T']} periods
  Initial Inventory: {params['initial_inventory']} units
  Max Storage: {params['max_storage']} units
  Demand: {params['demand']}

COSTS
  Order: ${params['costs']['c_order']} + ${params['costs']['c_unit']}/unit
  Storage: ${params['costs']['c_storage']}/unit
  Shortage: ${params['costs']['c_shortage']}/unit

{'='*55}
OPTIMAL SOLUTION
{'='*55}

  Order Schedule:    {solution['order_schedule']}
  Inventory Levels:  {solution['inventory_levels']}
  Shortages:         {solution.get('shortages', [])}

COST BREAKDOWN
  Ordering Cost:  ${breakdown['ordering']:,.2f}
  Storage Cost:   ${breakdown['storage']:,.2f}
  Shortage Cost:  ${breakdown['shortage']:,.2f}
  {'─'*30}
  TOTAL COST:     ${breakdown['total']:,.2f}

{'='*55}
"""
        self.results_text.insert(tk.END, text)
    
    def save_plots(self, scenario_name, solution):
        """Save visualization plots."""
        try:
            from src.visualization import save_all_plots
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, 'output', scenario_name)
            save_all_plots(solution, output_dir)
        except Exception as e:
            print(f"Warning: Could not save plots: {e}")
    
    def open_charts(self):
        """Open the output folder with charts."""
        scenario_name = self.scenario_var.get()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'output', scenario_name)
        
        if os.path.exists(output_dir):
            # Open folder in file explorer
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.call(['open', output_dir])
            else:
                subprocess.call(['xdg-open', output_dir])
        else:
            messagebox.showinfo("Info", "Please run optimization first to generate charts.")


def main():
    root = tk.Tk()
    app = InventoryOptimizerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
