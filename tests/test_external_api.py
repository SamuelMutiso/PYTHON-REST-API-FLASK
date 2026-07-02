from unittest.mock import patch, Mock
import requests as real_requests
import external_api


def test_fetch_by_barcode_success():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "code": "123456",
        "product": {"product_name": "Mock Milk", "brands": "MockBrand"}
    }

    with patch("external_api.requests.get", return_value=fake_response) as mock_get:
        result = external_api.fetch_product_by_barcode("123456")

    mock_get.assert_called_once()
    assert result["product_name"] == "Mock Milk"
    assert result["code"] == "123456"


def test_fetch_by_barcode_not_in_database():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"code": "000000", "product": {}}

    with patch("external_api.requests.get", return_value=fake_response):
        result = external_api.fetch_product_by_barcode("000000")

    assert result is None


def test_fetch_by_barcode_bad_status_code():
    fake_response = Mock()
    fake_response.status_code = 500

    with patch("external_api.requests.get", return_value=fake_response):
        result = external_api.fetch_product_by_barcode("123456")

    assert result is None


def test_fetch_by_barcode_connection_error():
    with patch("external_api.requests.get", side_effect=real_requests.exceptions.ConnectionError):
        result = external_api.fetch_product_by_barcode("123456")

    assert result is None


def test_fetch_by_name_success():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "products": [{"product_name": "Mock Cereal", "brands": "MockCo"}]
    }

    with patch("external_api.requests.get", return_value=fake_response):
        result = external_api.fetch_product_by_name("cereal")

    assert result["product_name"] == "Mock Cereal"


def test_fetch_by_name_no_results():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"products": []}

    with patch("external_api.requests.get", return_value=fake_response):
        result = external_api.fetch_product_by_name("madeupfoodthatdoesntexist")

    assert result is None


def test_fetch_by_name_timeout():
    with patch("external_api.requests.get", side_effect=real_requests.exceptions.Timeout):
        result = external_api.fetch_product_by_name("cereal")

    assert result is None