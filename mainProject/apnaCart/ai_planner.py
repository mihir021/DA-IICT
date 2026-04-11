"""
ai_planner.py — AI-powered grocery planning using OpenAI + MongoDB product search.

Flow:
1. User says "Daal Pakwaan for 4 guests"
2. OpenAI parses → dish name, servings, ingredient list with quantities
3. Each ingredient is matched against MongoDB products collection
4. Result is returned to the frontend for user approval
"""

import json
import logging

from openai import OpenAI
from django.conf import settings

from . import mongo_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OpenAI client (lazy singleton)
# ---------------------------------------------------------------------------
_openai_client = None


def _get_openai():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


# ---------------------------------------------------------------------------
# Step 1: Parse natural-language query → structured JSON via GPT
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a professional Indian chef and grocery expert.
The user will tell you what dish they want to make and for how many people.

Your job:
1. Identify the dish.
2. List EVERY ingredient required (even small items like salt, oil, spices).
3. Calculate the quantity needed for the given number of servings.

Reply ONLY with valid JSON — no markdown, no explanation.

Schema:
{
  "dish": "<dish name>",
  "servings": <number>,
  "ingredients": [
    {
      "name": "<ingredient name, e.g. Chana Dal>",
      "quantity": "<amount, e.g. 250>",
      "unit": "<g / kg / ml / L / pcs / tbsp / tsp / pack>",
      "category": "<Pulses / Spices / Dairy / Flour / Oil / Vegetables / Fruits / Pantry / Other>"
    }
  ]
}

Rules:
- Use commonly available Indian grocery product names.
- Always include oil, salt, and water if genuinely needed.
- Quantities must be realistic for home cooking.
- Keep ingredient names short and generic (not brand names).
"""


def parse_dish_request(user_input: str) -> dict:
    """Send the user's natural-language request to OpenAI and return parsed JSON."""
    client = _get_openai()

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]  # remove first line
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        data = json.loads(raw)
        return data

    except json.JSONDecodeError as e:
        logger.error("OpenAI returned invalid JSON: %s", e)
        return {"error": "AI returned an invalid response. Please try again."}
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        return {"error": f"AI service error: {str(e)}"}


# ---------------------------------------------------------------------------
# Step 2: Match each ingredient to real products in MongoDB
# ---------------------------------------------------------------------------


def match_ingredients_to_products(ingredients: list) -> list:
    """
    For each ingredient from the AI, search MongoDB for the best matching
    product and return enriched items with product info + price.
    """
    matched_items = []

    for ing in ingredients:
        name = ing.get("name", "")
        quantity = ing.get("quantity", "")
        unit = ing.get("unit", "")
        category = ing.get("category", "Other")

        # Search for this ingredient in the products DB
        product = mongo_client.search_product_by_name(name)

        if product:
            item = {
                "ingredient_name": name,
                "needed_quantity": f"{quantity}{unit}",
                "product_id": str(product["_id"]),
                "product_name": product.get("name", name),
                "product_price": product.get("price", 0),
                "product_unit": product.get("unit", unit),
                "product_weight": product.get("weight", ""),
                "product_image": product.get("image_url", ""),
                "product_category": product.get("category", category),
                "discount": product.get("discount", 0),
                "matched": True,
            }
        else:
            # No match found – return the ingredient info so the user sees it
            item = {
                "ingredient_name": name,
                "needed_quantity": f"{quantity}{unit}",
                "product_id": None,
                "product_name": name,
                "product_price": 0,
                "product_unit": unit,
                "product_weight": "",
                "product_image": "",
                "product_category": category,
                "discount": 0,
                "matched": False,
            }

        matched_items.append(item)

    return matched_items


# ---------------------------------------------------------------------------
# Step 3: Build the complete plan response
# ---------------------------------------------------------------------------


def generate_plan(user_query: str) -> dict:
    """
    End-to-end: parse the user query, match to products, return full plan.
    This is the single function that the view calls.
    """
    # 1. Parse with AI
    parsed = parse_dish_request(user_query)
    if "error" in parsed:
        return parsed

    dish = parsed.get("dish", "Unknown Dish")
    servings = parsed.get("servings", 1)
    ingredients = parsed.get("ingredients", [])

    if not ingredients:
        return {"error": "Could not identify ingredients for this dish."}

    # 2. Match to products
    matched_items = match_ingredients_to_products(ingredients)

    # 3. Calculate totals
    total_price = sum(
        item["product_price"] * (1 - item["discount"] / 100)
        for item in matched_items
        if item["matched"]
    )

    matched_count = sum(1 for item in matched_items if item["matched"])
    total_count = len(matched_items)

    return {
        "dish": dish,
        "servings": servings,
        "items": matched_items,
        "total_price": round(total_price, 2),
        "matched_count": matched_count,
        "total_count": total_count,
    }
