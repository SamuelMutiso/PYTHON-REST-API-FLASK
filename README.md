# Inventory Management System

Summative lab for my Python/Flask class. Small REST API for a retail
company's admin portal — add, view, update, and delete inventory items,
plus pull real product data from the OpenFoodFacts API by barcode or name
instead of typing everything by hand.

Three main pieces:

1. `app.py` - the Flask REST API
2. `external_api.py` - talks to OpenFoodFacts
3. `cli.py` - command line tool that talks to the Flask API

## Setup

```bash
git clone https://github.com/SamuelMutiso/lab-inventory-api.git
cd lab-inventory-api
pipenv install
pipenv shell
```

## Running the API

```bash
python app.py
```

Starts the Flask dev server at `http://127.0.0.1:5000` with debug mode on.

## Running the CLI

Needs the Flask server running in a separate terminal first:

```bash
python cli.py
```

## API Endpoints

| Method | Route                 | Description                                            |
|--------|------------------------|----------------------------------------------------------|
| GET    | `/inventory`           | Get all items, supports `?category=` filter              |
| GET    | `/inventory/<id>`      | Get a single item                                         |
| POST   | `/inventory`           | Add a new item manually (`name` required)                 |
| PATCH  | `/inventory/<id>`      | Update one or more fields on an item                       |
| DELETE | `/inventory/<id>`      | Remove an item                                             |
| GET    | `/inventory/low-stock` | Items under a stock threshold, default 10                 |
| GET    | `/inventory/lookup`    | Preview a product from OpenFoodFacts, doesn't save it      |
| POST   | `/inventory/import`    | Fetch from OpenFoodFacts and add to inventory              |

### Example item

```json
{
  "id": 1,
  "name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "0025293001165",
  "category": "Dairy Alternatives",
  "price": 3.99,
  "stock": 25,
  "ingredients": "Filtered water, almonds, cane sugar, ...",
  "source": "manual"
}
```

### Example requests

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Sea Salt Chips", "brand": "Kettle", "price": 3.49, "stock": 15}'

curl -X POST http://127.0.0.1:5000/inventory/import \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3017620422003", "price": 2.99, "stock": 12}'
```

## Testing

```bash
pipenv run pytest -v
```

Tests live under `tests/` and use Flask's test client plus `unittest.mock`
to fake out OpenFoodFacts calls, so the suite doesn't need internet access
to pass.

## Notes

- Inventory is just a Python list in memory, resets on server restart.
