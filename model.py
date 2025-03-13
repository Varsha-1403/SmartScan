def analyze_food_recommendation(food_data):
    unhealthy_threshold = {
        "calories": 500,
        "sugars": 10,
        "sodium": 500
    }

    recommendation = "Safe to eat"

    if (food_data["calories"] > unhealthy_threshold["calories"] or 
        food_data["sugars"] > unhealthy_threshold["sugars"] or 
        food_data["sodium"] > unhealthy_threshold["sodium"]):
        recommendation = "Not recommended! Try a healthier option."

    return recommendation
