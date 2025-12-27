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
    return C_ORDER_FIXED + C_UNIT * n


def emergencyOrder(n):
    return C_EMERGENCY_FIXED + C_EMERGENCY_UNIT * n

def storage(n):
    return C_STORAGE*n
