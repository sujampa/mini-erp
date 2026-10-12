import requests

from app.services.inventory_tools import (
    get_low_stock_products,
    get_inventory_summary,
    get_low_cost_products,
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"


def ask_ai(question: str) -> str:
    """Answer supported ERP questions using database-backed tools."""

    question = question.strip()
    question_lower = question.lower()

    if not question:
        return "Please enter a question."

    # TOOL 1: Low-cost products
    low_cost_keywords = [
        "low cost",
        "low-cost",
        "cheapest",
        "lowest price",
        "least expensive",
        "inexpensive",
        "cheap product",
        "cheap products",
        "products under",
        "cost less than",
        "price below",
    ]

    if any(keyword in question_lower for keyword in low_cost_keywords):
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

    # TOOL 2: Low-stock products
    low_stock_keywords = [
        "low stock",
        "low-stock",
        "low inventory",
        "below threshold",
        "stock shortage",
        "products running low",
        "running low",
    ]

    if any(keyword in question_lower for keyword in low_stock_keywords):
        products = get_low_stock_products()

        if not products:
            return (
                "There are no active products with stock at or "
                "below the threshold of 5 units."
            )

        lines = [
            f"- {product['name']}: {product['quantity']} units"
            for product in products
        ]

        return "Active products with low stock:\n" + "\n".join(lines)

    # TOOL 3: Inventory summary and stock questions
    stock_keywords = [
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
    ]

    if any(keyword in question_lower for keyword in stock_keywords):
        summary = get_inventory_summary()

        # Inventory valuation
        if any(
            word in question_lower
            for word in ["value", "worth", "valuation"]
        ):
            return (
                "The total value of active inventory is "
                f"{summary['total_inventory_value']:,.2f}."
            )

        # Active product count
        if any(
            phrase in question_lower
            for phrase in [
                "how many products",
                "how many items",
                "product count",
                "active products",
                "number of products",
            ]
        ):
            return (
                f"There are {summary['total_active_products']} "
                "active products."
            )

        # Total stock quantity
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
            ]
        ):
            return (
                f"There are {summary['total_stock_units']} units "
                "in active inventory."
            )

        # General inventory summary
        return (
            "Inventory Summary\n"
            f"- Active products: {summary['total_active_products']}\n"
            f"- Total stock units: {summary['total_stock_units']}\n"
            f"- Inventory value: "
            f"{summary['total_inventory_value']:,.2f}"
        )

    # GENERAL QUESTIONS: Use Ollama.
    # Current ERP facts are not answered from the LLM's memory.
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful Mini ERP assistant. "
                    "Answer general questions clearly. "
                    "Do not invent current ERP inventory, product, "
                    "sales, or financial information. "
                    "If asked for current ERP data that has not "
                    "been retrieved, say so."
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