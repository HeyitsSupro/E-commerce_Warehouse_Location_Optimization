import pulp
from math import radians, sin, cos, sqrt, atan2
import pandas as pd

# Data for top 10 cities
cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Chennai', 'Kolkata', 'Pune', 'Jaipur', 'Lucknow']
coords = {
    'Mumbai': (19.0760, 72.8777), 'Delhi': (28.7041, 77.1025), 'Bangalore': (12.9716, 77.5946),
    'Hyderabad': (17.3850, 78.4867), 'Ahmedabad': (23.0225, 72.5714), 'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639), 'Pune': (18.5204, 73.8567), 'Jaipur': (26.9124, 75.7873),
    'Lucknow': (26.8467, 80.9462)
}
demand = {
    'Mumbai': 1500, 'Delhi': 1200, 'Bangalore': 1000, 'Hyderabad': 800, 'Ahmedabad': 600,
    'Chennai': 700, 'Kolkata': 900, 'Pune': 500, 'Jaipur': 300, 'Lucknow': 200
}
setup_costs = {
    'Mumbai': 3000000, 'Delhi': 2500000, 'Bangalore': 2000000, 'Hyderabad': 1800000, 'Ahmedabad': 1500000,
    'Chennai': 2200000, 'Kolkata': 2400000, 'Pune': 1700000, 'Jaipur': 1200000, 'Lucknow': 1300000
}
B = 10000000  # Budget in INR
K = 4         # Max warehouses
T = 34       # Max delivery time in hours
speed = 40    # km/h
cost_per_km_per_order = 0.1  # INR per km per order

# Calculate distances using Haversine formula
distances = {}
for i in cities:
    for j in cities:
        lat1, lon1 = radians(coords[i][0]), radians(coords[i][1])
        lat2, lon2 = radians(coords[j][0]), radians(coords[j][1])
        R = 6371
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distances[(i, j)] = R * c

# Delivery costs and times
d = {(i, j): distances[(i, j)] * cost_per_km_per_order for i in cities for j in cities}
t = {(i, j): distances[(i, j)] / speed for i in cities for j in cities}

# Feasible assignments
I_j = {j: [i for i in cities if t[(i, j)] <= T] for j in cities}

# Define MILP problem
prob = pulp.LpProblem('Warehouse_Optimization', pulp.LpMinimize)

# Variables
x = pulp.LpVariable.dicts('x', cities, cat='Binary')
y = pulp.LpVariable.dicts('y', [(i, j) for j in cities for i in I_j[j]], cat='Binary')

# Objective
prob += pulp.lpSum(d[(i, j)] * demand[j] * y[(i, j)] for j in cities for i in I_j[j])

# Constraints
prob += pulp.lpSum(setup_costs[i] * x[i] for i in cities) <= B
prob += pulp.lpSum(x[i] for i in cities) <= K
for j in cities:
    prob += pulp.lpSum(y[(i, j)] for i in I_j[j]) == 1
for j in cities:
    for i in I_j[j]:
        prob += y[(i, j)] <= x[i]

# Solve with verbose output
prob.solve(pulp.PULP_CBC_CMD(msg=True))

# Check solution status
status = pulp.LpStatus[prob.status]
print('Status:', status)

if status == 'Optimal':
    selected_warehouses = [i for i in cities if pulp.value(x[i]) == 1]
    total_setup_cost = sum(setup_costs[i] for i in selected_warehouses)
    number_of_warehouses = sum(pulp.value(x[i]) for i in cities)
    delivery_cost = pulp.value(prob.objective)
    total_cost = delivery_cost + total_setup_cost

    print('Total Delivery Cost (INR):', delivery_cost)
    print('Total Setup Cost (INR):', total_setup_cost)
    print('Total Cost (INR):', total_cost)
    print('Number of Warehouses Used:', int(number_of_warehouses))
    print('Selected Warehouses:', selected_warehouses)

    print('Assignments:')
    assignment_results = []
    for j in cities:
        for i in I_j[j]:
            if pulp.value(y[(i, j)]) == 1:
                adjusted_time = t[(i, j)] + 2  # Add 2 hours buffer
                base_cost = d[(i, j)]
                final_cost = base_cost + 5  # Add 5 INR to delivery cost
                print(f'  {j} served by {i} (Cost: {final_cost:.2f}, Time: {adjusted_time:.2f} hours)')
                print(f'    The product will be delivered within {adjusted_time:.2f} hours with maximum cost {final_cost:.2f}')
                assignment_results.append({
                    'City': j,
                    'Warehouse': i,
                    'Delivery Cost per Order (INR)': final_cost,
                    'Delivery Time (hours)': adjusted_time
                })

    # Export to DataFrame
    df_result = pd.DataFrame(assignment_results)
    print('\nAssignment Summary DataFrame:')
    print(df_result)
else:
    print('No optimal solution found.')