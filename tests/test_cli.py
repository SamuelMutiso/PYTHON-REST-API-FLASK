from unittest.mock import patch, Mock
import cli


def test_view_all_items(capsys):
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = [
        {"id": 1, "name": "Chips", "brand": "Lays", "price": 3.0, "stock": 10}
    ]

    with patch("cli.requests.get", return_value=fake_response):
        items = cli.view_all_items()

    assert items[0]["name"] == "Chips"
    captured = capsys.readouterr()
    assert "Chips" in captured.out


def test_view_all_items_server_down():
    fake_response = Mock()
    fake_response.status_code = 500

    with patch("cli.requests.get", return_value=fake_response):
        result = cli.view_all_items()

    assert result is None


def test_view_item_found():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": 1, "name": "Chips"}

    with patch("cli.requests.get", return_value=fake_response):
        result = cli.view_item(1)

    assert result["name"] == "Chips"


def test_view_item_not_found():
    fake_response = Mock()
    fake_response.status_code = 404

    with patch("cli.requests.get", return_value=fake_response):
        result = cli.view_item(999)

    assert result is None


def test_add_item_success():
    fake_response = Mock()
    fake_response.status_code = 201
    fake_response.json.return_value = {"id": 3, "name": "Soda"}

    with patch("cli.requests.post", return_value=fake_response):
        result = cli.add_item("Soda", "Coke", "Drinks", 1.5, 20)

    assert result["name"] == "Soda"


def test_add_item_failure():
    fake_response = Mock()
    fake_response.status_code = 400
    fake_response.json.return_value = {"error": "name is required to add an item"}

    with patch("cli.requests.post", return_value=fake_response):
        result = cli.add_item("", "Coke", "Drinks", 1.5, 20)

    assert result is None


def test_update_item():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": 1, "stock": 50}

    with patch("cli.requests.patch", return_value=fake_response):
        result = cli.update_item(1, {"stock": 50})

    assert result["stock"] == 50


def test_delete_item_success():
    fake_response = Mock()
    fake_response.status_code = 200

    with patch("cli.requests.delete", return_value=fake_response):
        result = cli.delete_item(1)

    assert result is True


def test_delete_item_failure():
    fake_response = Mock()
    fake_response.status_code = 404
    fake_response.json.return_value = {"error": "item 1 not found"}

    with patch("cli.requests.delete", return_value=fake_response):
        result = cli.delete_item(1)

    assert result is False


def test_import_from_api():
    fake_response = Mock()
    fake_response.status_code = 201
    fake_response.json.return_value = {"id": 4, "name": "Imported Thing"}

    with patch("cli.requests.post", return_value=fake_response):
        result = cli.import_from_api(barcode="123", price=2.0, stock=5)

    assert result["name"] == "Imported Thing"


def test_import_from_api_no_search_term():
    result = cli.import_from_api()
    assert result is None


def test_search_external_found():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"product_name": "Found It"}

    with patch("cli.requests.get", return_value=fake_response):
        result = cli.search_external(name="something")

    assert result["product_name"] == "Found It"


def test_search_external_no_term():
    result = cli.search_external()
    assert result is None