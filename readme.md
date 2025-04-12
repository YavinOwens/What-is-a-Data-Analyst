# Lean Six Sigma Project for Water Industry Manufacturing

## Overview
This project applies Lean Six Sigma principles to improve manufacturing processes in the water industry, utilizing Python scripts and notebooks for data analysis and process improvement.

## Dummy Data
The project includes a relational database structure with the following entities:
- **Plants**
- **Products**
- **Orders**
- **Suppliers**

## Functions Overview

### 1. `create_plants(num_plants)`
- **Description**: Generates a list of dummy plant data for the manufacturing context. Each plant has a unique ID, a randomly generated name, and a location.
- **Parameters**:
  - `num_plants` (int): The number of plants to create.
- **Returns**: A list of dictionaries, each representing a plant with the following keys:
  - `PlantID`: Unique identifier for the plant.
  - `PlantName`: Randomly generated name of the plant.
  - `Location`: Randomly generated city where the plant is located.

### 2. `create_products(plants, num_products)`
- **Description**: Generates a list of dummy product data associated with the given plants. Each product has a unique ID, a name, a reference to a plant, and a cost.
- **Parameters**:
  - `plants` (list): A list of plant dictionaries to associate products with.
  - `num_products` (int): The number of products to create.
- **Returns**: A list of dictionaries, each representing a product with the following keys:
  - `ProductID`: Unique identifier for the product.
  - `ProductName`: Randomly generated name for the product (e.g., "Filtered Water").
  - `PlantID`: The ID of the plant that produces the product.
  - `Cost`: Randomly generated cost of the product.

### 3. `create_orders(products, num_orders)`
- **Description**: Generates a list of dummy order data for the products. Each order has a unique ID, a reference to a product, a quantity, and an order date.
- **Parameters**:
  - `products` (list): A list of product dictionaries to associate orders with.
  - `num_orders` (int): The number of orders to create.
- **Returns**: A list of dictionaries, each representing an order with the following keys:
  - `OrderID`: Unique identifier for the order.
  - `ProductID`: The ID of the product being ordered.
  - `Quantity`: Randomly generated quantity of the product ordered.
  - `OrderDate`: Randomly generated date for when the order was placed.

### 4. `create_suppliers(products, num_suppliers)`
- **Description**: Generates a list of dummy supplier data for the products. Each supplier has a unique ID, a name, and a reference to a product they supply.
- **Parameters**:
  - `products` (list): A list of product dictionaries to associate suppliers with.
  - `num_suppliers` (int): The number of suppliers to create.
- **Returns**: A list of dictionaries, each representing a supplier with the following keys:
  - `SupplierID`: Unique identifier for the supplier.
  - `SupplierName`: Randomly generated name of the supplier.
  - `ProductID`: The ID of the product that the supplier provides.

### Example Usage
```python
if __name__ == "__main__":
    num_plants = 5
    num_products = 10
    num_orders = 20
    num_suppliers = 5

    plants = create_plants(num_plants)
    products = create_products(plants, num_products)
    orders = create_orders(products, num_orders)
    suppliers = create_suppliers(products, num_suppliers)

    print("Plants:", plants)
    print("Products:", products)
    print("Orders:", orders)
    print("Suppliers:", suppliers)
```
### Sample Data
```sql
-- SQL commands to create and populate tables

-- Plants
INSERT INTO Plants (PlantID, PlantName, Location) VALUES (1, 'Water Plant A', 'Location A');
INSERT INTO Plants (PlantID, PlantName, Location) VALUES (2, 'Water Plant B', 'Location B');

-- Products
INSERT INTO Products (ProductID, ProductName, PlantID, Cost) VALUES (1, 'Filtered Water', 1, 1.00);
INSERT INTO Products (ProductID, ProductName, PlantID, Cost) VALUES (2, 'Mineral Water', 2, 1.50);

-- Orders
INSERT INTO Orders (OrderID, ProductID, Quantity, OrderDate) VALUES (1, 1, 100, '2023-01-01');
INSERT INTO Orders (OrderID, ProductID, Quantity, OrderDate) VALUES (2, 2, 200, '2023-01-02');

-- Suppliers
INSERT INTO Suppliers (SupplierID, SupplierName, ProductID) VALUES (1, 'Supplier A', 1);
INSERT INTO Suppliers (SupplierID, SupplierName, ProductID) VALUES (2, 'Supplier B', 2);
```

## DMAIC Framework
### Define
- Problem statement and project goals.

### Measure
- Data collection methods and metrics.

### Analyze
- Tools and techniques used for analysis.

### Improve
- Proposed solutions and implementation strategies.

### Control
- Monitoring and sustaining improvements.

