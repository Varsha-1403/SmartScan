import requests

def fetch_food_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    data = response.json()

    if data.get("status") == 1:
        product = data["product"]
        return {
            "name": product.get("product_name", "Unknown"),
            "calories": product.get("nutriments", {}).get("energy-kcal_100g", 0),
            "proteins": product.get("nutriments", {}).get("proteins_100g", 0),
            "carbohydrates": product.get("nutriments", {}).get("carbohydrates_100g", 0),
            "sugars": product.get("nutriments", {}).get("sugars_100g", 0),
            "fat": product.get("nutriments", {}).get("fat_100g", 0),
            "fiber": product.get("nutriments", {}).get("fiber_100g", 0),
            "sodium": product.get("nutriments", {}).get("sodium_100g", 0),
        }
    return None
