from flask import Flask, request, jsonify
from itertools import permutations
import math

app = Flask(__name__)

WAREHOUSES = {
    'C1': {'A': 3, 'B': 2, 'C': 8},
    'C2': {'D': 12, 'E': 25, 'F': 15},
    'C3': {'G': 0.5, 'H': 1, 'I': 2}
}

DISTANCE = {
    'C1': {'C2': 4, 'C3': 3, 'L1': 3},
    'C2': {'C1': 4, 'C3': 3, 'L1': 2.5},
    'C3': {'C1': 3, 'C2': 3, 'L1': 2}
}


def get_product_location(product):
    for center, products in WAREHOUSES.items():
        if product in products:
            return center
    return None


# ✅ FIXED: Use only weight picked up at each warehouse for each segment
def calculate_cost(path, warehouse_weights):
    total_cost = 0

    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]

        segment_weight = warehouse_weights.get(current_node, 0)  # Only pickup weight at this node
        distance = DISTANCE[current_node][next_node]

        if segment_weight <= 5:
            cost_per_unit = 10
        else:
            cost_per_unit = 10 + math.ceil((segment_weight - 5) / 5) * 8

        total_cost += cost_per_unit * distance

    return total_cost


@app.route('/calculate-cost', methods=['POST'])
def calculate_min_cost():
    data = request.get_json()
    requested_products = {k: v for k, v in data.items() if v > 0}

    if not requested_products:
        return jsonify({'error': 'No valid products with quantity > 0'}), 400

    warehouse_weights = {}
    for product, quantity in requested_products.items():
        location = get_product_location(product)
        if not location:
            return jsonify({'error': f'Invalid product: {product}'}), 400
        weight = WAREHOUSES[location][product] * quantity
        warehouse_weights[location] = warehouse_weights.get(location, 0) + weight

    min_cost = float('inf')

    for order in permutations(warehouse_weights.keys()):
        path = list(order) + ['L1']
        cost = calculate_cost(path, warehouse_weights)
        min_cost = min(min_cost, cost)

    return jsonify({'minimum_cost': round(min_cost)})


@app.route('/')
def home():
    return '''
    <h1>Welcome to the Cost Calculator API</h1>
    <p>Use the <code>/calculate-cost</code> endpoint with a POST request and JSON data.</p>
    '''


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
is this correct?

