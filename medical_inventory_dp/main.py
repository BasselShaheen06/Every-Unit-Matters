#!/usr/bin/env python3
"""
Medical Supply Chain Inventory Optimization
============================================
Dynamic Programming-based decision support system for hospital medical supplies.

Usage:
    python main.py --scenario normal
    python main.py --scenario spike --output output/spike
    python main.py --list-scenarios
"""

import argparse
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cost_model import CostModel
from src.dp_solver import DPSolver
from src.backtracking import generate_solution_report


def load_scenarios(scenarios_path: str = None) -> dict:
    """Load scenarios from JSON file."""
    if scenarios_path is None:
        scenarios_path = os.path.join(
            os.path.dirname(__file__), 'data', 'scenarios.json'
        )
    
    with open(scenarios_path, 'r') as f:
        data = json.load(f)
    
    return data.get('scenarios', data)


def run_optimization(scenario: dict) -> dict:
    """
    Run the DP optimization for a given scenario.
    
    Args:
        scenario: Dictionary with T, demand, costs, etc.
        
    Returns:
        Solution report dictionary
    """
    # Extract parameters
    T = scenario['T']
    demand = scenario['demand']
    initial_inventory = scenario.get('initial_inventory', 0)
    max_storage = scenario['MAX_STORAGE']
    c_order = scenario['c_order']
    c_unit = scenario.get('c_unit', 0)  # Per-unit cost (optional, default 0)
    c_storage = scenario['c_storage']
    c_shortage = scenario['c_shortage']
    
    # Create cost model
    cost_model = CostModel(c_order, c_storage, c_shortage, c_unit)
    
    # Create and solve
    solver = DPSolver(
        T=T,
        demand=demand,
        max_storage=max_storage,
        cost_model=cost_model,
        initial_inventory=initial_inventory
    )
    
    min_cost = solver.solve()
    
    # Generate full report
    report = generate_solution_report(solver)
    
    return report


def print_solution(solution: dict, scenario_name: str = ""):
    """Print solution in a formatted way."""
    print("\n" + "=" * 60)
    print(f"  OPTIMIZATION RESULTS{f' - {scenario_name}' if scenario_name else ''}")
    print("=" * 60)
       
    params = solution['parameters']
    print(f"\n[PARAMS] SCENARIO PARAMETERS")
    print(f"   Planning Horizon: {params['T']} periods")
    print(f"   Initial Inventory: {params['initial_inventory']} units")
    print(f"   Max Storage: {params['max_storage']} units")
    print(f"   Demand: {params['demand']}")
    print(f"   Costs: order=${params['costs']['c_order']} + ${params['costs']['c_unit']}/unit, "
          f"storage=${params['costs']['c_storage']}/unit, "
          f"shortage=${params['costs']['c_shortage']}/unit")
    
    print(f"\n[RESULT] OPTIMAL SOLUTION")
    print(f"   Order Schedule:    {solution['order_schedule']}")
    print(f"   Inventory Levels:  {solution['inventory_levels']}")
    
    if solution.get('shortages'):
        print(f"   Shortages:         {solution['shortages']}")
    
    breakdown = solution['cost_breakdown']
    print(f"\n[COSTS] COST BREAKDOWN")
    print(f"   Ordering Cost:  ${breakdown['ordering']:,.2f}")
    print(f"   Storage Cost:   ${breakdown['storage']:,.2f}")
    print(f"   Shortage Cost:  ${breakdown['shortage']:,.2f}")
    print(f"   ----------------------")
    print(f"   TOTAL COST:     ${breakdown['total']:,.2f}")
    
    print("\n" + "=" * 60)


def save_results(solution: dict, output_dir: str):
    """Save results to JSON and generate plots."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON
    json_path = os.path.join(output_dir, 'solution.json')
    with open(json_path, 'w') as f:
        json.dump(solution, f, indent=2)
    print(f"[OK] Saved results to: {json_path}")
    
    # Try to generate plots
    try:
        from src.visualization import save_all_plots
        save_all_plots(solution, output_dir)
        print(f"[OK] Saved visualizations to: {output_dir}/")
    except ImportError as e:
        print(f"[WARN] Could not generate plots: {e}")


def list_scenarios(scenarios: dict):
    """List available scenarios."""
    print("\nAvailable Scenarios:")
    print("-" * 50)
    for name, scenario in scenarios.items():
        desc = scenario.get('description', 'No description')
        T = scenario.get('T', '?')
        print(f"  - {name}: {desc} (T={T})")
    print("-" * 50)
    print("\nUsage: python main.py --scenario <name>")


def main():
    parser = argparse.ArgumentParser(
        description='Medical Supply Chain Inventory Optimization using DP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --scenario normal
  python main.py --scenario spike --output output/spike_results
  python main.py --list-scenarios
  python main.py --scenario normal --no-plots
        """
    )
    
    parser.add_argument(
        '--scenario', '-s',
        type=str,
        help='Scenario name from scenarios.json'
    )
    
    parser.add_argument(
        '--scenarios-file', '-f',
        type=str,
        help='Path to custom scenarios JSON file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    
    parser.add_argument(
        '--list-scenarios', '-l',
        action='store_true',
        help='List available scenarios'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Skip generating visualization plots'
    )
    
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Output only JSON (no console formatting)'
    )
    
    args = parser.parse_args()
    
    # Load scenarios
    try:
        scenarios = load_scenarios(args.scenarios_file)
    except FileNotFoundError as e:
        print(f"Error: Could not load scenarios file: {e}")
        return 1
    
    # List scenarios
    if args.list_scenarios:
        list_scenarios(scenarios)
        return 0
    
    # Require scenario
    if not args.scenario:
        print("Error: Please specify a scenario with --scenario <name>")
        print("Use --list-scenarios to see available options")
        return 1
    
    # Get scenario
    if args.scenario not in scenarios:
        print(f"Error: Unknown scenario '{args.scenario}'")
        list_scenarios(scenarios)
        return 1
    
    scenario = scenarios[args.scenario]
    
    # Run optimization
    print(f"\n[RUN] Running optimization for scenario: {args.scenario}")
    solution = run_optimization(scenario)
    
    # Output results
    if args.json_only:
        print(json.dumps(solution, indent=2))
    else:
        print_solution(solution, args.scenario)
        
        # Save results - use absolute path based on script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_base = os.path.join(script_dir, args.output)
        output_dir = os.path.join(output_base, args.scenario)
        save_results(solution, output_dir)
        
        if not args.no_plots:
            print("\n[DONE] Optimization complete!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
