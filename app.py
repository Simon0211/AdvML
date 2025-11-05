"""
Santa's Delivery Route Optimizer
Optimizes delivery routes considering constraints and time windows
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

app = Flask(__name__)
CORS(app)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Constants
COAL_WEIGHT = 0.1  # kg
COAL_VOLUME = 0.1  # liters
MAX_SLEIGH_WEIGHT = 1000  # kg
MAX_SLEIGH_VOLUME = 5000  # liters
DELIVERY_START_HOUR = 22
DELIVERY_END_HOUR = 5
SLEIGH_SPEED_KMH = 500  # Santa's magic sleigh!

# Global data store
data_store = {
    'children': None,
    'route': None,
    'metrics': None
}


def load_data():
    """Load and preprocess the children dataset"""
    # Use absolute path relative to script location
    csv_path = os.path.join(SCRIPT_DIR, 'santa_children_dataset_50k.csv')

    print(f"📂 Looking for dataset at: {csv_path}")

    if not os.path.exists(csv_path):
        # Try to create a small demo dataset
        print("⚠️  Large dataset not found! Creating small demo dataset...")
        return create_demo_dataset()

    print(f"✅ Found dataset file ({os.path.getsize(csv_path) / 1024 / 1024:.1f} MB)")

    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} children from dataset")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        print("⚠️  Creating demo dataset as fallback...")
        return create_demo_dataset()

    # Replace gifts with coal for naughty children
    naughty_mask = df['nice'] == 0
    df.loc[naughty_mask, 'wishlist_item'] = 'Coal'
    df.loc[naughty_mask, 'gift_weight_kg'] = COAL_WEIGHT
    df.loc[naughty_mask, 'gift_volume_l'] = COAL_VOLUME

    return df


def create_demo_dataset():
    """Create a small demo dataset if the main CSV is not available"""
    print("🎄 Creating demo dataset with 100 children...")

    # Sample cities around the world
    cities = [
        ("London", "United Kingdom", 51.5074, -0.1278),
        ("Paris", "France", 48.8566, 2.3522),
        ("Berlin", "Germany", 52.5200, 13.4050),
        ("Madrid", "Spain", 40.4168, -3.7038),
        ("Rome", "Italy", 41.9028, 12.4964),
        ("New York", "USA", 40.7128, -74.0060),
        ("Los Angeles", "USA", 34.0522, -118.2437),
        ("Chicago", "USA", 41.8781, -87.6298),
        ("Tokyo", "Japan", 35.6762, 139.6503),
        ("Sydney", "Australia", -33.8688, 151.2093),
        ("Toronto", "Canada", 43.6532, -79.3832),
        ("Moscow", "Russia", 55.7558, 37.6173),
        ("Dubai", "UAE", 25.2048, 55.2708),
        ("Singapore", "Singapore", 1.3521, 103.8198),
        ("Mumbai", "India", 19.0760, 72.8777),
    ]

    gifts = [
        ("LEGO Set", 0.73, 4.33),
        ("Teddy Bear", 0.86, 12.28),
        ("Video Game", 0.23, 0.73),
        ("Board Game", 1.91, 9.27),
        ("Doll", 0.76, 4.14),
        ("RC Car", 1.67, 5.64),
        ("Puzzle 1000pcs", 0.64, 3.51),
        ("Basketball", 0.88, 7.21),
        ("Art Kit", 1.45, 4.82),
        ("Science Kit", 1.88, 6.48),
    ]

    names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "James",
             "Isabella", "Oliver", "Charlotte", "Benjamin", "Mia", "Lucas", "Amelia"]

    import random
    random.seed(42)

    data = []
    for i in range(100):
        city, country, lat, lon = random.choice(cities)
        gift, weight, volume = random.choice(gifts)
        name = random.choice(names) + " " + random.choice(["Smith", "Johnson", "Brown", "Davis", "Wilson"])
        nice = random.random() > 0.2  # 80% nice, 20% naughty

        # If naughty, replace with coal
        if not nice:
            gift = "Coal"
            weight = COAL_WEIGHT
            volume = COAL_VOLUME

        data.append({
            'child_id': i + 1,
            'name': name,
            'address_line': f"{random.randint(1, 999)} Main St",
            'city': city,
            'country': country,
            'latitude': lat + random.uniform(-0.5, 0.5),
            'longitude': lon + random.uniform(-0.5, 0.5),
            'timezone': 'UTC',
            'wishlist_item': gift,
            'gift_weight_kg': weight,
            'gift_volume_l': volume,
            'nice': 1 if nice else 0,
            'delivery_window_start_local': '22:00',
            'delivery_window_end_local': '05:00'
        })

    df = pd.DataFrame(data)
    print("✅ Demo dataset created with 100 children")
    return df


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


def create_distance_matrix(locations):
    """Create distance matrix for all locations"""
    n = len(locations)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = calculate_distance(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )

    return matrix


def optimize_route_greedy(df, max_weight, max_volume, north_pole_lat=90.0, north_pole_lon=0.0):
    """
    Simple greedy nearest-neighbor algorithm as fallback
    """
    route = []
    visited = set()
    current_lat, current_lon = north_pole_lat, north_pole_lon
    current_weight = 0
    current_volume = 0

    # Visit each child in nearest-first order
    for _ in range(len(df)):
        best_idx = None
        best_distance = float('inf')

        for idx in df.index:
            if idx in visited:
                continue

            # Check if we can still carry this gift
            gift_weight = df.loc[idx, 'gift_weight_kg']
            gift_volume = df.loc[idx, 'gift_volume_l']

            if current_weight + gift_weight > max_weight:
                continue
            if current_volume + gift_volume > max_volume:
                continue

            # Calculate distance
            distance = calculate_distance(
                current_lat, current_lon,
                df.loc[idx, 'latitude'],
                df.loc[idx, 'longitude']
            )

            if distance < best_distance:
                best_distance = distance
                best_idx = idx

        if best_idx is None:
            break  # No more children can be visited

        # Visit this child
        visited.add(best_idx)
        current_lat = df.loc[best_idx, 'latitude']
        current_lon = df.loc[best_idx, 'longitude']
        current_weight += df.loc[best_idx, 'gift_weight_kg']
        current_volume += df.loc[best_idx, 'gift_volume_l']

        route.append({
            'child_id': int(df.loc[best_idx, 'child_id']),
            'name': df.loc[best_idx, 'name'],
            'city': df.loc[best_idx, 'city'],
            'country': df.loc[best_idx, 'country'],
            'latitude': float(df.loc[best_idx, 'latitude']),
            'longitude': float(df.loc[best_idx, 'longitude']),
            'wishlist_item': df.loc[best_idx, 'wishlist_item'],
            'gift_weight_kg': float(df.loc[best_idx, 'gift_weight_kg']),
            'gift_volume_l': float(df.loc[best_idx, 'gift_volume_l']),
            'nice': bool(df.loc[best_idx, 'nice']),
            'order': len(route) + 1
        })

    # Calculate total distance
    total_distance = 0
    prev_lat, prev_lon = north_pole_lat, north_pole_lon
    for stop in route:
        distance = calculate_distance(prev_lat, prev_lon, stop['latitude'], stop['longitude'])
        total_distance += distance
        prev_lat, prev_lon = stop['latitude'], stop['longitude']

    # Return to North Pole
    total_distance += calculate_distance(prev_lat, prev_lon, north_pole_lat, north_pole_lon)

    # Calculate metrics
    delivery_time_hours = total_distance / SLEIGH_SPEED_KMH
    naughty_count = len([r for r in route if not r['nice']])
    nice_count = len(route) - naughty_count

    metrics = {
        'total_distance_km': round(total_distance, 2),
        'total_weight_kg': round(current_weight, 2),
        'total_volume_l': round(current_volume, 2),
        'delivery_time_hours': round(delivery_time_hours, 2),
        'children_delivered': len(route),
        'nice_children': nice_count,
        'naughty_children': naughty_count,
        'weight_utilization_percent': round((current_weight / max_weight) * 100, 1),
        'volume_utilization_percent': round((current_volume / max_volume) * 100, 1),
        'time_constraint_met': delivery_time_hours <= 7,
        'avg_distance_per_child': round(total_distance / len(route), 2) if route else 0
    }

    return route, metrics


def optimize_route(df, max_weight=MAX_SLEIGH_WEIGHT, max_volume=MAX_SLEIGH_VOLUME,
                   sample_size=500, north_pole_lat=90.0, north_pole_lon=0.0):
    """
    Optimize delivery route using OR-Tools Vehicle Routing Problem solver
    """
    # For large datasets, sample to keep computation reasonable
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
    else:
        df_sample = df.copy()

    # Check if total weight/volume exceeds capacity
    total_weight = df_sample['gift_weight_kg'].sum()
    total_volume = df_sample['gift_volume_l'].sum()

    # If constraints can't be met, reduce sample size automatically
    if total_weight > max_weight or total_volume > max_volume:
        # Calculate how many children we can actually deliver
        weight_ratio = max_weight / total_weight if total_weight > 0 else 1
        volume_ratio = max_volume / total_volume if total_volume > 0 else 1
        max_ratio = min(weight_ratio, volume_ratio, 1.0)

        # Reduce sample size by 10% to leave some buffer
        adjusted_size = int(len(df_sample) * max_ratio * 0.9)
        adjusted_size = max(10, adjusted_size)  # At least 10 children

        df_sample = df_sample.head(adjusted_size)

    # Add North Pole as starting point
    locations = [(north_pole_lat, north_pole_lon)] + list(zip(df_sample['latitude'], df_sample['longitude']))
    weights = [0] + df_sample['gift_weight_kg'].tolist()
    volumes = [0] + df_sample['gift_volume_l'].tolist()

    # Create distance matrix
    distance_matrix = create_distance_matrix(locations)

    # Convert to integers for OR-Tools (multiply by 1000 to preserve precision)
    distance_matrix_int = (distance_matrix * 1000).astype(int)
    weights_int = (np.array(weights) * 1000).astype(int)
    volumes_int = (np.array(volumes) * 1000).astype(int)

    # Create routing model
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix_int), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Create distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix_int[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add weight capacity constraint with some slack
    def weight_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return weights_int[from_node]

    weight_callback_index = routing.RegisterUnaryTransitCallback(weight_callback)
    routing.AddDimensionWithVehicleCapacity(
        weight_callback_index,
        int(max_weight * 100),  # Add 10% slack
        [int(max_weight * 1000)],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Weight'
    )

    # Add volume capacity constraint with some slack
    def volume_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return volumes_int[from_node]

    volume_callback_index = routing.RegisterUnaryTransitCallback(volume_callback)
    routing.AddDimensionWithVehicleCapacity(
        volume_callback_index,
        int(max_volume * 100),  # Add 10% slack
        [int(max_volume * 1000)],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Volume'
    )

    # Set search parameters with more relaxed settings
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC
    )
    search_parameters.time_limit.seconds = 60
    search_parameters.log_search = False

    # Solve
    solution = routing.SolveWithParameters(search_parameters)

    # If no solution found, try with greedy fallback
    if not solution:
        return optimize_route_greedy(df_sample, max_weight, max_volume, north_pole_lat, north_pole_lon)

    # Extract route from solution
    route = []
    index = routing.Start(0)
    total_distance = 0
    total_weight = 0
    total_volume = 0

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node > 0:  # Skip North Pole start
            child_idx = df_sample.index[node - 1]
            route.append({
                'child_id': int(df_sample.loc[child_idx, 'child_id']),
                'name': df_sample.loc[child_idx, 'name'],
                'city': df_sample.loc[child_idx, 'city'],
                'country': df_sample.loc[child_idx, 'country'],
                'latitude': float(df_sample.loc[child_idx, 'latitude']),
                'longitude': float(df_sample.loc[child_idx, 'longitude']),
                'wishlist_item': df_sample.loc[child_idx, 'wishlist_item'],
                'gift_weight_kg': float(df_sample.loc[child_idx, 'gift_weight_kg']),
                'gift_volume_l': float(df_sample.loc[child_idx, 'gift_volume_l']),
                'nice': bool(df_sample.loc[child_idx, 'nice']),
                'order': len(route) + 1
            })
            total_weight += weights[node]
            total_volume += volumes[node]

        previous_index = index
        index = solution.Value(routing.NextVar(index))
        total_distance += routing.GetArcCostForVehicle(previous_index, index, 0) / 1000.0

    # Calculate delivery time
    delivery_time_hours = total_distance / SLEIGH_SPEED_KMH

    # Calculate metrics
    naughty_count = len([r for r in route if not r['nice']])
    nice_count = len(route) - naughty_count

    metrics = {
        'total_distance_km': round(total_distance, 2),
        'total_weight_kg': round(total_weight, 2),
        'total_volume_l': round(total_volume, 2),
        'delivery_time_hours': round(delivery_time_hours, 2),
        'children_delivered': len(route),
        'nice_children': nice_count,
        'naughty_children': naughty_count,
        'weight_utilization_percent': round((total_weight / max_weight) * 100, 1),
        'volume_utilization_percent': round((total_volume / max_volume) * 100, 1),
        'time_constraint_met': delivery_time_hours <= 7,  # 22:00 to 05:00 = 7 hours
        'avg_distance_per_child': round(total_distance / len(route), 2) if route else 0
    }

    return route, metrics


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/load_data', methods=['GET'])
def api_load_data():
    """Load and return basic dataset info"""
    try:
        df = load_data()
        data_store['children'] = df

        info = {
            'total_children': len(df),
            'nice_children': int(df['nice'].sum()),
            'naughty_children': int((df['nice'] == 0).sum()),
            'total_weight_kg': round(df['gift_weight_kg'].sum(), 2),
            'total_volume_l': round(df['gift_volume_l'].sum(), 2),
            'countries': df['country'].nunique(),
            'cities': df['city'].nunique()
        }

        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    """Optimize the delivery route"""
    try:
        params = request.get_json()
        max_weight = params.get('max_weight', MAX_SLEIGH_WEIGHT)
        max_volume = params.get('max_volume', MAX_SLEIGH_VOLUME)
        sample_size = params.get('sample_size', 500)

        print(f"🎅 Optimization request: weight={max_weight}kg, volume={max_volume}L, children={sample_size}")

        # Load data if not already loaded
        if data_store['children'] is None:
            print("📂 Loading dataset...")
            df = load_data()
            data_store['children'] = df
            print(f"✅ Loaded {len(df)} children")
        else:
            print(f"✅ Using cached dataset with {len(data_store['children'])} children")

        print("🔄 Starting route optimization...")
        route, metrics = optimize_route(
            data_store['children'],
            max_weight=max_weight,
            max_volume=max_volume,
            sample_size=sample_size
        )

        if route is not None and len(route) > 0:
            data_store['route'] = route
            data_store['metrics'] = metrics
            print(f"✅ Route optimized successfully: {len(route)} stops, {metrics['total_distance_km']} km")

            return jsonify({
                'success': True,
                'route': route,
                'metrics': metrics
            })
        else:
            error_msg = 'Could not find a valid route - no children could be delivered with given constraints'
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            })
    except FileNotFoundError as e:
        error_msg = f"Dataset file not found: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg})
    except Exception as e:
        import traceback
        error_msg = f"Error during optimization: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/export_route', methods=['GET'])
def api_export_route():
    """Export the current route as JSON"""
    if data_store['route'] is None:
        return jsonify({'success': False, 'error': 'No route available'})

    return jsonify({
        'success': True,
        'route': data_store['route'],
        'metrics': data_store['metrics']
    })


if __name__ == '__main__':
    print("="*60)
    print("🎅 Santa's Delivery Route Optimizer")
    print("="*60)
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📁 Script directory: {SCRIPT_DIR}")

    # Check for CSV file
    csv_path = os.path.join(SCRIPT_DIR, 'santa_children_dataset_50k.csv')
    if os.path.exists(csv_path):
        csv_size = os.path.getsize(csv_path) / 1024 / 1024
        print(f"✅ Found dataset: santa_children_dataset_50k.csv ({csv_size:.1f} MB)")
    else:
        print(f"⚠️  Dataset not found at: {csv_path}")
        print(f"⚠️  Will use demo dataset (100 children) instead")

    print("="*60)
    print("📍 Access the app at: http://localhost:5000")
    print("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000)
