class CostModel:
    """ 
        c_order: Fixed cost per order placed
        c_unit: Cost per unit ordered
        c_storage: Holding cost per unit per period
        c_shortage: Shortage penalty per unit
    """
    
    def __init__(self, c_order, c_storage, c_shortage, c_unit):
        assert c_order >= 0, "Ordering cost must be non negative"
        assert c_storage >= 0, "Storage cost must be non negative"
        assert c_shortage >= 0, "Shortage cost must be non negative"
        self.c_unit = c_unit
        self.c_order = c_order
        self.c_storage = c_storage
        self.c_shortage = c_shortage
    
    def compute_ordering_cost(self, order_quantity: int) -> float:
        """
        Compute fixed ordering cost.
        
        Args:
            order_quantity: Amount ordered (q)
            
        Returns:
            c_order if q > 0, else 0
        """
        return self.c_order + (order_quantity * self.c_unit) if order_quantity > 0 else 0.0
    
    def compute_storage_cost(self, ending_inventory: int) -> float:
        """
        Compute holding cost for ending inventory.
        
        Args:
            ending_inventory: Inventory at end of period (after demand satisfied)
            
        Returns:
            c_storage * max(0, ending_inventory)
        """
        return self.c_storage * max(0, ending_inventory)
    
    def compute_shortage_cost(self, shortage: int) -> float:
        """
        Compute shortage penalty.
        
        Args:
            shortage: Unmet demand units
            
        Returns:
            c_shortage * max(0, shortage)
        """
        return self.c_shortage * max(0, shortage)
    
    def compute_period_cost(self, order_quantity: int, inventory_before: int, 
                            demand: int) -> tuple[float, int, int]:
        """
        Compute total cost for a single period.
        
        Args:
            order_quantity: Units ordered
            inventory_before: Inventory at start of period
            demand: Demand to satisfy
            
        Returns:
            Tuple of (total_cost, ending_inventory, shortage)
        """
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
    
    def to_dict(self) -> dict:
        """Return cost parameters as dictionary."""
        return {
            "c_order": self.c_order,
            "c_unit": self.c_unit,
            "c_storage": self.c_storage,
            "c_shortage": self.c_shortage
        }
