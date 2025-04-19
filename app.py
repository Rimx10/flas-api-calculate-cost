from flask import Flask, request, jsonify
from itertools import permutations
import math

app = Flask(__name__)

# Product location and weight database
product_db = {
    'A': ('C1', 3),
    'B': ('C1', 2),
    'C': ('C1', 8),
    'D': ('C2', 12),
    'E': ('C2', 25),
    'F': ('C2', 15),
    'G': ('C3', 0.5),
    'H': ('C3', 1),
    'I': ('C3', 2),
}

# Distances between nodes
distance = {
    ('C1', 'C2'): 4,
    ('C2', 'C1'): 4,
    ('C1', 'C3'): 3,
    ('C3', 'C1'): 3,
    ('C2', 'C3'): 2,
    ('C3', 'C2'): 2,
    ('C1', 'L1'): 3,
    ('L1', 'C1'): 3,
    ('C2', 'L1'): 2.5,
    ('L1', 'C2'): 2.5,
    ('C3', 'L1'): 3,
    ('L1', 'C3'): 3,
}

# Cost calculation function
def calculate_cost(weight, dist):
    if weight <= 5:
        return dist * 10
    else:
        base_cost = dist * 10
        additional_weight = weight - 5
        additional_blocks = math.ceil(additional_weight / 5)
        additional_cost = additional_blocks * dist * 8
        return base_cost + additional_cost

@app.route('/min_cost', methods=['POST'])
def min_cost():
    order = request.get_json()

    # Organize products by center
    center_products = {'C1': [], 'C2': [], 'C3': []}
    for product, qty in order.items():
        if product in product_db and qty > 0:
            center, weight = product_db[product]
            center_products[center].append((product, qty, weight))

    # Get involved centers
    involved_centers = [center for center in center_products if center_products[center]]

    min_total_cost = float('inf')

    for start in involved_centers:
        other_centers = [c for c in involved_centers if c != start]
        for perm in permutations(other_centers):
            route = [start] + list(perm) + ['L1']
            total_cost = 0
            carried_items = []

            for i in range(len(route)-1):
                from_node = route[i]
                to_node = route[i+1]

                if from_node in center_products:
                    carried_items.extend(center_products[from_node])

                weight = sum(qty * wt for _, qty, wt in carried_items)
                dist = distance.get((from_node, to_node), float('inf'))
                total_cost += calculate_cost(weight, dist)

            min_total_cost = min(min_total_cost, total_cost)

    return jsonify({'minimum_cost': int(min_total_cost)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
