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
import re

from django.conf import settings

from . import mongo_client

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:  # optional dependency
    OpenAI = None

# ---------------------------------------------------------------------------
# OpenAI client (lazy singleton)
# ---------------------------------------------------------------------------
_openai_client = None


def _get_openai():
    if OpenAI is None:
        raise RuntimeError(
            "OpenAI SDK is not installed. Run: pip install -r mainProject/requirements.txt"
        )
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

_DISH_LIBRARY = {
    "sev tameta": [
        {"name": "Tomato", "quantity": "500", "unit": "g", "category": "Vegetables"},
        {"name": "Sev", "quantity": "200", "unit": "g", "category": "Pantry"},
        {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
        {"name": "Ginger", "quantity": "20", "unit": "g", "category": "Vegetables"},
        {"name": "Green Chili", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
        {"name": "Coriander", "quantity": "30", "unit": "g", "category": "Vegetables"},
        {"name": "Oil", "quantity": "2", "unit": "tbsp", "category": "Oil"},
        {"name": "Salt", "quantity": "1", "unit": "tsp", "category": "Spices"},
        {"name": "Turmeric", "quantity": "0.5", "unit": "tsp", "category": "Spices"},
        {"name": "Red Chili Powder", "quantity": "1", "unit": "tsp", "category": "Spices"},
    ],
    "paneer butter masala": [
        {"name": "Paneer", "quantity": "400", "unit": "g", "category": "Dairy"},
        {"name": "Tomato", "quantity": "400", "unit": "g", "category": "Vegetables"},
        {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
        {"name": "Butter", "quantity": "3", "unit": "tbsp", "category": "Dairy"},
        {"name": "Cream", "quantity": "120", "unit": "ml", "category": "Dairy"},
        {"name": "Salt", "quantity": "1", "unit": "tsp", "category": "Spices"},
        {"name": "Red Chili Powder", "quantity": "1", "unit": "tsp", "category": "Spices"},
        {"name": "Garam Masala", "quantity": "1", "unit": "tsp", "category": "Spices"},
        {"name": "Oil", "quantity": "1", "unit": "tbsp", "category": "Oil"},
    ],
    "chole bhature": [
        {"name": "Kabuli Chana", "quantity": "400", "unit": "g", "category": "Pulses"},
        {"name": "Maida", "quantity": "500", "unit": "g", "category": "Flour"},
        {"name": "Curd", "quantity": "150", "unit": "ml", "category": "Dairy"},
        {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
        {"name": "Tomato", "quantity": "3", "unit": "pcs", "category": "Vegetables"},
        {"name": "Oil", "quantity": "500", "unit": "ml", "category": "Oil"},
        {"name": "Salt", "quantity": "1.5", "unit": "tsp", "category": "Spices"},
    ],
}


def _extract_servings(user_input: str) -> int:
    m = re.search(r"\bfor\s+(\d{1,2})\b", user_input.lower())
    if m:
        return max(1, int(m.group(1)))
    digits = re.findall(r"\b(\d{1,2})\b", user_input)
    if digits:
        return max(1, int(digits[-1]))
    return 2


def _normalize_dish_name(user_input: str) -> str:
    text = user_input.lower().strip()
    text = re.sub(r"\bfor\s+\d{1,2}\b", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    aliases = {
        "sev tmeta": "sev tameta",
        "sev tameta nu shaak": "sev tameta",
        "pbm": "paneer butter masala",
    }
    return aliases.get(text, text)


def _scale_ingredients(items: list[dict], servings: int) -> list[dict]:
    # Base recipes in library assume 4 servings.
    factor = max(servings, 1) / 4.0
    scaled = []
    for item in items:
        q = item.get("quantity", "1")
        try:
            val = float(q)
            out = str(round(val * factor, 2)).rstrip("0").rstrip(".")
        except Exception:  # noqa: BLE001
            out = q
        scaled.append({**item, "quantity": out})
    return scaled


def _fallback_parse(user_input: str) -> dict:
    servings = _extract_servings(user_input)
    dish = _normalize_dish_name(user_input)
    if dish in _DISH_LIBRARY:
        ingredients = _scale_ingredients(_DISH_LIBRARY[dish], servings)
        return {"dish": dish.title(), "servings": servings, "ingredients": ingredients}
    # Generic minimal pantry fallback for unknown dishes
    ingredients = _scale_ingredients(
        [
            {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
            {"name": "Tomato", "quantity": "3", "unit": "pcs", "category": "Vegetables"},
            {"name": "Oil", "quantity": "2", "unit": "tbsp", "category": "Oil"},
            {"name": "Salt", "quantity": "1", "unit": "tsp", "category": "Spices"},
            {"name": "Green Chili", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
        ],
        servings,
    )
    return {"dish": dish.title() or "Custom Dish", "servings": servings, "ingredients": ingredients}


def parse_dish_request(user_input: str) -> dict:
    """Send the user's natural-language request to OpenAI and return parsed JSON."""
    try:
        client = _get_openai()
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
        logger.warning("OpenAI unavailable, using fallback parser: %s", e)
        return _fallback_parse(user_input)


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
