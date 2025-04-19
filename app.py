from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(_name_)

# warehouse data
WAREHOUSES = {
    'C1': {'A': 3, 'B': 2, 'C': 8},
    'C2': {'D': 12, 'E': 25, 'F': 15},
    'C3': {'G': 0.5, 'H': 1, 'I': 2}
}

# distance graph (undirected)
DISTANCE = {
    'C1': {'C2': 4, 'C3': 3, 'L1': 3},
    'C2': {'C1': 4, 'C3': 3, 'L1': 2.5},
    'C3': {'C1': 3, 'C2': 3, 'L1': 2},
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
        cost_per_unit = 10 if segment_weight <= 5 else 10 + ((segment_weight - 5) // 5 + 1) * 8
        total_cost += cost_per_unit * distance
    return total_cost

@app.route('/calculate-cost', methods=['POST'])
def calculate_min_cost():
    data = request.get_json()
    requested_products = {k: v for k, v in data.items() if v > 0}
    pickup_centers = set()

    for product in requested_products:
        location = get_product_location(product)
        if location:
            pickup_centers.add(location)
        else:
            return jsonify({'error': f"Invalid product: {product}"}), 400

    min_cost = float('inf')
    best_route = []

    for order in permutations(pickup_centers):
        path = list(order) + ['L1']
        weight_by_segment = []
        current_weight = 0
        collected_products = set()

        for i in range(len(path) - 1):
            for product, qty in requested_products.items():
                product_center = get_product_location(product)
                if product_center == path[i] and product not in collected_products:
                    current_weight += WAREHOUSES[product_center][product] * qty
                    collected_products.add(product)
            weight_by_segment.append(current_weight)

        cost = calculate_cost(path, weight_by_segment)
        if cost < min_cost:
            min_cost = cost
            best_route = path

    return jsonify({'minimum_cost': round(min_cost)})

@app.route('/')
def home():
    return '''
    <h1>Welcome to the Cost Calculator API</h1>
    <p>Use the <code>/calculate-cost</code> endpoint with a POST request and JSON data.</p>
    '''

if _name_ == '_main_':
    app.run(host="0.0.0.0", port=3000)
