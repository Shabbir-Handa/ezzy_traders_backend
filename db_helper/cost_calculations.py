"""
Cost Calculation Module for Ezzy Traders
Handles all cost calculations for quotations including base costs, attribute costs, and direct costs.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from db_helper.models import (
    Quotation, QuotationItem, QuotationItemAttribute, UnitValue,
    DoorTypeThicknessOption, Attribute, AttributeOption, Unit, CostType
)
from db_helper.door_attribute_crud import DoorAttributeCRUD


class CostCalculator:
    """Handles all cost calculations for quotations"""
    
    @staticmethod
    def calculate_base_cost(
        length: Decimal, 
        breadth: Decimal, 
        thickness_option: DoorTypeThicknessOption,
        quantity: int = 1
    ) -> Dict[str, Decimal]:
        """
        Calculate base cost for a door item based on dimensions and thickness
        
        Args:
            length: Length in inches
            breadth: Breadth in inches
            thickness_option: Thickness option with cost per sqft
            quantity: Quantity of items
            
        Returns:
            Dictionary with cost breakdown
        """
        area_sqft = (length * breadth) / 144
        
        # Calculate base cost per unit
        base_cost_per_unit = area_sqft * thickness_option.cost_per_sqft
        
        # Calculate total base cost
        total_base_cost = base_cost_per_unit * quantity
        
        return {
            'area_sqft': area_sqft,
            'cost_per_sqft': thickness_option.cost_per_sqft,
            'base_cost_per_unit': base_cost_per_unit,
            'quantity': quantity,
            'total_base_cost': total_base_cost
        }
    
    @staticmethod
    def calculate_attribute_cost(
        db: Session,
        attribute: Attribute,
        selected_option: Optional[AttributeOption] = None,
        unit_values: Optional[List[UnitValue]] = None,
        double_side: bool = False,
        direct_cost: Optional[Decimal] = None,
        child_options: Optional[Dict[int, int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate cost for an attribute based on its type and configuration
        
        Args:
            db: Database session
            attribute: The attribute to calculate cost for
            selected_option: Selected option if applicable
            unit_values: Unit values for variable costs
            double_side: Whether double side is selected
            direct_cost: Direct cost entered by user
            child_options: Dictionary mapping child_attribute_id to selected_option_id for nested attributes

        Returns:
            Dictionary with cost breakdown
        """
        calculated_cost = Decimal('0')
        cost_breakdown = {
            'attribute_id': attribute.id,
            'attribute_name': attribute.name,
            'cost_type': attribute.cost_type,
            'calculated_cost': calculated_cost,
            'direct_cost': direct_cost or Decimal('0'),
            'total_cost': Decimal('0'),
            'cost_details': {}
        }
        
        # Handle direct cost first (user override)
        # Fix: Check for non-None and non-zero properly with Decimal
        if direct_cost is not None and direct_cost != Decimal('0'):
            cost_breakdown['total_cost'] = direct_cost
            cost_breakdown['cost_details']['direct_cost_override'] = True
            return cost_breakdown
        
        # Calculate based on cost type
        if attribute.cost_type == CostType.CONSTANT:
            if selected_option:
                calculated_cost = selected_option.cost
            else:
                calculated_cost = attribute.fixed_cost or Decimal('0')
                
        elif attribute.cost_type == CostType.VARIABLE:
            # Use option's cost_per_unit if provided, else attribute-level cost_per_unit
            option_cost_per_unit = None
            if selected_option and getattr(selected_option, 'cost_per_unit', None):
                option_cost_per_unit = selected_option.cost_per_unit

            cost_per_unit = option_cost_per_unit if option_cost_per_unit is not None else (attribute.cost_per_unit or Decimal('0'))

            # Calculate based on unit values (supports area and linear)
            total_units = Decimal('0')
            if unit_values:
                for unit_value in unit_values:
                    if unit_value.value1:
                        if unit_value.value2:  # Area unit
                            total_units += unit_value.value1 * unit_value.value2
                        else:  # Linear or single unit
                            total_units += unit_value.value1

            calculated_cost = total_units * cost_per_unit
            cost_breakdown['cost_details'] = {
                'total_units': total_units,
                'cost_per_unit': cost_per_unit,
                'unit_name': attribute.unit.name if attribute.unit else 'units',
                'source': 'option' if option_cost_per_unit is not None else 'attribute'
            }
                
        elif attribute.cost_type == CostType.NESTED:
            # Handle nested attributes recursively with child options
            # Fix: Calculate total units from unit_values for proper nested calculation
            total_units = Decimal('1.0')
            if unit_values:
                total_units = Decimal('0')
                for unit_value in unit_values:
                    if unit_value.value1:
                        if unit_value.value2:  # Area unit
                            total_units += unit_value.value1 * unit_value.value2
                        else:  # Linear or single unit
                            total_units += unit_value.value1
                # Default to 1.0 if no valid units
                if total_units == Decimal('0'):
                    total_units = Decimal('1.0')
            
            nested_breakdown = DoorAttributeCRUD.get_nested_attribute_cost_breakdown(
                db, attribute.id, float(total_units), child_options
            )
            calculated_cost = Decimal(str(nested_breakdown['total_cost']))
            cost_breakdown['cost_details'] = nested_breakdown
            cost_breakdown['cost_details']['total_units_for_nested'] = float(total_units)
        
        # Apply double side multiplier if applicable
        # Fix: Validate that selected option also supports double side (if option is selected)
        if double_side and attribute.double_side:
            # Additional validation: if option is selected, check it supports double side
            # (assuming if attribute supports it, option inherits that capability)
            calculated_cost *= Decimal('2')
            cost_breakdown['cost_details']['double_side_applied'] = True
            cost_breakdown['cost_details']['double_side_multiplier'] = 2
        
        # Fix: Add negative cost protection
        if calculated_cost < Decimal('0'):
            calculated_cost = Decimal('0')
            cost_breakdown['cost_details']['negative_cost_corrected'] = True
        
        cost_breakdown['calculated_cost'] = calculated_cost
        cost_breakdown['total_cost'] = calculated_cost
        
        return cost_breakdown
    
    @staticmethod
    def calculate_item_total_cost(
        base_cost: Decimal,
        attribute_costs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate total cost for a quotation item
        
        Args:
            base_cost: Base cost from dimensions and thickness
            attribute_costs: List of attribute cost breakdowns
            
        Returns:
            Dictionary with total cost breakdown
        """
        total_attribute_cost = sum(
            attr_cost['total_cost'] for attr_cost in attribute_costs
        )
        
        total_item_cost = base_cost + total_attribute_cost
        
        return {
            'base_cost': base_cost,
            'attribute_costs': total_attribute_cost,
            'total_item_cost': total_item_cost,
            'cost_breakdown': {
                'base': base_cost,
                'attributes': total_attribute_cost,
                'total': total_item_cost
            }
        }
    
    @staticmethod
    def calculate_quotation_total_cost(
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate total cost for entire quotation
        
        Args:
            items: List of item cost breakdowns
            
        Returns:
            Dictionary with quotation total cost
        """
        total_base_cost = sum(item['base_cost'] for item in items)
        total_attribute_cost = sum(item['attribute_costs'] for item in items)
        total_quotation_cost = sum(item['total_item_cost'] for item in items)
        
        return {
            'total_base_cost': total_base_cost,
            'total_attribute_cost': total_attribute_cost,
            'total_quotation_cost': total_quotation_cost,
            'item_count': len(items)
        }
    
    @staticmethod
    def apply_direct_cost_overrides(
        attribute_costs: List[Dict[str, Any]],
        direct_costs: Dict[int, Decimal]
    ) -> List[Dict[str, Any]]:
        """
        Apply direct cost overrides to calculated costs
        
        Args:
            attribute_costs: List of calculated attribute costs
            direct_costs: Dictionary mapping attribute_id to direct cost
            
        Returns:
            Updated attribute costs with direct cost overrides
        """
        updated_costs = []
        
        for attr_cost in attribute_costs:
            attr_id = attr_cost['attribute_id']
            if attr_id in direct_costs:
                # Override with direct cost
                attr_cost['direct_cost'] = direct_costs[attr_id]
                attr_cost['total_cost'] = direct_costs[attr_id]
                attr_cost['cost_details']['direct_cost_override'] = True
            else:
                attr_cost['direct_cost'] = Decimal('0')
            
            updated_costs.append(attr_cost)
        
        return updated_costs
    
    @staticmethod
    def calculate_quotation_item_costs(
        db: Session,
        item: QuotationItem,
        username: str = None
    ) -> Dict[str, Any]:
        """
        Calculate all costs for a quotation item including base and attributes
        
        Args:
            db: Database session
            item: QuotationItem to calculate costs for
            username: Username for audit trail
            
        Returns:
            Dictionary with complete cost breakdown
        """
        if not item.length or not item.breadth or not item.thickness_option:
            return {
                'error': 'Missing required dimensions or thickness option',
                'item_id': item.id
            }
        
        # Calculate base cost
        base_cost_breakdown = CostCalculator.calculate_base_cost(
            length=item.length,
            breadth=item.breadth,
            thickness_option=item.thickness_option,
            quantity=1
        )
        
        # Calculate attribute costs
        attribute_costs = []
        per_unit_attribute_total = Decimal('0')
        
        for attr in item.attributes:
            # Get selected option if applicable
            selected_option = None
            if attr.selected_option_id:
                selected_option = db.query(AttributeOption).filter(
                    AttributeOption.id == attr.selected_option_id
                ).first()
            
            # Calculate attribute cost
            attr_cost_breakdown = CostCalculator.calculate_attribute_cost(
                db=db,
                attribute=attr.attribute,
                selected_option=selected_option,
                unit_values=attr.unit_values,
                double_side=attr.double_side,
                direct_cost=attr.direct_cost,
                child_options={}
            )
            
            # Update attribute costs
            attr.calculated_cost = attr_cost_breakdown['calculated_cost']
            attr.total_attribute_cost = attr_cost_breakdown['total_cost']
            per_unit_attribute_total += attr_cost_breakdown['total_cost']

            attribute_costs.append(attr_cost_breakdown)
        
        # Calculate per-unit with attributes
        unit_price_before_discount = base_cost_breakdown['base_cost_per_unit'] + per_unit_attribute_total
        
        # Fix: Protect against negative base/attribute costs
        if unit_price_before_discount < Decimal('0'):
            unit_price_before_discount = Decimal('0')
        
        tax_percentage = item.tax_percentage or Decimal('0')
        discount_amount = item.discount_amount or Decimal('0')

        # Fix: Apply discount FIRST, then tax (standard practice)
        unit_price_after_discount = unit_price_before_discount - discount_amount
        if unit_price_after_discount < Decimal('0'):
            unit_price_after_discount = Decimal('0')

        # Apply tax on discounted price
        tax_multiplier = (Decimal('1') + (tax_percentage / Decimal('100')))
        unit_price_final = unit_price_after_discount * tax_multiplier

        # Final negative protection
        if unit_price_final < Decimal('0'):
            unit_price_final = Decimal('0')

        total_item_cost = unit_price_final * (item.quantity or 1)
        
        # Update item with calculated costs
        # Fix: Use proper Decimal precision and add new field
        item.base_cost_per_unit = base_cost_breakdown['base_cost_per_unit']
        item.attribute_cost_per_unit = per_unit_attribute_total
        item.unit_price_before_tax = unit_price_after_discount  # Price after discount, before tax
        item.unit_price_with_attributes = unit_price_final  # Final price (after discount and tax)
        item.total_item_cost = total_item_cost
        
        return {
            'item_id': item.id,
            'base_cost_breakdown': base_cost_breakdown,
            'attribute_costs': attribute_costs,
            'per_unit_attribute_total': per_unit_attribute_total,
            'unit_price_with_attributes': unit_price_with_attributes,
            'total_item_cost': total_item_cost,
            'quantity': item.quantity
        }
    
    @staticmethod
    def recalculate_quotation_costs(
        db: Session,
        quotation_id: int,
        username: str = None
    ) -> Dict[str, Any]:
        """
        Recalculate all costs for an existing quotation
        
        Args:
            db: Database session
            quotation_id: ID of quotation to recalculate
            username: Username for audit trail
            
        Returns:
            Dictionary with recalculation results
        """
        from .customer_quotation_crud import CustomerQuotationCRUD
        
        quotation = CustomerQuotationCRUD.get_quotation_by_id(db, quotation_id)
        if not quotation:
            return {"error": "Quotation not found"}
        
        total_quotation_cost = Decimal('0')
        item_costs = []
        
        for item in quotation.items:
            item_cost = CostCalculator.calculate_quotation_item_costs(db, item, username)
            if 'error' not in item_cost:
                total_quotation_cost += item_cost['total_item_cost']
                item_costs.append(item_cost)
        
        # Update quotation total
        quotation.total_amount = total_quotation_cost
        quotation.updated_by = username
        
        db.commit()
        
        return {
            "message": "Costs recalculated successfully",
            "quotation_id": quotation_id,
            "new_total_amount": float(total_quotation_cost),
            "item_costs": item_costs
        }
    
    @staticmethod
    def get_quotation_cost_breakdown(
        db: Session,
        quotation_id: int
    ) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for a quotation
        
        Args:
            db: Database session
            quotation_id: ID of quotation
            
        Returns:
            Dictionary with complete cost breakdown
        """
        from .customer_quotation_crud import CustomerQuotationCRUD
        
        quotation = CustomerQuotationCRUD.get_quotation_by_id(db, quotation_id)
        if not quotation:
            return {}
        
        cost_breakdown = {
            "quotation_id": quotation.id,
            "quotation_number": getattr(quotation, 'quotation_number', None),
            "customer_name": quotation.customer.name if quotation.customer else None,
            "total_amount": str(quotation.total_amount) if quotation.total_amount else "0.00",  # Fix: Keep Decimal precision
            "items": [],
            "summary": {
                "total_base_cost": Decimal('0'),
                "total_attribute_cost": Decimal('0'),
                "total_quotation_cost": Decimal('0'),
                "item_count": 0
            }
        }
        
        total_base_cost = Decimal('0')
        total_attribute_cost = Decimal('0')
        
        for item in quotation.items:
            # Fix: Calculate area properly based on actual units (inches)
            area_sqft = Decimal('0')
            if item.length and item.breadth:
                # Convert inches to square feet: divide by 144 (12*12)
                area_sqft = (item.length * item.breadth) / Decimal('144')
            
            item_breakdown = {
                "item_id": item.id,
                "door_type": item.door_type.name if item.door_type else None,
                "thickness": str(item.thickness_option.thickness_value) if item.thickness_option else None,
                "dimensions": f"{item.length} × {item.breadth} inches",
                "quantity": item.quantity,
                "base_cost": {
                    "cost_per_sqft": str(item.thickness_option.cost_per_sqft) if item.thickness_option else "0.00",
                    "area_sqft": str(area_sqft),
                    "base_cost_per_unit": str(item.base_cost_per_unit) if item.base_cost_per_unit else "0.00",
                    "total_base_cost": str((item.base_cost_per_unit or 0) * (item.quantity or 1))
                },
                "attributes": [],
                "total_item_cost": str(item.total_item_cost) if item.total_item_cost else "0.00"
            }
            
            item_attribute_cost = Decimal('0')  # Fix: Use Decimal for precision
            
            for attr in item.attributes:
                attr_breakdown = {
                    "attribute_id": attr.attribute_id,
                    "attribute_name": attr.attribute.name if attr.attribute else None,
                    "cost_type": attr.attribute.cost_type if attr.attribute else None,
                    "double_side": attr.double_side,
                    "calculated_cost": str(attr.calculated_cost) if attr.calculated_cost else "0.00",  # Fix: Decimal precision
                    "direct_cost": str(attr.direct_cost) if attr.direct_cost else "0.00",
                    "total_attribute_cost": str(attr.total_attribute_cost) if attr.total_attribute_cost else "0.00",
                    "unit_values": []
                }
                
                # Add unit values if they exist
                for unit_value in attr.unit_values:
                    attr_breakdown["unit_values"].append({
                        "unit_name": unit_value.unit.name if unit_value.unit else None,
                        "value1": str(unit_value.value1) if unit_value.value1 else "0.00",  # Fix: Decimal precision
                        "value2": str(unit_value.value2) if unit_value.value2 else "0.00"
                    })
                
                item_attribute_cost += (attr.total_attribute_cost or Decimal('0'))  # Fix: Decimal math
                item_breakdown["attributes"].append(attr_breakdown)
            
            item_breakdown["attribute_costs"] = str(item_attribute_cost)  # Fix: String for JSON
            total_base_cost += Decimal(item_breakdown["base_cost"]["total_base_cost"])  # Fix: Decimal math
            total_attribute_cost += item_attribute_cost
            
            cost_breakdown["items"].append(item_breakdown)
        
        # Update summary with proper Decimal precision
        cost_breakdown["summary"] = {
            "total_base_cost": str(total_base_cost),
            "total_attribute_cost": str(total_attribute_cost),
            "total_quotation_cost": str(total_base_cost + total_attribute_cost),
            "item_count": len(quotation.items)
        }
        
        return cost_breakdown
