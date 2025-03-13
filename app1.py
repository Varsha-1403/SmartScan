from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import random
import os
from dotenv import load_dotenv
import jwt
import datetime
from bson.objectid import ObjectId
from PIL import Image
from pyzbar.pyzbar import decode


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "mysecret")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# MongoDB Connection
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client["nutrition_assistant"]
    users_collection = db["users"]
    bmi_collection = db["bmi_data"]
    nutrients_collection = db["nutrients"]
    
    # Test the connection
    client.admin.command('ping')
    
    print("Database connected successfully!")

except Exception as e:
    print(f"Error connecting to the database: {e}")
global_user_email = None

# Open Food Facts API
FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v0/product/{}.json"

# Home Route
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

# User Signup Route
@app.route("/signup-creds", methods=["POST"])
def signupCreds():
    global global_user_email
    data = request.json
    username = data.get("name")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return jsonify({"error": "All fields are required"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password, "email": email})
    print(users_collection)
    
    global_user_email = email
     # Store the registered email globally
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/health", methods=["GET"])
def health():
    return render_template("health.html")

# User Login with JWT
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    print(email)
    print(password)
    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    return jsonify({
    "message": "Login successful",
    "data": {
        "email": email,
        "user_id": str(user["_id"])  # Convert ObjectId to string
    }
}), 200



# Forgot Password Page Route
@app.route("/forgot-password", methods=["GET"])
def forgot_password():
    return render_template("forgot-password.html")

# Reset Password Route
@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    new_password = data.get("newPassword")

    if not email or not new_password:
        return jsonify({"error": "Email and new password are required"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Hash the new password
    hashed_password = generate_password_hash(new_password)

    # Update the user's password in the database
    users_collection.update_one(
        {"email": email},
        {"$set": {"password": hashed_password}}
    )

    return jsonify({"message": "Password reset successfully"}), 200

@app.route("/process_food", methods=["POST"])
def process_food():
    try:
        # ✅ Print received request data
        data = request.json
        print("Received Data:", data)

        # ✅ Validate required fields
        if not data or "barcode" not in data or "userId" not in data:
            return jsonify({"error": "Missing required fields: barcode and userId"}), 400

        userId = data.get('userId')
        barcode = data.get("barcode")
        quantity = float(data.get("quantity", 1))  

        # ✅ Fetch user data from MongoDB
        user = users_collection.find_one({"_id": ObjectId(userId)}, {"password": 0})
        bmi_data = bmi_collection.find_one({"userId": userId})  

        if not user:
            return jsonify({"message": "❌ User not found."}), 400 #67bffa54c82c7171e71a6031
        
        print("User Data:", user)

        # ✅ Fetch food details using Open Food Facts API
        response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
        
        if response.status_code != 200:
            return jsonify({"message": "❌ Product not found."}), 400
        
        product_data = response.json().get("product", {})
        if not product_data:
            return jsonify({"message": "❌ Product not found."}), 400

        # print("Product Data:", product_data)

        # ✅ Extract food details (scaled by quantity)
        nutriments = product_data.get("nutriments", {})
        food_info = {
            "name": product_data.get("product_name", "Unknown"),
            "calories": float(nutriments.get("energy-kcal_100g", 0)) * quantity,
            "protein": float(nutriments.get("proteins_100g", 0)) * quantity,
            "carbs": float(nutriments.get("carbohydrates_100g", 0)) * quantity,
            "ingredients": product_data.get("ingredients_text", "No ingredients available"),
            "image": product_data.get("image_url", "")
        }

        print("Extracted Food Info:", food_info)

        # ✅ Fetch user BMI data
        bmi = float(bmi_data.get("bmi", 22))  # Convert to float  # Default BMI if not found
        age = bmi_data.get("age", 30)  # Default age if not found
        gender = bmi_data.get("gender", "Male")  # Default gender

        # Default daily intake values based on dietary guidelines
        base_calories = 2500 if gender == "Male" else 2000
        base_protein = 56 if gender == "Male" else 46
        base_carbs = 300 if gender == "Male" else 250

        # Adjust based on BMI
        bmi_factor = 1.2 if bmi < 18.5 else (1.0 if 18.5 <= bmi <= 24.9 else 0.8)
        
        recommended_calories = base_calories * bmi_factor
        recommended_protein = base_protein * bmi_factor
        recommended_carbs = base_carbs * bmi_factor

        # ✅ Check if the food is safe
        severity = 0
        warnings = []
        print(food_info["calories"])
        print(food_info["carbs"])
        print(food_info["protein"])
        if food_info["calories"] >= recommended_calories:
            severity += 2
            warnings.append("⚠️ High in calories. Consider reducing portion size.")
        if food_info["carbs"] >= recommended_carbs:
            severity += 1
            warnings.append("⚠️ High in carbohydrates. Choose a low-carb alternative.")
        if food_info["protein"] < recommended_protein:
            severity += 1
            warnings.append("⚠️ Low in protein. Consider a high-protein alternative.")

        status_message = "✅ Yes, you can consume this item." if severity == 0 else "❌ This product is not suitable for you."
       
        # ✅ Generate health scale
        health_scale = {
            "calories": (food_info["calories"] / recommended_calories) * 100 if recommended_calories else 0,
            "protein": (food_info["protein"] / recommended_protein) * 100 if recommended_protein else 0,
            "carbs": (food_info["carbs"] / recommended_carbs) * 100 if recommended_carbs else 0
        }

        # ✅ Return the final response
        return jsonify({
            "food_info": food_info,
            "recommended_intake": {
                "calories": recommended_calories,
                "protein": recommended_protein,
                "carbs": recommended_carbs
            },
            "health_status": status_message,
            "warnings": warnings,
            "health_scale": health_scale
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


# Recommend Healthier Food Route
@app.route("/recommend_food", methods=["POST"])
def recommend_food():
    # category = request.args.get("category", "snacks")
    data = request.json
    print(data)
    category = data.get("food_name")
    print(category)
    response = requests.get(f"https://world.openfoodfacts.org/category/{category}.json")
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch category data"}), 500
    
    products = response.json().get("products", [])
    
    if not products:
        return jsonify({"error": "No products found in this category"}), 404
    
    recommended = random.sample(products, min(5, len(products)))
    recommendations = [{
        "product_name": p.get("product_name", "Unknown"),
        "calories": p.get("nutriments", {}).get("energy-kcal", 0)
    } for p in recommended]
    
    return jsonify(recommendations)
@app.route("/save_bmi", methods=["POST"])
def save_bmi():
    data = request.json
    print(data)
    height = data.get("height")
    weight = data.get("weight")
    gender=data.get("gender")
    age=data.get("age")
    userId=data.get("userId")
    category=data.get("category")
    
    if not height or not weight:
        return jsonify({"error": "Height and weight are required"}), 400
    
    try:
        height = float(height)
        weight = float(weight)
        heightInMeters = height / 100
        bmiValue = weight/ (heightInMeters ** 2)
        bmi="{:.2f}".format(bmiValue)
    except ValueError:
        return jsonify({"error": "Invalid height or weight"}), 400
    
    bmi_collection.insert_one({ "userId":userId,"height": height, "weight": weight, "bmi": bmi,"category":category,"age":age,"gender":gender})
    return jsonify({"message": "BMI data saved successfully", "bmi": bmi}), 201


@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")
@app.route("/profile", methods=["GET"])
def profile():
    return render_template("profile.html")
@app.route("/bmi",methods=["GET"])
def bmi():
    return render_template("bmi.html")
@app.route("/nutrition",methods=["GET"])
def nutrition():
    return render_template("nutrition.html")



@app.route("/profile-details/<user_id>", methods=["GET"])
def profile_details(user_id):
    try:
        print("Fetching profile for user:", user_id)

        # Validate ObjectId
        if not ObjectId.is_valid(user_id):
            return jsonify({"error": "Invalid user ID format"}), 400

        # Fetch user data
        user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})  # Exclude password
        bmi = bmi_collection.find_one({"userId": user_id})  # Fetch BMI data

        if not user:
            return jsonify({"error": "User not found"}), 404
        print(bmi)
        # Convert ObjectId fields to strings
        user["_id"] = str(user["_id"])
        if bmi and "_id" in bmi:
            bmi["_id"] = str(bmi["_id"])

        return jsonify({"profile": user, "bmi": bmi or None}), 200

    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 500


@app.route("/upload_barcode", methods=["POST"])
def upload_barcode():
    if "barcode_image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["barcode_image"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Open the image using PIL
        image = Image.open(file_path)

        # Decode the barcode
        barcodes = decode(image)
        
        if not barcodes:
            return jsonify({"error": "No barcode detected"}), 400

        barcode_data = [{"type": barcode.type, "data": barcode.data.decode("utf-8")} for barcode in barcodes]

        return jsonify({"success": True, "barcodes": barcode_data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Remove the uploaded file after processing
        os.remove(file_path)

@app.route("/save_consumed_food", methods=["POST"])
def save_consumed_food():
    try:
        data = request.json
        print("Received consumed food data:", data)

        # ✅ Validate required fields
        if not data or "userId" not in data or "foodName" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # ✅ Save to MongoDB nutrients collection
        nutrients_collection.insert_one({
            "userId": data["userId"],
            "foodName": data["foodName"],
            "calories": data["calories"],
            "protein": data["protein"],
            "carbs": data["carbs"],
            "image": data["image"],
            "timestamp": datetime.datetime.utcnow()
        })

        return jsonify({"success": True, "message": "Consumed food saved successfully!"})

    except Exception as e:
        print("Error saving consumed food:", str(e))
        return jsonify({"error": str(e)}), 500
def serialize_document(doc):
    """ Convert MongoDB document to JSON serializable format """
    if doc:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc

@app.route("/older-adults")
def older_adults():
    return render_template("older-adults.html") 

@app.route('/get_bmi_data/<userId>', methods=['GET'])
def get_bmi_data(userId):
    if not userId:
        return jsonify({"error": "User ID is required"}), 400

    bmi = bmi_collection.find_one({"userId": userId})
    nutritions = nutrients_collection.find_one({"userId": userId})

    if not bmi and not nutritions:
        return jsonify({"error": "No data found for the given user"}), 404

    return jsonify({
        "message": "Data retrieved successfully",
        "data": {
            "bmi": serialize_document(bmi),
            "nutritions": serialize_document(nutritions)
        }
    }), 200
@app.route('/get_bmi_data_only/<userId>', methods=['GET'])
def get_bmi_data_only(userId):
    if not userId:
        return jsonify({"error": "User ID is required"}), 400

    bmi = bmi_collection.find_one({"userId": userId})
    bmiValue=bmi["bmi"]

    if not bmi:
        return jsonify({"error": "No data found for the given user"}), 404

    return jsonify({"success": True, "bmi":bmiValue })

if __name__ == "__main__":
    app.run(debug=True)
