# All costs are in USD
# Time unit: 1 period = 1 month
# Inventory unit: single medical supply unit (e.g., box of masks)

# Planning horizon
T = 12  # 12 months (1 year planning)

# Regular ordering costs
C_ORDER_FIXED = 100  # Fixed cost per order (shipping, admin, processing)
C_UNIT = 10          # Cost per unit of supply (e.g., $10 per box of masks)

# Storage costs
C_STORAGE = 2        # Storage cost per unit per month (warehouse, handling)

# Emergency ordering costs (when shortage occurs)
C_EMERGENCY_FIXED = 150   # Emergency shipping fee (50% higher than regular)
C_EMERGENCY_UNIT = 60     # Emergency unit cost (6x regular price - premium supplier)

# Capacity
MAX_STORAGE = 500    # Maximum warehouse capacity (units)

#Cost functions 
def normalOrder(n):
    if n == 0:
        return 0
    return C_ORDER_FIXED + C_UNIT * n


def emergencyOrder(n):
    if n == 0:
        return 0
    return C_EMERGENCY_FIXED + C_EMERGENCY_UNIT * n

def storage(n):
    return C_STORAGE*n

def OptimalCost(demand):
    dp = [[float('inf')] * (MAX_STORAGE + 1) for _ in range(T + 1)]
    # Base case: at time T, no cost regardless of inventory
    for I in range(MAX_STORAGE + 1):
        dp[T][I] = 0  # No cost at time 12
    # Fill dp table backwards
    for t in range(T - 1, -1, -1):
        for I in range(MAX_STORAGE + 1):  # current inventory
            for q in range(MAX_STORAGE - I + 1):  # feasible order quantities
                available = I + q
                shortage = max(0, demand[t] - available)
                remaining_inventory = max(0, available - demand[t])
                cost = normalOrder(q) + emergencyOrder(shortage) + storage(remaining_inventory) + dp[t + 1][remaining_inventory]
                if cost < dp[t][I]:
                    dp[t][I] = cost
    return dp[0][0]  # Minimum cost starting with 0 inventory at time 0

print(OptimalCost([50, 80, 60, 70, 90, 100, 110, 80, 60, 70, 90, 100]))