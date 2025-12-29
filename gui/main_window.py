"""
Main application window with comprehensive error handling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import traceback

from models.inventory_solver import InventoryDPSolver
from gui.tabs.main_tab import MainTab
from gui.tabs.dp_visualization_tab import DPVisualizationTab
from gui.tabs.comparison_tab import ComparisonTab
from gui.widgets.plot_manager import PlotManager
from Utils.constant import WINDOW_WIDTH, WINDOW_HEIGHT, T
from Utils.validators import InputValidator, SolverErrorHandler, ValidationError


class InventoryGUI(tk.Tk):
    """Main GUI application with comprehensive error handling."""
    
    def __init__(self):
        super().__init__()
        self.title("Medical Inventory Optimization (DP)")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # State variables
        self.current_demand = None
        self.current_schedule = None
        self.current_cost = None
        self.solver = None
        self.greedy_schedule = None
        self.greedy_cost = None

        # Widget references
        self.demand_entry = None
        self.init_inv = None
        self.c_order_fixed = None
        self.c_unit = None
        self.c_storage = None
        self.c_emergency_fixed = None
        self.c_emergency_unit = None
        self.max_storage = None
        self.table = None
        self.log = None
        self.dp_tree = None
        self.decision_tree = None
        self.comparison_text = None
        self.dp_comparison_table = None
        self.greedy_comparison_table = None

        # Initialize validator and plot manager
        self.validator = InputValidator()
        self.plot_manager = PlotManager(self)

        # Create tabs
        self.setup_tabs()
        
        # Set up error handling
        self.report_callback_exception = self.handle_exception
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Global exception handler for the GUI."""
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Exception occurred:\n{error_msg}")
        
        user_msg = SolverErrorHandler.handle_solver_error(exc_value)
        messagebox.showerror("Error", user_msg)
    
    def setup_tabs(self):
        """Create notebook and tabs."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.main_tab = MainTab(self.notebook, self)
        self.dp_viz_tab = DPVisualizationTab(self.notebook, self)
        self.comparison_tab = ComparisonTab(self.notebook, self)
        
        self.notebook.add(self.main_tab.get_frame(), text="Main Optimization")
        self.notebook.add(self.dp_viz_tab.get_frame(), text="DP Table Visualization")
        self.notebook.add(self.comparison_tab.get_frame(), text="DP vs Greedy Comparison")
    
    def run_solver(self):
        """
        Main solver orchestration with comprehensive error handling.
        """
        try:
            # Validate all inputs
            is_valid, values, errors = self.validator.validate_all_inputs(
                self.demand_entry.get(),
                self.init_inv.get(),
                self.c_order_fixed.get(),
                self.c_unit.get(),
                self.c_storage.get(),
                self.c_emergency_fixed.get(),
                self.c_emergency_unit.get(),
                self.max_storage.get()
            )
            
            if not is_valid:
                error_msg = "Input Validation Failed:\n\n" + "\n".join(errors)
                messagebox.showerror("Validation Error", error_msg)
                return
            
            # Show warnings if any (starting with ⚠️)
            warnings = [e for e in errors if e.startswith("⚠️")]
            if warnings:
                warning_msg = "\n".join(warnings)
                response = messagebox.askokcancel(
                    "Warning", 
                    f"{warning_msg}\n\nDo you want to continue anyway?"
                )
                if not response:
                    return
            
            # Extract validated values
            demand = values['demand']
            init_inv = values['initial_inventory']
            c_order_fixed = values['c_order_fixed']
            c_unit = values['c_unit']
            c_storage = values['c_storage']
            c_emergency_fixed = values['c_emergency_fixed']
            c_emergency_unit = values['c_emergency_unit']
            max_storage = values['max_storage']
            
            # Show progress indicator
            self.log.delete("1.0", tk.END)
            self.log.insert(tk.END, "⏳ Running optimization...\n")
            self.update_idletasks()
            
            # Create solver with error handling
            try:
                solver = InventoryDPSolver(
                    T, demand, max_storage, init_inv,
                    c_order_fixed, c_unit, c_storage,
                    c_emergency_fixed, c_emergency_unit
                )
            except Exception as e:
                raise ValidationError(f"Failed to create solver: {str(e)}")
            
            # Solve with DP
            try:
                self.log.insert(tk.END, "⏳ Computing DP solution...\n")
                self.update_idletasks()
                solver.solve()
                schedule, cost = solver.backtrack()
            except MemoryError:
                messagebox.showerror(
                    "Memory Error",
                    "Problem size too large for available memory.\n\n"
                    "Try reducing:\n"
                    "• Max storage capacity\n"
                    "• Number of periods"
                )
                return
            except Exception as e:
                error_msg = SolverErrorHandler.handle_solver_error(e)
                messagebox.showerror("Solver Error", error_msg)
                return
            
            # Solve with Greedy
            try:
                self.log.insert(tk.END, "⏳ Computing greedy solution...\n")
                self.update_idletasks()
                greedy_schedule, greedy_cost = solver.solve_greedy()
            except Exception as e:
                # Greedy failure is not critical
                print(f"Greedy solver failed: {e}")
                greedy_schedule, greedy_cost = None, None
            
            # Validate results
            if schedule is None or len(schedule) == 0:
                messagebox.showerror("Error", "Solver returned empty schedule")
                return
            
            if cost is None or cost < 0:
                messagebox.showerror("Error", "Invalid cost calculated")
                return
            
            # Update state
            self.current_demand = demand
            self.current_schedule = schedule
            self.current_cost = cost
            self.solver = solver
            self.greedy_schedule = greedy_schedule
            self.greedy_cost = greedy_cost
            
            # Update displays with error handling
            try:
                self.update_main_table(schedule, cost, demand)
            except Exception as e:
                print(f"Error updating main table: {e}")
                messagebox.showwarning("Display Warning", "Could not update main table")
            
            try:
                self.dp_viz_tab.display_tables(solver)
            except Exception as e:
                print(f"Error updating DP visualization: {e}")
                messagebox.showwarning("Display Warning", "Could not update DP tables")
            
            try:
                if greedy_schedule is not None:
                    self.comparison_tab.display_comparison(
                        schedule, cost, greedy_schedule, greedy_cost
                    )
            except Exception as e:
                print(f"Error updating comparison: {e}")
                messagebox.showwarning("Display Warning", "Could not update comparison")
            
            # Success message
            self.log.insert(tk.END, "\n✅ Optimization completed successfully!\n")
            messagebox.showinfo(
                "Success",
                f"Optimization completed!\n\n"
                f"Optimal Cost: ${cost:,.2f}\n"
                f"Emergency Orders: {sum(1 for s in schedule if s['Emergency'] > 0)}"
            )
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            error_msg = SolverErrorHandler.handle_solver_error(e)
            messagebox.showerror("Unexpected Error", error_msg)
            # Print full traceback for debugging
            traceback.print_exc()
    
    def update_main_table(self, schedule, cost, demand):
        """Update main results table with error handling."""
        try:
            # Clear table
            self.table.delete(*self.table.get_children())
            
            emergency_count = 0
            total_ordered = 0
            total_emergency = 0
            
            for s in schedule:
                if s["Emergency"] > 0:
                    emergency_count += 1
                    total_emergency += s["Emergency"]
                
                total_ordered += s["Order"]
                
                self.table.insert("", "end", values=(
                    s["Period"], 
                    s["Start"], 
                    s["Order"],
                    s["Demand"],
                    f"🚨 {s['Emergency']}" if s["Emergency"] else "-",
                    s["End"],
                    f"${s['Cost']:.2f}"
                ))
            
            # Update log with detailed summary
            self.log.delete("1.0", tk.END)
            self.log.insert(tk.END, "╔═══════════════════════════════════════════╗\n")
            self.log.insert(tk.END, "║        OPTIMIZATION RESULTS               ║\n")
            self.log.insert(tk.END, "╚═══════════════════════════════════════════╝\n\n")
            self.log.insert(tk.END, f" Optimal Total Cost: ${cost:,.2f}\n")
            self.log.insert(tk.END, f" Total Demand: {sum(demand):,} units\n")
            self.log.insert(tk.END, f" Total Ordered: {total_ordered:,} units\n")
            self.log.insert(tk.END, f" Emergency Orders: {emergency_count} periods\n")
            self.log.insert(tk.END, f" Emergency Units: {total_emergency:,} units\n")
            self.log.insert(tk.END, f" Average Cost/Period: ${cost/T:.2f}\n")
            
            # Add efficiency metrics
            regular_orders = sum(1 for s in schedule if s["Order"] > 0)
            self.log.insert(tk.END, f"📅 Regular Orders: {regular_orders} periods\n")
            
            if total_ordered > 0:
                fulfillment_rate = (sum(demand) - total_emergency) / sum(demand) * 100
                self.log.insert(tk.END, f"✓ Fulfillment Rate: {fulfillment_rate:.1f}%\n")
            
        except Exception as e:
            raise Exception(f"Error updating main table: {str(e)}")
    
    def validate_before_plot(self):
        """Validate that data exists before plotting."""
        is_valid, error = self.validator.validate_solver_state(self.solver)
        if not is_valid:
            messagebox.showwarning("No Data", error)
            return False
        
        if self.current_schedule is None:
            messagebox.showwarning("No Data", "Please run optimization first.")
            return False
        
        return True