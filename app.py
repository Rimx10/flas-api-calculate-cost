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

def calculate_segment_cost(weight, distance):
    if weight <= 5:
        rate = 10
    else:
        rate = 10 + math.ceil((weight - 5) / 5) * 8
    return rate * distance

def calculate_total_cost(path, product_weights, center_products):
    cost = 0
    current_weight = 0
    for i in range(len(path) - 1):
        current_center = path[i]
        # Pick up all products at this center
        for product in center_products.get(current_center, []):
            current_weight += product_weights[product]
        distance = DISTANCE[current_center][path[i + 1]]
        cost += calculate_segment_cost(current_weight, distance)
    return cost

@app.route('/calculate-cost', methods=['POST'])
def calculate_min_cost():
    data = request.get_json()
    requested_products = {k: v for k, v in data.items() if v > 0}
    if not requested_products:
        return jsonify({'error': 'No valid products with quantity > 0'}), 400

    product_weights = {}
    center_products = {}
    pickup_centers = set()

    # Map product weights and which centers have which products
    for product, qty in requested_products.items():
        center = get_product_location(product)
        if not center:
            return jsonify({'error': f'Invalid product: {product}'}), 400
        weight = WAREHOUSES[center][product] * qty
        product_weights[product] = weight
        pickup_centers.add(center)
        center_products.setdefault(center, []).append(product)

    # Try all permutations of pickup centers ending in L1
    min_cost = float('inf')
    for perm in permutations(pickup_centers):
        path = list(perm) + ['L1']
        cost = calculate_total_cost(path, product_weights, center_products)
        if cost < min_cost:
            min_cost = cost

    return jsonify({'minimum_cost': round(min_cost)})

@app.route('/')
def home():
    return '''
    <h1>Welcome to the Cost Calculator API</h1>
    <p>Use the <code>/calculate-cost</code> endpoint with a POST request and JSON data.</p>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
