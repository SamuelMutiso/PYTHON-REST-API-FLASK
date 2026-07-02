import pytest
import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True

    # reset the "database" before each test so tests don't affect each other
    app_module.inventory.clear()
    app_module.inventory.extend([
        {
            "id": 1,
            "name": "Test Milk",
            "brand": "TestBrand",
            "barcode": "1111111111",
            "category": "Dairy",
            "price": 2.50,
            "stock": 10,
            "ingredients": "milk",
            "source": "manual"
        }
    ])
    app_module.next_id = 2

    with app_module.app.test_client() as test_client:
        yield test_client


def test_get_all_items(client):
    res = client.get("/inventory")
    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_get_single_item(client):
    res = client.get("/inventory/1")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Test Milk"


def test_get_item_not_found(client):
    res = client.get("/inventory/999")
    assert res.status_code == 404


def test_filter_by_category(client):
    res = client.get("/inventory?category=Dairy")
    assert res.status_code == 200
    assert len(res.get_json()) == 1

    res = client.get("/inventory?category=Snacks")
    assert res.get_json() == []


def test_add_item(client):
    payload = {"name": "New Item", "brand": "Brand X", "price": 5.0, "stock": 3}
    res = client.post("/inventory", json=payload)
    assert res.status_code == 201
    assert res.get_json()["name"] == "New Item"
    assert len(app_module.inventory) == 2


def test_add_item_missing_name(client):
    res = client.post("/inventory", json={"brand": "no name here"})
    assert res.status_code == 400


def test_update_item(client):
    res = client.patch("/inventory/1", json={"stock": 99})
    assert res.status_code == 200
    assert res.get_json()["stock"] == 99


def test_update_item_no_body(client):
    res = client.patch("/inventory/1", json=None)
    assert res.status_code == 400


def test_update_item_not_found(client):
    res = client.patch("/inventory/999", json={"stock": 1})
    assert res.status_code == 404


def test_delete_item(client):
    res = client.delete("/inventory/1")
    assert res.status_code == 200
    assert len(app_module.inventory) == 0


def test_delete_item_not_found(client):
    res = client.delete("/inventory/999")
    assert res.status_code == 404


def test_low_stock_route(client):
    res = client.get("/inventory/low-stock?threshold=20")
    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_low_stock_default_threshold(client):
    res = client.get("/inventory/low-stock")
    assert res.status_code == 200
    assert len(res.get_json()) == 0


def test_lookup_requires_param(client):
    res = client.get("/inventory/lookup")
    assert res.status_code == 400


def test_lookup_external_success(client, monkeypatch):
    fake_product = {"product_name": "Fake Product", "brands": "FakeBrand"}
    monkeypatch.setattr(app_module, "fetch_product_by_barcode", lambda code: fake_product)

    res = client.get("/inventory/lookup?barcode=123456")
    assert res.status_code == 200
    assert res.get_json()["product_name"] == "Fake Product"


def test_lookup_external_by_name(client, monkeypatch):
    fake_product = {"product_name": "Found By Name"}
    monkeypatch.setattr(app_module, "fetch_product_by_name", lambda name: fake_product)

    res = client.get("/inventory/lookup?name=granola")
    assert res.status_code == 200
    assert res.get_json()["product_name"] == "Found By Name"


def test_lookup_external_not_found(client, monkeypatch):
    monkeypatch.setattr(app_module, "fetch_product_by_barcode", lambda code: None)

    res = client.get("/inventory/lookup?barcode=000000")
    assert res.status_code == 404


def test_import_from_external(client, monkeypatch):
    fake_product = {
        "product_name": "Imported Snack",
        "brands": "SnackCo",
        "code": "999999",
        "ingredients_text": "corn, salt",
        "categories": "Snacks"
    }
    monkeypatch.setattr(app_module, "fetch_product_by_barcode", lambda code: fake_product)

    res = client.post("/inventory/import", json={"barcode": "999999", "price": 1.99, "stock": 5})
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Imported Snack"
    assert data["source"] == "openfoodfacts"
    assert len(app_module.inventory) == 2


def test_import_not_found(client, monkeypatch):
    monkeypatch.setattr(app_module, "fetch_product_by_barcode", lambda code: None)
    res = client.post("/inventory/import", json={"barcode": "000000"})
    assert res.status_code == 404


def test_import_requires_barcode_or_name(client):
    res = client.post("/inventory/import", json={"price": 1.0})
    assert res.status_code == 400