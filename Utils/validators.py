"""
Input validation and error handling for Medical Inventory Optimization.
"""

from typing import List, Tuple, Optional
from Utils.constant import T


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Validates all user inputs for the inventory optimization system."""
    
    @staticmethod
    def validate_demand(demand_str: str) -> Tuple[bool, Optional[List[int]], Optional[str]]:
        """
        Validate demand input string.
        
        Args:
            demand_str: Comma-separated demand values
            
        Returns:
            (is_valid, demand_list, error_message)
        """
        try:
            # Check if empty
            if not demand_str or demand_str.strip() == "":
                return False, None, "Demand cannot be empty"
            
            # Parse values
            demand = [int(x.strip()) for x in demand_str.split(",")]
            
            # Check length
            if len(demand) != T:
                return False, None, f"Demand must have exactly {T} values, got {len(demand)}"
            
            # Check for negative values
            if any(d < 0 for d in demand):
                return False, None, "Demand values cannot be negative"
            
            # Check for unreasonably large values
            if any(d > 100000 for d in demand):
                return False, None, "Demand values seem unreasonably large (max: 100,000)"
            
            # Check if all zeros
            if all(d == 0 for d in demand):
                return False, None, "At least one demand value must be positive"
            
            return True, demand, None
            
        except ValueError as e:
            return False, None, f"Invalid demand format. Use comma-separated integers (e.g., 100,20,100)"
        except Exception as e:
            return False, None, f"Unexpected error parsing demand: {str(e)}"
    
    @staticmethod
    def validate_initial_inventory(value_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validate initial inventory input.
        
        Returns:
            (is_valid, value, error_message)
        """
        try:
            if not value_str or value_str.strip() == "":
                return False, None, "Initial inventory cannot be empty"
            
            value = int(value_str.strip())
            
            if value < 0:
                return False, None, "Initial inventory cannot be negative"
            
            if value > 100000:
                return False, None, "Initial inventory seems unreasonably large (max: 100,000)"
            
            return True, value, None
            
        except ValueError:
            return False, None, "Initial inventory must be a valid integer"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def validate_cost_parameter(value_str: str, param_name: str, 
                                allow_zero: bool = False) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Validate cost parameter input.
        
        Args:
            value_str: String value to validate
            param_name: Name of parameter for error messages
            allow_zero: Whether zero is a valid value
            
        Returns:
            (is_valid, value, error_message)
        """
        try:
            if not value_str or value_str.strip() == "":
                return False, None, f"{param_name} cannot be empty"
            
            value = float(value_str.strip())
            
            if not allow_zero and value <= 0:
                return False, None, f"{param_name} must be positive"
            
            if allow_zero and value < 0:
                return False, None, f"{param_name} cannot be negative"
            
            if value > 1000000:
                return False, None, f"{param_name} seems unreasonably large (max: 1,000,000)"
            
            return True, value, None
            
        except ValueError:
            return False, None, f"{param_name} must be a valid number"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def validate_max_storage(value_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validate maximum storage capacity.
        
        Returns:
            (is_valid, value, error_message)
        """
        try:
            if not value_str or value_str.strip() == "":
                return False, None, "Max storage capacity cannot be empty"
            
            value = int(value_str.strip())
            
            if value <= 0:
                return False, None, "Max storage capacity must be positive"
            
            if value < 10:
                return False, None, "Max storage capacity too small (minimum: 10)"
            
            if value > 100000:
                return False, None, "Max storage capacity seems unreasonably large (max: 100,000)"
            
            return True, value, None
            
        except ValueError:
            return False, None, "Max storage capacity must be a valid integer"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def validate_all_inputs(demand_str: str, init_inv_str: str,
                           c_order_fixed_str: str, c_unit_str: str,
                           c_storage_str: str, c_emergency_fixed_str: str,
                           c_emergency_unit_str: str, max_storage_str: str) -> Tuple[bool, dict, List[str]]:
        """
        Validate all inputs at once.
        
        Returns:
            (is_valid, values_dict, error_messages_list)
        """
        errors = []
        values = {}
        
        # Validate demand
        valid, demand, error = InputValidator.validate_demand(demand_str)
        if not valid:
            errors.append(f"❌ Demand: {error}")
        else:
            values['demand'] = demand
        
        # Validate initial inventory
        valid, init_inv, error = InputValidator.validate_initial_inventory(init_inv_str)
        if not valid:
            errors.append(f"❌ Initial Inventory: {error}")
        else:
            values['initial_inventory'] = init_inv
        
        # Validate max storage
        valid, max_storage, error = InputValidator.validate_max_storage(max_storage_str)
        if not valid:
            errors.append(f"❌ Max Storage: {error}")
        else:
            values['max_storage'] = max_storage
        
        # Validate order fixed cost
        valid, c_order_fixed, error = InputValidator.validate_cost_parameter(
            c_order_fixed_str, "Ordering Fixed Cost", allow_zero=True
        )
        if not valid:
            errors.append(f"❌ Ordering Fixed Cost: {error}")
        else:
            values['c_order_fixed'] = c_order_fixed
        
        # Validate unit cost
        valid, c_unit, error = InputValidator.validate_cost_parameter(
            c_unit_str, "Ordering Unit Cost", allow_zero=True
        )
        if not valid:
            errors.append(f"❌ Ordering Unit Cost: {error}")
        else:
            values['c_unit'] = c_unit
        
        # Validate storage cost
        valid, c_storage, error = InputValidator.validate_cost_parameter(
            c_storage_str, "Storage Cost", allow_zero=True
        )
        if not valid:
            errors.append(f"❌ Storage Cost: {error}")
        else:
            values['c_storage'] = c_storage
        
        # Validate emergency fixed cost
        valid, c_emergency_fixed, error = InputValidator.validate_cost_parameter(
            c_emergency_fixed_str, "Emergency Fixed Cost", allow_zero=True
        )
        if not valid:
            errors.append(f"❌ Emergency Fixed Cost: {error}")
        else:
            values['c_emergency_fixed'] = c_emergency_fixed
        
        # Validate emergency unit cost
        valid, c_emergency_unit, error = InputValidator.validate_cost_parameter(
            c_emergency_unit_str, "Emergency Unit Cost", allow_zero=False
        )
        if not valid:
            errors.append(f"❌ Emergency Unit Cost: {error}")
        else:
            values['c_emergency_unit'] = c_emergency_unit
        
        # Cross-validation checks
        if len(errors) == 0:
            # Check if initial inventory exceeds max storage
            if values['initial_inventory'] > values['max_storage']:
                errors.append(f"❌ Initial inventory ({values['initial_inventory']}) cannot exceed max storage ({values['max_storage']})")
            
            # Check if emergency costs make sense
            if values['c_emergency_unit'] < values['c_unit']:
                errors.append(f"⚠️ Warning: Emergency unit cost ({values['c_emergency_unit']}) is less than regular unit cost ({values['c_unit']}). This is unusual.")
            
            # Check if max storage can handle max demand
            max_demand = max(values['demand'])
            if values['max_storage'] < max_demand:
                errors.append(f"⚠️ Warning: Max storage ({values['max_storage']}) is less than peak demand ({max_demand}). Emergency orders will be frequent.")
        
        return len(errors) == 0, values, errors
    
    @staticmethod
    def validate_solver_state(solver) -> Tuple[bool, Optional[str]]:
        """
        Validate that solver has been run successfully.
        
        Returns:
            (is_valid, error_message)
        """
        if solver is None:
            return False, "Solver has not been initialized. Please run optimization first."
        
        if solver.dp is None:
            return False, "DP table not computed. Please run optimization first."
        
        if solver.decision is None:
            return False, "Decision table not computed. Please run optimization first."
        
        return True, None


class SolverErrorHandler:
    """Handles errors during solver execution."""
    
    @staticmethod
    def handle_solver_error(error: Exception) -> str:
        """
        Convert solver exceptions into user-friendly error messages.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        if "memory" in error_msg.lower() or isinstance(error, MemoryError):
            return ("Memory error: Problem size too large. "
                   "Try reducing max storage capacity or number of periods.")
        
        if "overflow" in error_msg.lower():
            return ("Numerical overflow: Cost values too large. "
                   "Check your cost parameters for unreasonable values.")
        
        if isinstance(error, IndexError):
            return ("Index error in solver: This might indicate invalid demand or storage values. "
                   "Please check your inputs.")
        
        if isinstance(error, ValueError):
            return f"Value error in solver: {error_msg}"
        
        if isinstance(error, ZeroDivisionError):
            return "Division by zero error: Check for zero or negative values in inputs."
        
        # Generic error
        return f"Solver error ({error_type}): {error_msg}\n\nPlease check your inputs and try again."


# Edge case test data
EDGE_CASE_TESTS = {
    "zero_initial": {
        "demand": "10,20,15,25,30,10,20,15,25,30,10,20",
        "initial_inventory": "0",
        "description": "Starting with zero inventory"
    },
    "high_initial": {
        "demand": "10,20,15,25,30,10,20,15,25,30,10,20",
        "initial_inventory": "200",
        "description": "Starting with high inventory"
    },
    "constant_demand": {
        "demand": "50,50,50,50,50,50,50,50,50,50,50,50",
        "initial_inventory": "0",
        "description": "Constant demand every period"
    },
    "fluctuating_demand": {
        "demand": "100,20,100,20,100,20,100,20,100,20,100,20",
        "initial_inventory": "0",
        "description": "Highly fluctuating demand (Original)"
    },
    "increasing_demand": {
        "demand": "10,20,30,40,50,60,70,80,90,100,110,120",
        "initial_inventory": "0",
        "description": "Steadily increasing demand"
    },
    "decreasing_demand": {
        "demand": "120,110,100,90,80,70,60,50,40,30,20,10",
        "initial_inventory": "0",
        "description": "Steadily decreasing demand"
    },
    "single_peak": {
        "demand": "10,20,30,40,100,40,30,20,10,10,10,10",
        "initial_inventory": "0",
        "description": "Single demand peak"
    },
    "zero_costs": {
        "demand": "50,50,50,50,50,50,50,50,50,50,50,50",
        "initial_inventory": "0",
        "c_order_fixed": "0",
        "c_unit": "0",
        "c_storage": "0",
        "description": "All costs zero (edge case)"
    },
    "high_storage_cost": {
        "demand": "50,50,50,50,50,50,50,50,50,50,50,50",
        "initial_inventory": "0",
        "c_storage": "50",
        "description": "Very high storage cost"
    },
    "low_emergency_cost": {
        "demand": "100,20,100,20,100,20,100,20,100,20,100,20",
        "initial_inventory": "0",
        "c_emergency_fixed": "10",
        "c_emergency_unit": "15",
        "description": "Emergency cheaper than storage"
    }
}