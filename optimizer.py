import pulp
from math import radians, sin, cos, sqrt, atan2
import pandas as pd

# Data for top 10 cities
cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad',
          'Chennai', 'Kolkata', 'Pune', 'Jaipur', 'Lucknow']

coords = {
    'Mumbai': (19.0760, 72.8777), 'Delhi': (28.7041, 77.1025), 'Bangalore': (12.9716, 77.5946),
    'Hyderabad': (17.3850, 78.4867), 'Ahmedabad': (23.0225, 72.5714), 'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639), 'Pune': (18.5204, 73.8567), 'Jaipur': (26.9124, 75.7873),
    'Lucknow': (26.8467, 80.9462)
}
demand = {   # expected daily order volume per city (deterministic)
    'Mumbai': 1500, 'Delhi': 1200, 'Bangalore': 1000, 'Hyderabad': 800, 'Ahmedabad': 600,
    'Chennai': 700, 'Kolkata': 900, 'Pune': 500, 'Jaipur': 300, 'Lucknow': 200
}
setup_costs = {   # ANNUAL setup / holding cost per warehouse (INR)
    'Mumbai': 3000000, 'Delhi': 2500000, 'Bangalore': 2000000, 'Hyderabad': 1800000, 'Ahmedabad': 1500000,
    'Chennai': 2200000, 'Kolkata': 2400000, 'Pune': 1700000, 'Jaipur': 1200000, 'Lucknow': 1300000
}

B = 10_000_000               # Budget cap on annual setup (INR)
K = 4                        # Max warehouses
T = 36                       # Max delivery time (hours) on real travel time
speed = 40                   # km/h
cost_per_km_per_order = 0.1  # INR per km per order
DAYS_PER_YEAR = 365          # puts daily delivery and annual setup on one basis

# Haversine great-circle distances
distances = {}
for i in cities:
    for j in cities:
        lat1, lon1 = radians(coords[i][0]), radians(coords[i][1])
        lat2, lon2 = radians(coords[j][0]), radians(coords[j][1])
        R = 6371
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distances[(i, j)] = R * c

# per-order delivery cost (INR) and travel time (hours)
d = {(i, j): distances[(i, j)] * cost_per_km_per_order for i in cities for j in cities}
t = {(i, j): distances[(i, j)] / speed for i in cities for j in cities}

# feasible assignments: only those within the delivery-time limit
I_j = {j: [i for i in cities if t[(i, j)] <= T] for j in cities}

# MILP
prob = pulp.LpProblem('Warehouse_Optimization', pulp.LpMinimize)

x = pulp.LpVariable.dicts('x', cities, cat='Binary')
y = pulp.LpVariable.dicts('y', [(i, j) for j in cities for i in I_j[j]], cat='Binary')

# Objective: annual total cost = annualized delivery + annual setup
annual_delivery = DAYS_PER_YEAR * pulp.lpSum(
    d[(i, j)] * demand[j] * y[(i, j)] for j in cities for i in I_j[j]
)
annual_setup = pulp.lpSum(setup_costs[i] * x[i] for i in cities)
prob += annual_delivery + annual_setup

# Constraints
prob += pulp.lpSum(setup_costs[i] * x[i] for i in cities) <= B     # budget on setup
prob += pulp.lpSum(x[i] for i in cities) <= K                      # warehouse cap
for j in cities:
    prob += pulp.lpSum(y[(i, j)] for i in I_j[j]) == 1             # each city served exactly once
for j in cities:
    for i in I_j[j]:
        prob += y[(i, j)] <= x[i]                                  # link assignment to open warehouse

prob.solve(pulp.PULP_CBC_CMD(msg=True))

status = pulp.LpStatus[prob.status]
print('Status:', status)

if status == 'Optimal':
    selected = [i for i in cities if pulp.value(x[i]) == 1]
    setup_total = sum(setup_costs[i] for i in selected)

    daily_delivery = sum(
        d[(i, j)] * demand[j] * pulp.value(y[(i, j)])
        for j in cities for i in I_j[j]
    )
    annual_delivery_val = daily_delivery * DAYS_PER_YEAR
    total_annual = annual_delivery_val + setup_total

    print(f'Selected warehouses       : {selected}')
    print(f'Number of warehouses      : {len(selected)}')
    print(f'Daily delivery cost  (INR): {daily_delivery:,.2f}')
    print(f'Annual delivery cost (INR): {annual_delivery_val:,.2f}')
    print(f'Annual setup cost    (INR): {setup_total:,.2f}')
    print(f'Total annual cost    (INR): {total_annual:,.2f}')

    rows = []
    for j in cities:
        for i in I_j[j]:
            if pulp.value(y[(i, j)]) == 1:
                rows.append({
                    'City': j,
                    'Warehouse': i,
                    'Cost per Order (INR)': round(d[(i, j)], 2),
                    'Delivery Time (hrs)': round(t[(i, j)], 2),
                })
    df_result = pd.DataFrame(rows).sort_values('Delivery Time (hrs)').reset_index(drop=True)
    print('\nAssignment Summary:')
    print(df_result.to_string(index=False))
else:
    print('No optimal solution found.')
