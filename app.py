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

def calculate_cost(path, product_weights, product_locations):
    current_weight = 0
    total_cost = 0
    visited_products = set()

    for i in range(len(path) - 1):
        pickup_center = path[i]
        next_stop = path[i + 1]
        segment_pickup = 0

        for product, weight in product_weights.items():
            if product_locations[product] == pickup_center and product not in visited_products:
                segment_pickup += weight
                visited_products.add(product)

        current_weight += segment_pickup

        distance = DISTANCE[pickup_center][next_stop]
        if current_weight <= 5:
            cost_per_km = 10
        else:
            extra = math.ceil((current_weight - 5) / 5)
            cost_per_km = 10 + extra * 8

        total_cost += cost_per_km * distance

    return total_cost

@app.route('/calculate-cost', methods=['POST'])
def calculate_min_cost():
    data = request.get_json()
    requested_products = {k: v for k, v in data.items() if v > 0}

    if not requested_products:
        return jsonify({'error': 'No valid products with quantity > 0'}), 400

    product_weights = {}
    product_locations = {}
    pickup_centers = set()

    for product, quantity in requested_products.items():
        location = get_product_location(product)
        if not location:
            return jsonify({'error': f"Invalid product: {product}"}), 400
        product_locations[product] = location
        weight = WAREHOUSES[location][product] * quantity
        product_weights[product] = weight
        pickup_centers.add(location)

    min_cost = float('inf')

    for perm in permutations(pickup_centers):
        path = list(perm) + ['L1']
        cost = calculate_cost(path, product_weights, product_locations)
        min_cost = min(min_cost, cost)

    return jsonify({'minimum_cost': round(min_cost)})

@app.route('/')
def home():
    return '<h1>Delivery Cost Calculator API</h1><p>POST to /calculate-cost with product quantities.</p>'

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
