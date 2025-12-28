# Medical Supply Chain Inventory Optimization

A Dynamic Programming-based decision support system for hospital medical supply ordering optimization.

## Overview

This system helps hospital operations teams determine optimal ordering policies for medical supplies over a finite planning horizon, minimizing total operational costs while preventing shortages.

## Features

- **DP-based optimization**: Uses backward induction to find globally optimal ordering decisions
- **Realistic cost modeling**: Accounts for ordering, storage, and shortage costs
- **Multiple scenarios**: Pre-built test scenarios for different situations
- **Visualizations**: Generates charts for inventory, orders, and cost breakdown
- **Modular design**: Clean separation of concerns for easy customization

## Installation

```bash
# Clone or copy the project
cd medical_inventory_dp

# Install dependencies (matplotlib for visualizations)
pip install matplotlib
```

## Usage

### Command Line

```bash
# List available scenarios
python main.py --list-scenarios

# Run optimization for a specific scenario
python main.py --scenario normal

# Run with custom output directory
python main.py --scenario spike --output results/spike_analysis

# Skip plot generation
python main.py --scenario normal --no-plots

# JSON output only
python main.py --scenario normal --json-only
```

### Programmatic Usage

```python
from src.cost_model import CostModel
from src.dp_solver import DPSolver
from src.backtracking import generate_solution_report

# Define problem
cost_model = CostModel(c_order=50, c_storage=2, c_shortage=20)
solver = DPSolver(
    T=5,
    demand=[10, 12, 15, 30, 8],
    max_storage=40,
    cost_model=cost_model,
    initial_inventory=5
)

# Solve
min_cost = solver.solve()

# Get full report
report = generate_solution_report(solver)
print(report)
```

## Project Structure

```
medical_inventory_dp/
├── src/
│   ├── cost_model.py      # Cost calculation logic
│   ├── dp_solver.py       # DP table construction
│   ├── backtracking.py    # Optimal schedule reconstruction
│   └── visualization.py   # Charts and plots
├── tests/
│   ├── test_normal.py     # Normal demand tests
│   ├── test_spike.py      # Demand spike tests
│   └── test_extreme.py    # Edge case tests
├── data/
│   └── scenarios.json     # Pre-defined scenarios
├── main.py                # CLI entry point
└── README.md
```

## Mathematical Model

### Objective Function

Minimize total cost over planning horizon:

$$\sum_{t=1}^{T} \left( c_{order} \cdot \mathbf{1}_{q_t > 0} + c_{storage} \cdot \max(0, I_t + q_t - d_t) + c_{shortage} \cdot \max(0, d_t - (I_t + q_t)) \right)$$

### DP Recurrence

$$DP(t, I) = \min_q \left[ \text{ImmediateCost}(t, I, q) + DP(t+1, I_{t+1}) \right]$$

Where: $I_{t+1} = \max(0, I + q - d_t)$

## Available Scenarios

| Scenario | Description | Periods |
|----------|-------------|---------|
| `normal` | Steady demand pattern | 7 |
| `spike` | Emergency outbreak situation | 7 |
| `high_storage_cost` | Cold chain supplies | 5 |
| `high_order_cost` | Bulk ordering preference | 5 |
| `tight_capacity` | Small warehouse | 6 |
| `zero_initial` | Emergency planning | 5 |
| `stress_long_horizon` | 30-day stress test | 30 |

## Output

### Console Output
- Scenario parameters
- Optimal order schedule
- Inventory trajectory
- Cost breakdown

### Files Generated
- `solution.json`: Full solution data
- `inventory_levels.png`: Inventory over time
- `orders_per_period.png`: Order quantities
- `cost_breakdown.png`: Cost pie chart
- `dashboard.png`: Combined visualization

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_normal.py -v
```

## License

MIT License - Free for educational and commercial use.
