import os
from typing import Optional

# Try to import matplotlib, but handle if not available
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def check_matplotlib():
    """Check if matplotlib is available."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install with: pip install matplotlib"
        )


def plot_inventory_vs_time(inventory_levels: list[int], demand: list[int],
                            max_storage: int, output_path: Optional[str] = None,
                            title: str = "Inventory Levels Over Time"):

    check_matplotlib()
    
    T = len(inventory_levels)
    periods = list(range(1, T + 1))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot inventory levels
    ax.plot(periods, inventory_levels, 'b-o', linewidth=2, markersize=8, 
            label='Ending Inventory', color='#2196F3')
    
    # Plot demand for reference
    ax.plot(periods, demand, 'r--s', linewidth=2, markersize=6,
            label='Demand', color='#F44336', alpha=0.7)
    
    # Max storage line
    ax.axhline(y=max_storage, color='#4CAF50', linestyle=':', 
               linewidth=2, label=f'Max Storage ({max_storage})')
    
    # Zero line
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    
    ax.set_xlabel('Period', fontsize=12)
    ax.set_ylabel('Units', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(periods)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()
    return fig


def plot_orders_per_period(schedule: list[int], demand: list[int],
                           output_path: Optional[str] = None,
                           title: str = "Orders vs Demand per Period"):
    """
    Plot order quantities as a bar chart.
    """
    check_matplotlib()
    
    T = len(schedule)
    periods = list(range(1, T + 1))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    width = 0.35
    x = range(len(periods))
    
    bars1 = ax.bar([i - width/2 for i in x], schedule, width, 
                   label='Orders', color='#2196F3', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], demand, width,
                   label='Demand', color='#F44336', alpha=0.8)
    
    ax.set_xlabel('Period', fontsize=12)
    ax.set_ylabel('Units', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(periods)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()
    return fig


def plot_cost_breakdown(cost_breakdown: dict, output_path: Optional[str] = None,
                        title: str = "Cost Breakdown"):
    """
    Plot cost breakdown as a pie chart.
    """
    check_matplotlib()
    
    labels = ['Ordering', 'Storage', 'Shortage']
    values = [
        cost_breakdown.get('ordering', 0),
        cost_breakdown.get('storage', 0),
        cost_breakdown.get('shortage', 0)
    ]
    colors = ['#2196F3', '#4CAF50', '#F44336']
    
    # Filter out zero values
    non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    
    if not non_zero:
        print("No costs to display")
        return None
    
    labels, values, colors = zip(*non_zero)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Simple autopct without complex indexing
    total = sum(values)
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors,
        autopct='%1.1f%%',
        startangle=90, explode=[0.02] * len(values)
    )
    
    ax.set_title(f"{title}\\nTotal: ${total:.0f}", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()
    return fig


def plot_combined_dashboard(solution: dict, output_path: Optional[str] = None,
                            title: str = "Inventory Optimization Dashboard"):
    """
    Create a combined dashboard with all visualizations.
    """
    check_matplotlib()
    
    schedule = solution['order_schedule']
    inventory = solution['inventory_levels']
    demand = solution['parameters']['demand']
    max_storage = solution['parameters']['max_storage']
    cost_breakdown = solution['cost_breakdown']
    shortages = solution.get('shortages', [])
    
    T = len(schedule)
    periods = list(range(1, T + 1))
    
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Inventory & Demand over time (top left)
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(periods, inventory, 'b-o', linewidth=2, markersize=8,
             label='Ending Inventory', color='#2196F3')
    ax1.plot(periods, demand, 'r--s', linewidth=2, markersize=6,
             label='Demand', color='#F44336', alpha=0.7)
    ax1.axhline(y=max_storage, color='#4CAF50', linestyle=':',
                linewidth=2, label=f'Max Storage')
    ax1.set_xlabel('Period')
    ax1.set_ylabel('Units')
    ax1.set_title('Inventory vs Demand', fontweight='bold')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(periods)
    
    # 2. Orders bar chart (top right)
    ax2 = fig.add_subplot(2, 2, 2)
    width = 0.35
    x = range(len(periods))
    ax2.bar([i - width/2 for i in x], schedule, width,
            label='Orders', color='#2196F3', alpha=0.8)
    ax2.bar([i + width/2 for i in x], demand, width,
            label='Demand', color='#F44336', alpha=0.8)
    ax2.set_xlabel('Period')
    ax2.set_ylabel('Units')
    ax2.set_title('Orders vs Demand', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(periods)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Cost breakdown pie (bottom left)
    ax3 = fig.add_subplot(2, 2, 3)
    labels = ['Ordering', 'Storage', 'Shortage']
    values = [cost_breakdown['ordering'], cost_breakdown['storage'], 
              cost_breakdown['shortage']]
    colors = ['#2196F3', '#4CAF50', '#F44336']
    non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    
    if non_zero:
        labels, values, colors = zip(*non_zero)
        ax3.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90)
    ax3.set_title(f'Cost Breakdown (Total: ${cost_breakdown["total"]:.0f})', 
                  fontweight='bold')
    
    # 4. Summary table (bottom right)
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    
    summary_text = f"""
    OPTIMIZATION SUMMARY
    {'='*40}
    
    Planning Horizon: {T} periods
    Initial Inventory: {solution['parameters']['initial_inventory']} units
    Max Storage: {max_storage} units
    
    RESULTS
    {'='*40}
    Total Orders Placed: {sum(1 for q in schedule if q > 0)}
    Total Units Ordered: {sum(schedule)}
    Total Demand: {sum(demand)}
    Total Shortages: {sum(shortages)}
    
    COSTS
    {'='*40}
    Ordering Cost: ${cost_breakdown['ordering']:.2f}
    Storage Cost: ${cost_breakdown['storage']:.2f}
    Shortage Cost: ${cost_breakdown['shortage']:.2f}
    
    TOTAL COST: ${cost_breakdown['total']:.2f}
    """
    
    ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment='center',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()
    return fig


def plot_decision_table(solution: dict, output_path=None,
                        title: str = "Decision Table"):
    """
    Create a table image showing decisions per period.
    """
    check_matplotlib()
    
    schedule = solution['order_schedule']
    inventory = solution['inventory_levels']
    demand = solution['parameters']['demand']
    shortages = solution.get('shortages', [0] * len(schedule))
    
    T = len(schedule)
    
    # Prepare table data
    headers = ['Period', 'Demand', 'Order', 'Inventory', 'Shortage']
    data = []
    for t in range(T):
        data.append([t+1, demand[t], schedule[t], inventory[t], shortages[t]])
    
    fig, ax = plt.subplots(figsize=(10, max(4, T * 0.5 + 2)))
    ax.axis('off')
    
    table = ax.table(
        cellText=data,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        colColours=['#4CAF50'] * 5
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.5)
    
    # Style header
    for i in range(len(headers)):
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()
    return fig


def plot_cost_table(solution: dict, output_path=None,
                    title: str = "Cost Table Per Period"):
    """
    Create a table image showing costs per period.
    """
    check_matplotlib()
    
    schedule = solution['order_schedule']
    inventory = solution['inventory_levels']
    demand = solution['parameters']['demand']
    shortages = solution.get('shortages', [0] * len(schedule))
    costs = solution['parameters']['costs']
    
    T = len(schedule)
    c_order = costs['c_order']
    c_unit = costs.get('c_unit', 0)
    c_storage = costs['c_storage']
    c_shortage = costs['c_shortage']
    
    # Calculate costs per period
    headers = ['Period', 'Order Cost', 'Storage Cost', 'Shortage Cost', 'Total']
    data = []
    for t in range(T):
        q = schedule[t]
        order_cost = (c_order + q * c_unit) if q > 0 else 0
        storage_cost = inventory[t] * c_storage
        shortage_cost = shortages[t] * c_shortage
        total = order_cost + storage_cost + shortage_cost
        data.append([t+1, f"${order_cost:.0f}", f"${storage_cost:.0f}", 
                    f"${shortage_cost:.0f}", f"${total:.0f}"])
    
    # Add totals row
    total_order = sum((c_order + schedule[t] * c_unit) if schedule[t] > 0 else 0 for t in range(T))
    total_storage = sum(inventory[t] * c_storage for t in range(T))
    total_shortage = sum(shortages[t] * c_shortage for t in range(T))
    grand_total = total_order + total_storage + total_shortage
    data.append(['TOTAL', f"${total_order:.0f}", f"${total_storage:.0f}",
                f"${total_shortage:.0f}", f"${grand_total:.0f}"])
    
    fig, ax = plt.subplots(figsize=(12, max(4, (T+1) * 0.5 + 2)))
    ax.axis('off')
    
    table = ax.table(
        cellText=data,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        colColours=['#2196F3'] * 5
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.5)
    
    # Style header
    for i in range(len(headers)):
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style totals row
    for i in range(len(headers)):
        table[(T+1, i)].set_text_props(weight='bold')
        table[(T+1, i)].set_facecolor('#FFE082')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    plt.close()
    return fig


def save_all_plots(solution: dict, output_dir: str = "output"):
    """
    Generate and save all visualization plots.
    
    Args:
        solution: Full solution dictionary
        output_dir: Directory to save plots
    """
    check_matplotlib()
    
    os.makedirs(output_dir, exist_ok=True)
    
    schedule = solution['order_schedule']
    inventory = solution['inventory_levels']
    demand = solution['parameters']['demand']
    max_storage = solution['parameters']['max_storage']
    cost_breakdown = solution['cost_breakdown']
    
    # Generate individual plots
    plot_inventory_vs_time(
        inventory, demand, max_storage,
        os.path.join(output_dir, 'inventory_levels.png')
    )
    
    plot_orders_per_period(
        schedule, demand,
        os.path.join(output_dir, 'orders_per_period.png')
    )
    
    plot_cost_breakdown(
        cost_breakdown,
        os.path.join(output_dir, 'cost_breakdown.png')
    )
    
    plot_combined_dashboard(
        solution,
        os.path.join(output_dir, 'dashboard.png')
    )
    
    print(f"\nAll plots saved to: {output_dir}/")
