# Time horizon
T = 12  # Number of periods (months)

# Default cost parameters
DEFAULT_ORDER_FIXED = 100
DEFAULT_UNIT_COST = 10
DEFAULT_STORAGE_COST = 2
DEFAULT_EMERGENCY_FIXED = 150
DEFAULT_EMERGENCY_UNIT = 60

# Default operational parameters
DEFAULT_MAX_STORAGE = 500
DEFAULT_INITIAL_INVENTORY = 0
DEFAULT_DEMAND = "100,20,100,20,100,20,100,20,100,20,100,20"

# UI Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 850
TABLE_HEIGHT = 12

# Column definitions
SCHEDULE_COLUMNS = ["Period", "Start", "Order", "Demand", "Emergency", "End", "Cost"]
COMPARISON_COLUMNS = ["Period", "Order", "Emergency", "Cost"]