from flask import Flask, request, jsonify
from itertools import permutations
import math

app = Flask(__name__)

# Warehouse data
WAREHOUSES = {
    'C1': {'A': 3, 'B': 2, 'C': 8},
    'C2': {'D': 12, 'E': 25, 'F': 15},
    'C3': {'G': 0.5, 'H': 1, 'I': 2}
}

# Distance graph (undirected)
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

def calculate_cost(path, weight_by_segment):
    total_cost = 0
    for i in range(len(path) - 1):
        segment_weight = weight_by_segment[i]
        distance = DISTANCE[path[i]][path[i + 1]]
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

    product_weights = {}
    pickup_centers = set()
    for product, quantity in requested_products.items():
        location = get_product_location(product)
        if location:
            weight = WAREHOUSES[location][product] * quantity
            product_weights[product] = weight
            pickup_centers.add(location)
        else:
            return jsonify({'error': f"Invalid product: {product}"}), 400

    min_cost = float('inf')
    best_route = []

    for start in ['C1', 'C2', 'C3']:
        if start not in DISTANCE:
            continue
    for order in permutations(pickup_centers):        
        path = list(order) + ['L1']
        carried_weight = 0
        weight_by_segment = []
        visited_products = set()
        for i in range(len(path) - 1):
            segment_pickup = 0
            for product, weight in product_weights.items():
                product_center = get_product_location(product)
                if product_center == path[i] and product not in visited_products:
                    segment_pickup += weight
                    visited_products.add(product)
            carried_weight += segment_pickup
            weight_by_segment.append(carried_weight)

        cost = calculate_cost(path, weight_by_segment)
        if cost < min_cost:
            min_cost = cost
            best_route = path

    if min_cost == float('inf'):
        return jsonify({'error': 'No valid delivery route found'}), 400

    return jsonify({'minimum_cost': round(min_cost)})

@app.route('/')
def home():
    return '''
    <h1>Welcome to the Cost Calculator API</h1>
    <p>Use the <code>/calculate-cost</code> endpoint with a POST request and JSON data.</p>
    '''

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
