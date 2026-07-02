import requests

# public OpenFoodFacts API
BASE_URL = "https://world.openfoodfacts.org"

# i used this headers cause it was kinda refusing to pull data it looked like a bot or something to them 
HEADERS = {
    "User-Agent" :  "InventoryLabApp/1.0 (student project, contact: sam@example.com"
}


def fetch_product_by_barcode(barcode):
    """Looks up a single product by barcode. Returns a dict, or None if not found / request failed."""
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Couldn't reach OpenFoodFacts: {e}")
        return None

    if response.status_code != 200:
        print(f"OpenFoodFacts returned status {response.status_code} for barcode {barcode}")
        return None

    data = response.json()

    # when a barcode isn't found, "product" comes back as an empty dict,
    # so that's a more reliable check than looking for a "status" field
    product = data.get("product")
    if not product:
        return None

    product["code"] = data.get("code", barcode)
    return product


def fetch_product_by_name(name):
    """Searches by product name and returns the first match. Not the most precise but good enough here."""
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "json": 1,
        "page_size": 1
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Couldn't reach OpenFoodFacts: {e}")
        return None

    if response.status_code != 200:
        print(f"OpenFoodFacts returned status {response.status_code} for search '{name}'")
        return None

    data = response.json()
    products = data.get("products", [])

    if not products:
        return None

    return products[0]