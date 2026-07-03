# E-commerce Warehouse Location Optimizer

Finds the optimal placement of warehouses across India's top 10 e-commerce 
cities using Mixed-Integer Linear Programming (MILP). Minimizes total daily 
delivery cost subject to budget, warehouse count, and delivery time constraints.

## Problem
Given 10 candidate cities with known demand, setup costs, and coordinates — 
select up to 4 warehouse locations that minimize delivery costs while staying 
within a ₹10,000,000 budget and a 36-hour delivery time limit.

## Approach
- **Distances** computed via the Haversine formula (great-circle distance)
- **Optimization** modelled as a MILP and solved using PuLP (CBC solver)
- **Objective** minimizes a single annual total cost: annualized delivery cost (daily × 365) + annual setup cost, so the setup-vs-delivery tradeoff is handled explicitly rather than setup being only a budget cap
- **Demand** taken as the expected daily order volume per city (deterministic)

> **Note:** Some inputs (certain setup costs, demand figures, and rate assumptions) are illustrative placeholders, not sourced data. The point of the project is to show the formulation and solver produce a sensible, constraint-satisfying solution — absolute cost figures are model outputs on these inputs, not empirical estimates.

## Result
The optimizer selects **Mumbai, Delhi, Bangalore, and Kolkata** as regional hubs
covering all 10 cities within the budget, warehouse-count, and 36-hour delivery
constraints. Total annual cost is **₹4,94,88,147** (annual delivery ₹3,95,88,147
+ annual setup ₹99,00,000); daily delivery cost is **₹1,08,461**.

| City       | Served by  | Cost/Order (₹) | Delivery Time (hrs) |
|------------|------------|----------------|----------------------|
| Mumbai     | Mumbai     | 0.00           | 0.00                 |
| Delhi      | Delhi      | 0.00           | 0.00                 |
| Bangalore  | Bangalore  | 0.00           | 0.00                 |
| Kolkata    | Kolkata    | 0.00           | 0.00                 |
| Pune       | Mumbai     | 12.02          | 3.00                 |
| Jaipur     | Delhi      | 23.75          | 5.94                 |
| Chennai    | Bangalore  | 29.02          | 7.25                 |
| Lucknow    | Delhi      | 43.08          | 10.77                |
| Ahmedabad  | Mumbai     | 44.00          | 11.00                |
| Hyderabad  | Bangalore  | 50.00          | 12.50                |

## Setup
```bash
pip install -r requirements.txt
optimizer.py
```

## Parameters
You can adjust these constants at the top of `optimizer.py`:
| Parameter | Default | Description |
|-----------|---------|-------------|
| `B` | ₹10,000,000 | Total budget |
| `K` | 4 | Max warehouses |
| `T` | 36 hrs | Max delivery time |
| `speed` | 40 km/h | Average vehicle speed |

## Report
A detailed project report covering the methodology, mathematical formulation, 
and results is available in `warehouse_optimization_report.pdf`.

## This was a collaborative academic project.
