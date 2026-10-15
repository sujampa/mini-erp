from unittest.mock import patch

from app.services.ai_assistant import ask_ai


@patch("app.services.ai_assistant.get_low_stock_products")
def test_reorder_question_uses_low_stock_tool(mock_low_stock):
    mock_low_stock.return_value = []

    answer = ask_ai("Do we need to reorder any products?")

    mock_low_stock.assert_called_once()
    assert "no active products" in answer.lower()
    assert "reordering" in answer.lower()


@patch("app.services.ai_assistant.get_low_stock_products")
def test_almost_out_of_stock_uses_low_stock_tool(mock_low_stock):
    mock_low_stock.return_value = [
        {"name": "Keyboard", "quantity": 3}
    ]

    answer = ask_ai("Which items are almost out of stock?")

    mock_low_stock.assert_called_once()
    assert "Keyboard" in answer
    assert "3 units" in answer


@patch("app.services.ai_assistant.get_low_cost_products")
def test_cheapest_product_question_uses_low_cost_tool(mock_low_cost):
    mock_low_cost.return_value = [
        {
            "name": "Mouse",
            "price": 500.0,
            "quantity": 10,
        }
    ]

    answer = ask_ai("Give me the cheapest item we sell.")

    mock_low_cost.assert_called_once()
    assert "Mouse" in answer
    assert "500.00" in answer


@patch("app.services.ai_assistant.get_inventory_summary")
def test_total_stock_question_uses_inventory_tool(mock_summary):
    mock_summary.return_value = {
        "total_active_products": 2,
        "total_stock_units": 31,
        "total_inventory_value": 775000.0,
    }

    answer = ask_ai("Tell me how much stock we have altogether.")

    mock_summary.assert_called_once()
    assert "31 units" in answer


@patch("app.services.ai_assistant.get_inventory_summary")
def test_inventory_value_question_uses_inventory_tool(mock_summary):
    mock_summary.return_value = {
        "total_active_products": 2,
        "total_stock_units": 31,
        "total_inventory_value": 775000.0,
    }

    answer = ask_ai("What is my total inventory value?")

    mock_summary.assert_called_once()
    assert "775,000.00" in answer


@patch("app.services.ai_assistant.requests.post")
def test_general_question_uses_ollama(mock_post):
    mock_post.return_value.json.return_value = {
        "message": {
            "content": "An ERP system integrates business operations."
        }
    }
    mock_post.return_value.raise_for_status.return_value = None

    answer = ask_ai("What is an ERP system?")

    mock_post.assert_called_once()
    assert "integrates business operations" in answer


def test_empty_question_does_not_call_tools():
    answer = ask_ai("   ")

    assert answer == "Please enter a question."