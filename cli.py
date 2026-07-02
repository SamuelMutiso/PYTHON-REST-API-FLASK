import requests

API_URL = "http://127.0.0.1:5000/inventory"


def view_all_items():
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("Couldn't fetch inventory, is the server running?")
        return None

    items = response.json()
    if not items:
        print("Inventory is empty.")
    for item in items:
        print(f"[{item['id']}] {item['name']} - {item['brand']} | ${item['price']} | stock: {item['stock']}")
    return items


def view_item(item_id):
    response = requests.get(f"{API_URL}/{item_id}")
    if response.status_code != 200:
        print(f"Item {item_id} not found.")
        return None
    item = response.json()
    print(item)
    return item


def add_item(name, brand, category, price, stock, barcode=""):
    payload = {
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "stock": stock,
        "barcode": barcode
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 201:
        print("Item added!")
        return response.json()
    print("Failed to add item:", response.json().get("error", "unknown error"))
    return None


def update_item(item_id, updates):
    response = requests.patch(f"{API_URL}/{item_id}", json=updates)
    if response.status_code == 200:
        print("Item updated!")
        return response.json()
    print("Failed to update item:", response.json().get("error", "unknown error"))
    return None


def delete_item(item_id):
    response = requests.delete(f"{API_URL}/{item_id}")
    if response.status_code == 200:
        print("Item deleted.")
        return True
    print("Failed to delete item:", response.json().get("error", "unknown error"))
    return False


def import_from_api(barcode=None, name=None, price=0.0, stock=0):
    if not barcode and not name:
        print("Need a barcode or name to search.")
        return None

    payload = {"price": price, "stock": stock}
    if barcode:
        payload["barcode"] = barcode
    else:
        payload["name"] = name

    response = requests.post(f"{API_URL}/import", json=payload)
    if response.status_code == 201:
        print("Product imported from OpenFoodFacts!")
        return response.json()
    print("Import failed:", response.json().get("error", "unknown error"))
    return None


def search_external(barcode=None, name=None):
    if not barcode and not name:
        print("Need a barcode or name to search.")
        return None

    params = {"barcode": barcode} if barcode else {"name": name}
    response = requests.get(f"{API_URL}/lookup", params=params)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    print("Nothing found on OpenFoodFacts for that.")
    return None


def print_menu():
    print("\n----- Inventory Manager -----")
    print("1. View all items")
    print("2. View item by ID")
    print("3. Add new item manually")
    print("4. Import item from OpenFoodFacts")
    print("5. Update an item")
    print("6. Delete an item")
    print("7. Search OpenFoodFacts (preview only, doesn't save)")
    print("8. Exit")


def main():
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_all_items()

        elif choice == "2":
            item_id = input("Item ID: ").strip()
            if item_id.isdigit():
                view_item(int(item_id))
            else:
                print("That's not a valid ID.")

        elif choice == "3":
            name = input("Name: ").strip()
            brand = input("Brand: ").strip()
            category = input("Category: ").strip()
            try:
                price = float(input("Price: ").strip())
                stock = int(input("Stock: ").strip())
            except ValueError:
                print("Price/stock need to be numbers, try again.")
                continue
            barcode = input("Barcode (optional): ").strip()
            add_item(name, brand, category, price, stock, barcode)

        elif choice == "4":
            mode = input("Search by (b)arcode or (n)ame? ").strip().lower()
            try:
                price = float(input("Price to set (0 if unknown): ").strip() or 0)
                stock = int(input("Starting stock: ").strip() or 0)
            except ValueError:
                print("Price/stock need to be numbers, try again.")
                continue
            if mode == "b":
                import_from_api(barcode=input("Barcode: ").strip(), price=price, stock=stock)
            else:
                import_from_api(name=input("Product name: ").strip(), price=price, stock=stock)

        elif choice == "5":
            item_id = input("Item ID to update: ").strip()
            if not item_id.isdigit():
                print("That's not a valid ID.")
                continue
            field = input("Field to update (price/stock/name/brand/category): ").strip()
            value = input("New value: ").strip()
            try:
                if field == "price":
                    value = float(value)
                elif field == "stock":
                    value = int(value)
            except ValueError:
                print("That value doesn't match the field type.")
                continue
            update_item(int(item_id), {field: value})

        elif choice == "6":
            item_id = input("Item ID to delete: ").strip()
            if item_id.isdigit():
                delete_item(int(item_id))
            else:
                print("That's not a valid ID.")

        elif choice == "7":
            mode = input("Search by (b)arcode or (n)ame? ").strip().lower()
            if mode == "b":
                search_external(barcode=input("Barcode: ").strip())
            else:
                search_external(name=input("Product name: ").strip())

        elif choice == "8":
            print("Bye!")
            break

        else:
            print("Not a valid option, try again.")


if __name__ == "__main__":
    main()