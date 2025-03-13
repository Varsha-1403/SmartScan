from flask import Flask, request, render_template, jsonify, send_from_directory
from pymongo import MongoClient
import os
import requests
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
import random

app = Flask(__name__, static_folder="static", template_folder="templates")


USER_DATA_FILE = "user_data.json"
client = MongoClient("mongodb://localhost:27017/")  # Change this to your MongoDB URI
db = client["smart_scan_db"]  # Database name
users_collection = db["users"]  # Collection name
emailRegisterd=""

# ✅ Load user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {"calories": 0, "protein": 0, "carbohydrates": 0, "bmi": 0, "age": 0, "gender": "", "history": []}

# ✅ Save user data
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/signup")
def signup():
    return render_template("signup.html")

def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Save login details in MongoDB
    user_data = {"email": email, "password": password}  # Store plain text (not recommended for real apps)
    users_collection.insert_one(user_data)

    return jsonify({"message": "Login successful", "email": email}), 201

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate input
    if not name or len(name) < 3:
        return jsonify({"message": "Name must be at least 3 characters"}), 400
    if not email or "@" not in email:
        return jsonify({"message": "Invalid email format"}), 400
    if not password or len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    # Check if email already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "Email already registered"}), 400

   
    # Store user data
    users_collection.insert_one({"name": name, "email": email, "password": password})
    return render_template("health.html")

    
    

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ✅ Save BMI data
@app.route("/save_bmi", methods=["POST"])
def save_bmi():
    user_data = load_user_data()
    data = request.json
    print(data)
    user_data["bmi"] = data.get("bmi", 0)
    user_data["calories"] = data.get("calories", 0)
    user_data["protein"] = data.get("protein", 0)
    user_data["carbohydrates"] = data.get("carbohydrates", 0)
    user_data["age"] = data.get("age", 0)
    user_data["gender"] = data.get("gender", "")
    save_user_data(user_data)
    return jsonify({"message": "✅ BMI data saved."}), 200

# ✅ Recommend healthier alternatives
def recommend_food(user_needs, current_product_name, current_product_nutrition, num_recommendations=5):
    response = requests.get("https://world.openfoodfacts.org/api/v2/search?categories=healthy-foods&fields=product_name,image_url,ingredients_text,nutriments")
    if response.status_code != 200:
        return None

    food_items = response.json().get("products", [])
    food_data = []

    # Filter out the current product and unhealthy items
    filtered_items = []
    for item in food_items:
        if item.get("product_name", "").lower() != current_product_name.lower():
            food_data.append([
                float(item.get("nutriments", {}).get("energy-kcal_100g", 0)),
                float(item.get("nutriments", {}).get("proteins_100g", 0)),
                float(item.get("nutriments", {}).get("carbohydrates_100g", 0))
            ])
            filtered_items.append(item)

    if not food_data:
        return None

    food_data = np.array(food_data)
    knn = NearestNeighbors(n_neighbors=10)  # Find top 10 nearest neighbors
    knn.fit(food_data)

    _, indices = knn.kneighbors([user_needs])
    recommended_items = [filtered_items[index] for index in indices[0]]

    # Randomly select 5 unique recommendations
    unique_recommendations = random.sample(recommended_items, min(num_recommendations, len(recommended_items)))

    # Add "Why" explanation for each recommendation
    for item in unique_recommendations:
        item["why"] = generate_why_explanation(current_product_nutrition, item)

    return unique_recommendations

# ✅ Generate "Why" explanation for each recommendation
def generate_why_explanation(current_product_nutrition, recommended_item):
    why_explanation = []
    recommended_calories = float(recommended_item.get("nutriments", {}).get("energy-kcal_100g", 0))
    recommended_protein = float(recommended_item.get("nutriments", {}).get("proteins_100g", 0))
    recommended_carbs = float(recommended_item.get("nutriments", {}).get("carbohydrates_100g", 0))

    if recommended_calories < current_product_nutrition["calories"]:
        why_explanation.append("lower in calories")
    if recommended_protein > current_product_nutrition["protein"]:
        why_explanation.append("higher in protein")
    if recommended_carbs < current_product_nutrition["carbs"]:
        why_explanation.append("lower in carbs")

    if not why_explanation:
        return "This product is a healthier alternative."
    return f"This product is {', '.join(why_explanation)}."

# ✅ API to process food & suggest healthier alternatives
@app.route("/process_food", methods=["POST"])
def process_food():
    user_data = load_user_data()
    data = request.json
    barcode = data.get("barcode")
    quantity = float(data.get("quantity", 1))  

    # ✅ Fetch food details using Open Food Facts API
    response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
    if response.status_code != 200:
        return jsonify({"message": "❌ Product not found."}), 400

    product_data = response.json().get("product", {})
    if not product_data:
        return jsonify({"message": "❌ Product not found."}), 400

    # ✅ Extract food details (scaled by quantity)
    food_info = {
        "name": product_data.get("product_name", "Unknown"),
        "calories": float(product_data.get("nutriments", {}).get("energy-kcal_100g", 0)) * quantity,
        "protein": float(product_data.get("nutriments", {}).get("proteins_100g", 0)) * quantity,
        "carbs": float(product_data.get("nutriments", {}).get("carbohydrates_100g", 0)) * quantity,
        "ingredients": product_data.get("ingredients_text", "No ingredients available"),
        "image": product_data.get("image_url", "")
    }

    # ✅ Calculate recommended daily intake based on user BMI, age, and gender
    bmi = user_data["bmi"]
    age = user_data["age"]
    gender = user_data["gender"]

    if gender == "Male":
        recommended_calories = user_data["calories"] * 0.3
        recommended_protein = user_data["protein"] * 0.2
        recommended_carbs = user_data["carbohydrates"] * 0.3
    else:
        recommended_calories = user_data["calories"] * 0.25
        recommended_protein = user_data["protein"] * 0.15
        recommended_carbs = user_data["carbohydrates"] * 0.25

    # ✅ Check if the food is safe based on health severity
    severity = 0
    warnings = []
    if food_info["calories"] > recommended_calories:
        severity += 2
        warnings.append("⚠️ High in calories. Consider reducing portion size.")
    if food_info["carbs"] > recommended_carbs:
        severity += 1
        warnings.append("⚠️ High in carbohydrates. Choose a low-carb alternative.")
    if food_info["protein"] < recommended_protein:
        severity += 1
        warnings.append("⚠️ Low in protein. Consider a high-protein alternative.")

    if severity == 0:
        status_message = "✅ Yes, you can consume this item."
        alternative_foods = None
    else:
        status_message = "❌ This product is not suitable for you."
        # Recommend multiple alternatives based on BMI, age, and gender
        alternative_foods = recommend_food([recommended_calories, recommended_protein, recommended_carbs], food_info["name"], food_info)

    # ✅ Generate health scale visualization
    health_scale = {
        "calories": (food_info["calories"] / recommended_calories) * 100,
        "protein": (food_info["protein"] / recommended_protein) * 100,
        "carbs": (food_info["carbs"] / recommended_carbs) * 100
    }

    return jsonify({
        "message": status_message,
        "warnings": warnings,
        "food_info": food_info,
        "alternatives": alternative_foods,
        "health_scale": health_scale
    })





if __name__ == "__main__":
    app.run(debug=True)
