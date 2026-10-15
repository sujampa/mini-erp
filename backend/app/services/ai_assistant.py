import re

import requests

from app.services.inventory_tools import (
    get_low_stock_products,
    get_inventory_summary,
    get_low_cost_products,
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

# Requests that must never execute through the AI assistant.
DESTRUCTIVE_KEYWORDS = [
    "delete",
    "remove",
    "erase",
    "clear",
    "wipe",
    "truncate",
    "drop table",
    "drop database",
    "destroy",
    "empty inventory",
    "empty the inventory",
    "clear inventory",
    "clear the inventory",
    "remove inventory",
    "remove all inventory",
    "delete all products",
    "remove all products",
    "delete all items",
    "remove all items",
    "reset inventory",
    "reset the inventory",
    "remove all stock",
    "delete all stock",
]

LOW_COST_KEYWORDS = [
    "low cost",
    "low-cost",
    "cheapest",
    "lowest price",
    "least expensive",
    "inexpensive",
    "cheap product",
    "cheap products",
    "cheapest item",
    "cheapest product",
    "lowest cost",
    "products under",
    "cost less than",
    "price below",
]

LOW_STOCK_KEYWORDS = [
    "low stock",
    "low-stock",
    "low inventory",
    "below threshold",
    "stock shortage",
    "products running low",
    "product running low",
    "running low",
    "almost out of stock",
    "almost out of",
    "nearly out of stock",
    "reorder",
    "re-order",
    "restock",
    "restocking",
    "need to order",
    "need to buy",
    "need more stock",
    "shortage",
    "out of stock",
]

INVENTORY_KEYWORDS = [
    "stock",
    "inventory",
    "units",
    "quantity",
    "quantities",
    "how many",
    "in stock",
    "available products",
    "available items",
    "product count",
    "products",
    "items",
]


def _is_destructive_request(question: str) -> bool:
    """Identify requests to delete, clear, or destroy ERP data."""

    normalized = re.sub(r"\s+", " ", question.lower()).strip()

    return any(
        keyword in normalized
        for keyword in DESTRUCTIVE_KEYWORDS
    )


def ask_ai(question: str) -> str:
    """Answer ERP questions using read-only tools or Ollama."""

    question = question.strip()

    if not question:
        return "Please enter a question."

    question_lower = question.lower()

    # GUARDRAIL: Check destructive requests before tool routing.
    if _is_destructive_request(question):
        return (
            "I cannot execute destructive database or inventory "
            "operations. No deletion or inventory-clearing action "
            "was performed by the AI Assistant. Please use the "
            "authorized ERP interface and follow your organization's "
            "approval process for such changes."
        )

    # TOOL 1: Cheapest products.
    if any(
        keyword in question_lower
        for keyword in LOW_COST_KEYWORDS
    ):
        products = get_low_cost_products()

        if not products:
            return "There are no active products in the inventory."

        lines = [
            f"- {product['name']}: {product['price']:,.2f}"
            f" | Stock: {product['quantity']} units"
            for product in products
        ]

        return (
            "Active products sorted from lowest to highest price:\n"
            + "\n".join(lines)
        )

    # TOOL 2: Low-stock and reorder questions.
    if any(
        keyword in question_lower
        for keyword in LOW_STOCK_KEYWORDS
    ):
        products = get_low_stock_products()

        if not products:
            return (
                "No active products currently meet the low-stock "
                "threshold of 5 units or less. Based on this threshold, "
                "no active products are flagged for reordering."
            )

        lines = [
            f"- {product['name']}: {product['quantity']} units"
            for product in products
        ]

        return (
            "Active products requiring a low-stock review:\n"
            + "\n".join(lines)
            + "\nReview these items before placing a purchase order."
        )

    # TOOL 3: Inventory summary and stock questions.
    if any(
        keyword in question_lower
        for keyword in INVENTORY_KEYWORDS
    ):
        summary = get_inventory_summary()

        # Inventory valuation.
        if any(
            word in question_lower
            for word in [
                "value",
                "worth",
                "valuation",
                "total cost",
            ]
        ):
            return (
                "The total value of active inventory is "
                f"{summary['total_inventory_value']:,.2f}."
            )

        # Active product count.
        if any(
            phrase in question_lower
            for phrase in [
                "how many products",
                "how many items",
                "product count",
                "active products",
                "number of products",
                "how many different",
            ]
        ):
            return (
                f"There are {summary['total_active_products']} "
                "active products."
            )

        # Total stock quantity.
        if any(
            phrase in question_lower
            for phrase in [
                "how many units",
                "many units",
                "units are",
                "stock quantity",
                "total quantity",
                "quantity in stock",
                "in stock",
                "stock levels",
                "available items",
                "altogether",
                "total stock",
            ]
        ):
            return (
                f"There are {summary['total_stock_units']} units "
                "in active inventory."
            )

        return (
            "Inventory Summary\n"
            f"- Active products: {summary['total_active_products']}\n"
            f"- Total stock units: {summary['total_stock_units']}\n"
            f"- Inventory value: "
            f"{summary['total_inventory_value']:,.2f}"
        )

    # GENERAL QUESTIONS: Use Ollama.
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful Mini ERP assistant. "
                    "Answer general questions clearly. "
                    "You are read-only and must never claim to have "
                    "modified or deleted ERP records. "
                    "Do not invent current ERP inventory, product, "
                    "sales, or financial information. "
                    "If asked for current ERP data that has not "
                    "been retrieved, say so. "
                    "You do not have access to live weather or other "
                    "real-time external information unless a tool "
                    "explicitly provides it."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        return result["message"]["content"]

    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Check that Ollama is running."
        ) from exc


if __name__ == "__main__":
    print("Mini ERP AI Business Assistant")
    print("Type 'exit' to stop.")

    while True:
        try:
            question = input("\nYou: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            if not question:
                continue

            print("\nAI Assistant:")
            print(ask_ai(question))

        except (RuntimeError, ValueError, KeyError) as exc:
            print(f"\nError: {exc}")

        except Exception as exc:
            print(
                "\nUnexpected error while processing the question: "
                f"{type(exc).__name__}: {exc}"
            )