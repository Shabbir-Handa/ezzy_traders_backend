# Ezzy Traders Backend API Documentation

## Overview
Ezzy Traders Backend is a comprehensive door quotation management system that handles customer quotations, door types, attributes, and cost calculations. The system supports various attribute types including constant, variable, direct, and nested attributes.

## Database Schema

### Core Tables

#### 1. Employee Management
- **`employee`**: Stores employee information with authentication details
  - `username`, `hashed_password`, `email`, `phone`, `first_name`, `last_name`
  - `role`: admin, manager, sales, engineer, viewer
  - `is_active`: Boolean flag for soft deletion

#### 2. Customer Management
- **`customer_details`**: Customer information and contact details
  - `name`, `email`, `phone`, `address`, `city`, `state`, `postal_code`, `country`
  - `is_active`: Boolean flag for soft deletion

#### 3. Door and Attribute Management
- **`door_type`**: Different types of doors (Solid Wood, Hollow Core, Metal, Glass)
- **`door_type_thickness_option`**: Thickness options with cost per square foot
- **`attribute`**: Various attributes that can be applied to doors
  - `cost_type`: constant, variable, direct, nested
  - `fixed_cost`: For constant cost attributes
  - `cost_per_unit`: For variable cost attributes
  - `double_side`: Boolean for double-sided application
- **`attribute_option`**: Options for constant-type attributes with different costs
- **`entity_attribute`**: Links attributes to door types
- **`unit`**: Measurement units (Piece, Square Foot, Linear Foot, Kilogram, etc.)

#### 4. Quotation Management
- **`quotation`**: Main quotation records
  - `quotation_number`: Auto-generated unique identifier (QT2024010001 format)
  - `customer_id`, `date`, `status`, `total_amount`
- **`quotation_item`**: Individual items in a quotation
  - `base_cost_per_unit`: Base door cost without attributes
  - `attribute_cost_per_unit`: Sum of all attribute costs per unit
  - `unit_price_with_attributes`: Per-door price including attributes
  - `total_item_cost`: Total cost for quantity (unit_price_with_attributes × quantity)
- **`quotation_item_attribute`**: Attribute selections for each item
  - `selected_option_id`: For constant/variable attributes
  - `direct_cost`: User-override cost
  - `calculated_cost`: System-calculated cost
  - `total_attribute_cost`: Final attribute cost
- **`unit_value`**: Unit measurements for variable cost attributes

## Cost Calculation System

### Base Cost Calculation
```
Base Cost = (Length × Breadth) / 92903.04 × Cost per sqft
```
- Dimensions are stored in millimeters
- Converted to square feet for cost calculation
- Multiplied by thickness-specific cost per square foot

### Attribute Cost Types

#### 1. Constant Cost Attributes
- Fixed cost regardless of dimensions or quantity
- Examples: Premium Finish, Hardware Package
- Can have multiple options with different costs
- Double-side multiplier applies if applicable

#### 2. Variable Cost Attributes
- Cost varies based on unit measurements
- Examples: Custom Size (cost per square foot)
- Unit values stored in `unit_value` table
- Supports area (value1 × value2) and linear (value1) calculations

#### 3. Direct Cost Attributes
- User-specified cost override
- Examples: Special Handling, Custom Requirements
- Bypasses system calculation

#### 4. Nested Attributes
- Complex attributes with sub-components
- Recursive cost calculation
- Examples: Multi-part hardware systems

### Total Cost Calculation
```
Per-Unit Cost = Base Cost + Sum of Attribute Costs
Total Item Cost = Per-Unit Cost × Quantity
Quotation Total = Sum of All Item Costs
```

## API Endpoints

### Authentication
```
POST /auth/login
POST /auth/register
```

### Employee Management
```
GET /employees/ - List all employees
POST /employees/ - Create new employee
GET /employees/{id} - Get employee details
PUT /employees/{id} - Update employee
DELETE /employees/{id} - Delete employee
```

### Customer Management
```
GET /customers/ - List all customers
POST /customers/ - Create new customer
GET /customers/{id} - Get customer details
PUT /customers/{id} - Update customer
DELETE /customers/{id} - Delete customer
```

### Door Type Management
```
GET /door-types/ - List all door types
POST /door-types/ - Create new door type
GET /door-types/{id} - Get door type details
PUT /door-types/{id} - Update door type
DELETE /door-types/{id} - Delete door type
```

### Attribute Management
```
GET /attributes/ - List all attributes
POST /attributes/ - Create new attribute
GET /attributes/{id} - Get attribute details
PUT /attributes/{id} - Update attribute
DELETE /attributes/{id} - Delete attribute
```

### Quotation Management
```
GET /quotations/ - List all quotations
POST /quotations/ - Create new quotation
GET /quotations/{id} - Get quotation details
PUT /quotations/{id} - Update quotation
DELETE /quotations/{id} - Delete quotation
GET /quotations/{id}/cost-breakdown - Get detailed cost breakdown
POST /quotations/{id}/recalculate - Recalculate all costs
```

## Example Payloads

### 1. Create Customer
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA"
}
```

### 2. Create Door Type with Thickness Options
```json
{
  "name": "Premium Solid Wood Door",
  "description": "High-quality solid wood door with premium finish",
  "thickness_options": [
    {
      "thickness_value": 45.0,
      "cost_per_sqft": 35.00
    },
    {
      "thickness_value": 55.0,
      "cost_per_sqft": 45.00
    }
  ]
}
```

### 3. Create Attribute (Constant Cost)
```json
{
  "name": "Premium Finish",
  "description": "High-quality premium finish",
  "double_side": true,
  "cost_type": "constant",
  "fixed_cost": 50.00,
  "options": [
    {
      "name": "Standard Premium",
      "cost": 50.00,
      "display_order": 1
    },
    {
      "name": "Deluxe Premium",
      "cost": 75.00,
      "display_order": 2
    }
  ]
}
```

### 4. Create Attribute (Variable Cost)
```json
{
  "name": "Custom Size",
  "description": "Custom size adjustment",
  "double_side": false,
  "cost_type": "variable",
  "cost_per_unit": 2.50,
  "unit_id": 2
}
```

### 5. Create Attribute (Direct Cost)
```json
{
  "name": "Special Handling",
  "description": "Special handling requirements",
  "double_side": false,
  "cost_type": "direct"
}
```

### 6. Create Comprehensive Quotation

#### Request Payload
```json
{
  "customer_id": 1,
  "date": "2024-01-15T00:00:00",
  "status": "draft",
  "items": [
    {
      "door_type_id": 1,
      "thickness_option_id": 2,
      "length": 2133.6,
      "breadth": 914.4,
      "quantity": 2,
      "attributes": [
        {
          "attribute_id": 1,
          "selected_option_id": 2,
          "double_side": true,
          "direct_cost": null
        },
        {
          "attribute_id": 2,
          "selected_option_id": null,
          "double_side": false,
          "direct_cost": null,
          "unit_values": [
            {
              "unit_id": 2,
              "value1": 20.0,
              "value2": 7.0
            }
          ]
        },
        {
          "attribute_id": 3,
          "selected_option_id": null,
          "double_side": false,
          "direct_cost": 25.00
        },
        {
          "attribute_id": 4,
          "selected_option_id": 1,
          "double_side": false,
          "direct_cost": null
        }
      ]
    }
  ]
}
```

#### Response Payload
```json
{
  "id": 1,
  "quotation_number": "QT2024010001",
  "customer_id": 1,
  "date": "2024-01-15T00:00:00",
  "status": "draft",
  "total_amount": 1250.00,
  "customer": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com"
  },
  "items": [
    {
      "id": 1,
      "door_type_id": 1,
      "thickness_option_id": 2,
      "length": 2133.6,
      "breadth": 914.4,
      "quantity": 2,
      "base_cost_per_unit": 75.00,
      "attribute_cost_per_unit": 550.00,
      "unit_price_with_attributes": 625.00,
      "total_item_cost": 1250.00,
      "door_type": {
        "id": 1,
        "name": "Premium Solid Wood Door"
      },
      "thickness_option": {
        "id": 2,
        "thickness_value": 45.0,
        "cost_per_sqft": 35.00
      },
      "attributes": [
        {
          "id": 1,
          "attribute_id": 1,
          "selected_option_id": 2,
          "double_side": true,
          "direct_cost": null,
          "calculated_cost": 150.00,
          "total_attribute_cost": 150.00,
          "attribute": {
            "id": 1,
            "name": "Premium Finish",
            "cost_type": "constant"
          }
        },
        {
          "id": 2,
          "attribute_id": 2,
          "selected_option_id": null,
          "double_side": false,
          "direct_cost": null,
          "calculated_cost": 350.00,
          "total_attribute_cost": 350.00,
          "attribute": {
            "id": 2,
            "name": "Custom Size",
            "cost_type": "variable"
          },
          "unit_values": [
            {
              "id": 1,
              "unit_id": 2,
              "value1": 20.0,
              "value2": 7.0,
              "unit": {
                "id": 2,
                "name": "Square Foot"
              }
            }
          ]
        },
        {
          "id": 3,
          "attribute_id": 3,
          "selected_option_id": null,
          "double_side": false,
          "direct_cost": 25.00,
          "calculated_cost": 25.00,
          "total_attribute_cost": 25.00,
          "attribute": {
            "id": 3,
            "name": "Special Handling",
            "cost_type": "direct"
          }
        },
        {
          "id": 4,
          "attribute_id": 4,
          "selected_option_id": 1,
          "double_side": false,
          "direct_cost": null,
          "calculated_cost": 75.00,
          "total_attribute_cost": 75.00,
          "attribute": {
            "id": 4,
            "name": "Hardware Package",
            "cost_type": "constant"
          }
        }
      ]
    }
  ]
}
```

### 7. Cost Breakdown Response
```json
{
  "quotation_id": 1,
  "quotation_number": "QT2024010001",
  "customer_name": "John Doe",
  "total_amount": 1250.00,
  "items": [
    {
      "item_id": 1,
      "door_type": "Premium Solid Wood Door",
      "thickness": 45.0,
      "dimensions": "2133.6mm × 914.4mm",
      "quantity": 2,
      "base_cost": {
        "cost_per_sqft": 35.00,
        "area_sqft": 20.0,
        "base_cost_per_unit": 75.00,
        "total_base_cost": 150.00
      },
      "attributes": [
        {
          "attribute_id": 1,
          "attribute_name": "Premium Finish",
          "cost_type": "constant",
          "double_side": true,
          "calculated_cost": 150.00,
          "direct_cost": 0.00,
          "total_attribute_cost": 150.00
        }
      ],
      "attribute_costs": 600.00,
      "total_item_cost": 1250.00
    }
  ],
  "summary": {
    "total_base_cost": 150.00,
    "total_attribute_cost": 600.00,
    "total_quotation_cost": 1250.00,
    "item_count": 1
  }
}
```

## Cost Calculation Examples

### Example 1: Basic Door with Premium Finish
- **Door**: 2133.6mm × 914.4mm (20 sqft)
- **Thickness**: 45mm at $35/sqft
- **Base Cost**: 20 × $35 = $700
- **Premium Finish**: $75 (constant, double-side = false)
- **Total per Unit**: $700 + $75 = $775
- **Quantity**: 2
- **Total Item Cost**: $775 × 2 = $1,550

### Example 2: Door with Variable Size Adjustment
- **Base Cost**: $700
- **Custom Size**: 20 sqft × $2.50/sqft = $50
- **Total per Unit**: $700 + $50 = $750
- **Quantity**: 1
- **Total Item Cost**: $750

### Example 3: Door with Multiple Attributes
- **Base Cost**: $700
- **Premium Finish**: $75 (double-side = true) = $150
- **Custom Size**: $50
- **Special Handling**: $25 (direct cost)
- **Hardware Package**: $75
- **Total per Unit**: $700 + $150 + $50 + $25 + $75 = $1,000
- **Quantity**: 1
- **Total Item Cost**: $1,000

## Setup and Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create database and run migrations
alembic upgrade head
```

### 3. Seed Data
```python
from db_helper.seed_data import seed_all_data
from db_helper.database import get_db

db = next(get_db())
seed_all_data(db)
```

### 4. Run Application
```bash
uvicorn main:app --reload
```

## Default Login Credentials
- **Username**: shabbir
- **Password**: shabbir
- **Role**: admin

## Testing the API

### 1. Login to Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=shabbir&password=shabbir"
```

### 2. Use Token for Authenticated Requests
```bash
curl -X GET "http://localhost:8000/quotations/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Notes
- All dimensions are stored in millimeters
- Costs are calculated in the system's base currency
- Double-side attributes automatically multiply cost by 2 when applicable
- Direct cost attributes override system calculations
- Quotation numbers are auto-generated in QTYYYYMM#### format
- All timestamps are in UTC
- Soft deletion is implemented for most entities
