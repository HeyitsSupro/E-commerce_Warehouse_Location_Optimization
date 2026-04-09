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
- **Demand** modelled as a Poisson random variable; expected value used in objective

## Result
The optimizer selects **Mumbai, Delhi, Bangalore, and Kolkata**, achieving a 
minimum daily delivery cost of ₹1,08,461 across all 10 cities.

| City       | Served by  | Cost/Order (₹) | Delivery Time (hrs) |
|------------|------------|----------------|----------------------|
| Mumbai     | Mumbai     | 5.00           | 2.00                 |
| Delhi      | Delhi      | 5.00           | 2.00                 |
| Bangalore  | Bangalore  | 5.00           | 2.00                 |
| Kolkata    | Kolkata    | 5.00           | 2.00                 |
| Pune       | Mumbai     | 17.02          | 5.00                 |
| Jaipur     | Delhi      | 28.75          | 7.94                 |
| Chennai    | Bangalore  | 34.02          | 9.25                 |
| Ahmedabad  | Mumbai     | 49.00          | 13.00                |
| Lucknow    | Delhi      | 48.08          | 12.77                |
| Hyderabad  | Bangalore  | 55.00          | 14.50                |

## Setup
```bash
pip install -r requirements.txt
python code.py
```

## Parameters
You can adjust these constants at the top of `code.py`:
| Parameter | Default | Description |
|-----------|---------|-------------|
| `B` | ₹10,000,000 | Total budget |
| `K` | 4 | Max warehouses |
| `T` | 34 hrs | Max delivery time |
| `speed` | 40 km/h | Average vehicle speed |

## This was a collaborative academic project.
