from flask import Flask, jsonify, request
from external_api import fetch_product_by_barcode, fetch_product_by_name

app = Flask(__name__)


inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "0025293001165",
        "category": "Dairy Alternatives",
        "price": 3.99,
        "stock": 25,
        "ingredients": "Filtered water, almonds, cane sugar, sea salt, ...",
        "source": "manual"
    },
    {
        "id": 2,
        "name": "Classic Peanut Butter",
        "brand": "Jif",
        "barcode": "0051500255162",
        "category": "Spreads",
        "price": 4.49,
        "stock": 40,
        "ingredients": "Roasted peanuts, sugar, molasses, salt",
        "source": "manual"
    }
]

# every new item needs a unique id  this  just hands out
# the next available number instead of checking max IDS every time
next_id = 3


def find_item(item_id):
    """Loops through inventory and returns the item with a matching id, or None."""
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


@app.route("/inventory", methods=["GET"])
def get_inventory():
    # optional filter,  EXAMPOLE LIKE /inventory?category=Spreads
    category = request.args.get("category")
    if category:
        filtered = [i for i in inventory if i["category"].lower() == category.lower()]
        return jsonify(filtered), 200
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": f"item {item_id} not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    data = request.get_json(silent=True)

    if not data or not data.get("name"):
        return jsonify({"error": "name is required to add an item"}), 400

    new_item = {
        "id": next_id,
        "name": data.get("name"),
        "brand": data.get("brand", "Unknown"),
        "barcode": data.get("barcode", ""),
        "category": data.get("category", "Uncategorized"),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
        "ingredients": data.get("ingredients", ""),
        "source": "manual"
    }

    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": f"item {item_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no update data provided"}), 400

    # only touch fields that were actually sent
    updatable_fields = ["name", "brand", "barcode", "category", "price", "stock", "ingredients"]
    for field in updatable_fields:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": f"item {item_id} not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"item {item_id} deleted"}), 200


# extra helper routes not required CRUD but useful for the CLI thought of adding it 

@app.route("/inventory/low-stock", methods=["GET"])
def low_stock():
    """Returns items below a stock threshold. Default is 10, override with ?threshold=5"""
    threshold = request.args.get("threshold", default=10, type=int)
    low = [i for i in inventory if i["stock"] < threshold]
    return jsonify(low), 200


@app.route("/inventory/lookup", methods=["GET"])
def lookup_external():
    
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        result = fetch_product_by_barcode(barcode)
    elif name:
        result = fetch_product_by_name(name)
    else:
        return jsonify({"error": "provide a barcode or name query param"}), 400

    if result is None:
        return jsonify({"error": "no product found"}), 404

    return jsonify(result), 200


@app.route("/inventory/import", methods=["POST"])
def import_from_external():
    
    global next_id
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "request body required"}), 400

    barcode = data.get("barcode")
    name = data.get("name")

    if barcode:
        product = fetch_product_by_barcode(barcode)
    elif name:
        product = fetch_product_by_name(name)
    else:
        return jsonify({"error": "provide a barcode or name in the request body"}), 400

    if product is None:
        return jsonify({"error": "could not find that product on OpenFoodFacts"}), 404

    new_item = {
        "id": next_id,
        "name": product.get("product_name", "Unknown product"),
        "brand": product.get("brands", "Unknown"),
        "barcode": product.get("code", barcode or ""),
        "category": product.get("categories", "Uncategorized"),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
        "ingredients": product.get("ingredients_text", ""),
        "source": "openfoodfacts"
    }

    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(debug=True)