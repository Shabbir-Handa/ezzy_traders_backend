"""
Cost Analysis Router
Provides endpoints for cost analysis and breakdowns
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from dependencies import get_db
from db_helper.customer_quotation_crud import CustomerQuotationCRUD
from db_helper.cost_calculations import CostCalculator

router = APIRouter(prefix="/cost-analysis", tags=["Cost Analysis"])


@router.get("/quotation/{quotation_id}/breakdown")
async def get_quotation_cost_breakdown(
    quotation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed cost breakdown for a specific quotation
    """
    breakdown = CustomerQuotationCRUD.get_quotation_cost_breakdown(db, quotation_id)
    
    if not breakdown:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    return breakdown


@router.post("/quotation/{quotation_id}/recalculate")
async def recalculate_quotation_costs(
    quotation_id: int,
    username: str = "system",  # In real app, get from auth
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Recalculate all costs for a quotation
    Useful when underlying costs change
    """
    result = CustomerQuotationCRUD.recalculate_quotation_costs(
        db, quotation_id, username
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/quotation/{quotation_id}/summary")
async def get_quotation_cost_summary(
    quotation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get cost summary for a quotation
    """
    breakdown = CustomerQuotationCRUD.get_quotation_cost_breakdown(db, quotation_id)
    
    if not breakdown:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Extract summary information
    summary = {
        "quotation_id": breakdown["quotation_id"],
        "customer_name": breakdown["customer_name"],
        "total_amount": breakdown["total_amount"],
        "cost_breakdown": breakdown["summary"],
        "item_count": breakdown["summary"]["item_count"]
    }
    
    return summary


@router.get("/quotation/{quotation_id}/item/{item_id}/costs")
async def get_item_cost_details(
    quotation_id: int,
    item_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed cost breakdown for a specific item in a quotation
    """
    breakdown = CustomerQuotationCRUD.get_quotation_cost_breakdown(db, quotation_id)
    
    if not breakdown:
        raise HTTPException(status_code=404, detail="Quotation not found")
    
    # Find the specific item
    item = None
    for item_data in breakdown["items"]:
        if item_data["item_id"] == item_id:
            item = item_data
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.get("/cost-calculator/demo")
async def cost_calculator_demo() -> Dict[str, Any]:
    """
    Demo endpoint showing cost calculation examples
    """
    from decimal import Decimal
    
    # Mock data for demonstration
    class MockThicknessOption:
        def __init__(self, cost_per_sqft):
            self.cost_per_sqft = cost_per_sqft
    
    thickness_option = MockThicknessOption(Decimal('25.50'))
    
    # Example calculations
    base_cost = CostCalculator.calculate_base_cost(
        length=Decimal('1000'),
        breadth=Decimal('800'),
        thickness_option=thickness_option,
        quantity=2
    )
    
    return {
        "message": "Cost Calculator Demo",
        "example": {
            "dimensions": "1000mm × 800mm",
            "thickness_cost_per_sqft": "$25.50",
            "quantity": 2,
            "calculations": {
                "area_sqmm": float(base_cost['area_sqmm']),
                "area_sqft": float(base_cost['area_sqft']),
                "base_cost_per_unit": float(base_cost['base_cost_per_unit']),
                "total_base_cost": float(base_cost['total_base_cost'])
            }
        },
        "usage": {
            "base_cost": "Use calculate_base_cost() for door base costs",
            "attribute_cost": "Use calculate_attribute_cost() for attribute costs",
            "item_total": "Use calculate_item_total_cost() for item totals",
            "quotation_total": "Use calculate_quotation_total_cost() for quotation totals"
        }
    }
