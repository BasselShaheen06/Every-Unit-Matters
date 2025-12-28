class CostModel:
    """ 
    COMPLEXITY ANALYSIS:
        All methods: O(1) - constant time arithmetic operations
    """
    
    def __init__(self, c_order, c_storage, c_shortage, c_unit):
        assert c_order >= 0, "Ordering cost must be non negative"
        assert c_storage >= 0, "Storage cost must be non negative"
        assert c_shortage >= 0, "Shortage cost must be non negative"
        self.c_unit = c_unit
        self.c_order = c_order
        self.c_storage = c_storage
        self.c_shortage = c_shortage
    
    def compute_ordering_cost(self, order_quantity):
        return self.c_order + (order_quantity * self.c_unit) if order_quantity > 0 else 0.0
    
    def compute_storage_cost(self, ending_inventory):
        return self.c_storage * max(0, ending_inventory)
    
    def compute_shortage_cost(self, shortage):
        return self.c_shortage * max(0, shortage)
    
    def compute_period_cost(self, order_quantity, inventory_before, demand) :
        available = inventory_before + order_quantity
        
        if available >= demand:
            ending_inventory = available - demand
            shortage = 0
        else:
            ending_inventory = 0
            shortage = demand - available
        
        ordering = self.compute_ordering_cost(order_quantity)
        storage = self.compute_storage_cost(ending_inventory)
        shortage_cost = self.compute_shortage_cost(shortage)
        total = ordering + storage + shortage_cost
        return total, ending_inventory, shortage
    
    def to_dict(self):
        return {
            "c_order": self.c_order,
            "c_unit": self.c_unit,
            "c_storage": self.c_storage,
            "c_shortage": self.c_shortage
        }
