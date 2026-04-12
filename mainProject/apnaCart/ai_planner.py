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

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)
_mongo_lookup_available = True

# ---------------------------------------------------------------------------
# OpenAI client (lazy singleton)
# ---------------------------------------------------------------------------
_openai_client = None

_FALLBACK_RECIPES = {
    "daal pakwaan": {
        "description": "A traditional Sindhi breakfast of crispy fried flatbreads served with spiced chana dal.",
        "prep_time": "20 mins",
        "cook_time": "45 mins",
        "ingredients": [
            {"name": "Chana Dal", "quantity": "500", "unit": "g", "category": "Pulses"},
            {"name": "Maida", "quantity": "400", "unit": "g", "category": "Flour"},
            {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
            {"name": "Tomato", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
            {"name": "Green Chilli", "quantity": "4", "unit": "pcs", "category": "Vegetables"},
            {"name": "Coriander", "quantity": "1", "unit": "bunch", "category": "Vegetables"},
            {"name": "Cumin", "quantity": "2", "unit": "tsp", "category": "Spices"},
            {"name": "Turmeric", "quantity": "1", "unit": "tsp", "category": "Spices"},
            {"name": "Salt", "quantity": "2", "unit": "tsp", "category": "Pantry"},
            {"name": "Oil", "quantity": "500", "unit": "ml", "category": "Oil"},
        ],
        "recipe_steps": [
            "Soak chana dal for 4 hours, then pressure cook until soft with turmeric and salt.",
            "Knead maida with salt, oil, and water into a smooth dough. Rest for 30 minutes.",
            "Heat oil in a kadai. Temper with cumin seeds, hing, and curry leaves.",
            "Add chopped onions and green chillies, sauté until golden.",
            "Add tomatoes, turmeric, and red chilli powder. Cook until soft.",
            "Add boiled dal and mash lightly. Simmer for 10 minutes.",
            "Roll dough into thin circles and deep fry until golden and crispy.",
            "Garnish dal with fresh coriander and serve hot with crispy pakwaan.",
        ],
    },
    "paneer butter masala": {
        "description": "Rich and creamy North Indian curry made with soft paneer cubes in a buttery tomato-based gravy.",
        "prep_time": "15 mins",
        "cook_time": "30 mins",
        "ingredients": [
            {"name": "Paneer", "quantity": "500", "unit": "g", "category": "Dairy"},
            {"name": "Tomato", "quantity": "5", "unit": "pcs", "category": "Vegetables"},
            {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
            {"name": "Butter", "quantity": "100", "unit": "g", "category": "Dairy"},
            {"name": "Fresh Cream", "quantity": "200", "unit": "ml", "category": "Dairy"},
            {"name": "Ginger Garlic Paste", "quantity": "2", "unit": "tbsp", "category": "Pantry"},
            {"name": "Red Chilli Powder", "quantity": "1", "unit": "tsp", "category": "Spices"},
            {"name": "Garam Masala", "quantity": "1", "unit": "tsp", "category": "Spices"},
            {"name": "Salt", "quantity": "2", "unit": "tsp", "category": "Pantry"},
            {"name": "Oil", "quantity": "3", "unit": "tbsp", "category": "Oil"},
        ],
        "recipe_steps": [
            "Blanch tomatoes and blend into a smooth puree.",
            "Heat butter in a pan, add ginger garlic paste and sauté for 1 minute.",
            "Add sliced onions and cook until translucent.",
            "Pour in tomato puree, add red chilli powder, turmeric. Cook for 10 mins.",
            "Strain the gravy through a sieve for a smooth texture.",
            "Return gravy to pan, add sugar, salt, and garam masala.",
            "Add paneer cubes and simmer for 5 minutes on low heat.",
            "Finish with fresh cream and butter. Garnish with coriander.",
        ],
    },
    "chole bhature": {
        "description": "Iconic Punjabi street food of spiced chickpea curry served with puffy deep-fried bread.",
        "prep_time": "30 mins (+ overnight soaking)",
        "cook_time": "50 mins",
        "ingredients": [
            {"name": "Kabuli Chana", "quantity": "500", "unit": "g", "category": "Pulses"},
            {"name": "Maida", "quantity": "500", "unit": "g", "category": "Flour"},
            {"name": "Curd", "quantity": "200", "unit": "g", "category": "Dairy"},
            {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
            {"name": "Tomato", "quantity": "3", "unit": "pcs", "category": "Vegetables"},
            {"name": "Ginger Garlic Paste", "quantity": "2", "unit": "tbsp", "category": "Pantry"},
            {"name": "Chole Masala", "quantity": "2", "unit": "tbsp", "category": "Spices"},
            {"name": "Salt", "quantity": "2", "unit": "tsp", "category": "Pantry"},
            {"name": "Oil", "quantity": "750", "unit": "ml", "category": "Oil"},
        ],
        "recipe_steps": [
            "Soak kabuli chana overnight. Pressure cook with salt and tea bag for colour.",
            "For bhature: Mix maida, curd, salt, sugar, baking powder and knead into soft dough. Rest 2 hours.",
            "Heat oil in a pan. Add cumin seeds, bay leaf, and chopped onions.",
            "Add ginger garlic paste and cook until raw smell disappears.",
            "Add tomato puree, chole masala, red chilli powder. Cook for 5 mins.",
            "Add boiled chana with some cooking water. Simmer for 15 minutes.",
            "Roll bhature dough into oval shapes and deep fry until puffed and golden.",
            "Serve hot chole with bhature, sliced onion and green chutney.",
        ],
    },
    "pasta aglio e olio": {
        "description": "A classic Italian pasta dish with garlic, olive oil, and chilli flakes — simple and elegant.",
        "prep_time": "5 mins",
        "cook_time": "15 mins",
        "ingredients": [
            {"name": "Pasta", "quantity": "400", "unit": "g", "category": "Pantry"},
            {"name": "Garlic", "quantity": "10", "unit": "cloves", "category": "Vegetables"},
            {"name": "Olive Oil", "quantity": "80", "unit": "ml", "category": "Oil"},
            {"name": "Chilli Flakes", "quantity": "2", "unit": "tsp", "category": "Spices"},
            {"name": "Parsley", "quantity": "1", "unit": "bunch", "category": "Vegetables"},
            {"name": "Salt", "quantity": "2", "unit": "tsp", "category": "Pantry"},
        ],
        "recipe_steps": [
            "Boil pasta in salted water until al dente. Reserve 1 cup pasta water.",
            "Thinly slice garlic cloves. Heat olive oil in a wide pan on low heat.",
            "Add sliced garlic and chilli flakes. Toast until garlic is light golden (not brown).",
            "Add drained pasta to the pan along with 2-3 tbsp pasta water.",
            "Toss everything together, adding more pasta water if needed for silkiness.",
            "Finish with chopped parsley and a drizzle of olive oil. Serve immediately.",
        ],
    },
}


def _get_openai():
    global _openai_client
    if OpenAI is None or not settings.OPENAI_API_KEY:
        return None
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


_GENERIC_COOKING_STAPLES = [
    {"name": "Onion", "quantity": "2", "unit": "pcs", "category": "Vegetables"},
    {"name": "Tomato", "quantity": "3", "unit": "pcs", "category": "Vegetables"},
    {"name": "Ginger", "quantity": "1", "unit": "piece", "category": "Vegetables"},
    {"name": "Garlic", "quantity": "5", "unit": "cloves", "category": "Vegetables"},
    {"name": "Green Chilli", "quantity": "3", "unit": "pcs", "category": "Vegetables"},
    {"name": "Cumin", "quantity": "1", "unit": "tsp", "category": "Spices"},
    {"name": "Turmeric", "quantity": "1", "unit": "tsp", "category": "Spices"},
    {"name": "Red Chilli Powder", "quantity": "1", "unit": "tsp", "category": "Spices"},
    {"name": "Garam Masala", "quantity": "1", "unit": "tsp", "category": "Spices"},
    {"name": "Coriander", "quantity": "1", "unit": "bunch", "category": "Vegetables"},
    {"name": "Salt", "quantity": "2", "unit": "tsp", "category": "Pantry"},
    {"name": "Oil", "quantity": "3", "unit": "tbsp", "category": "Oil"},
]


def _fallback_parse_dish_request(user_input: str) -> dict:
    query = user_input.strip()
    lowered = query.lower()

    servings = 2
    servings_match = re.search(r"\bfor\s+(\d+)\b", lowered)
    if servings_match:
        servings = int(servings_match.group(1))

    dish = re.split(r"\bfor\s+\d+\b", query, maxsplit=1, flags=re.IGNORECASE)[0].strip(" ,.-")
    if not dish:
        dish = query

    # Try known recipes first
    recipe = _FALLBACK_RECIPES.get(dish.lower())
    if recipe is not None:
        return {
            "dish": dish.title(),
            "servings": servings,
            "description": recipe.get("description", ""),
            "prep_time": recipe.get("prep_time", ""),
            "cook_time": recipe.get("cook_time", ""),
            "ingredients": recipe["ingredients"],
            "recipe_steps": recipe.get("recipe_steps", []),
        }

    # For unknown dishes, return generic cooking staples
    logger.info("No built-in recipe for '%s', using generic staples", dish)
    return {
        "dish": dish.title(),
        "servings": servings,
        "description": f"A custom meal plan for {dish.title()}. Generic cooking staples provided.",
        "prep_time": "15 mins",
        "cook_time": "30 mins",
        "ingredients": list(_GENERIC_COOKING_STAPLES),
        "recipe_steps": [
            "Prepare all vegetables — wash, peel and chop onions, tomatoes, and other veggies.",
            "Heat oil in a pan. Add cumin seeds and let them splutter.",
            "Add chopped onions and sauté until golden brown.",
            "Add ginger-garlic paste and green chillies. Cook for 1 minute.",
            "Add tomatoes, turmeric, red chilli powder and salt. Cook until soft.",
            "Add your main ingredient and mix well. Cook on medium heat.",
            "Add garam masala and adjust salt to taste. Simmer for 5 minutes.",
            "Garnish with fresh coriander and serve hot with rice or roti.",
        ],
    }


# ---------------------------------------------------------------------------
# Step 1: Parse natural-language query → structured JSON via GPT
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a professional Indian chef and grocery expert.
The user will tell you what dish they want to make and for how many people.

Your job:
1. Identify the dish.
2. List EVERY ingredient required (even small items like salt, oil, spices).
3. Calculate the quantity needed for the given number of servings.
4. Provide step-by-step cooking instructions (concise, numbered steps).

Reply ONLY with valid JSON — no markdown, no explanation.

Schema:
{
  "dish": "<dish name>",
  "servings": <number>,
  "description": "<one-line description of the dish>",
  "prep_time": "<e.g. 15 mins>",
  "cook_time": "<e.g. 30 mins>",
  "ingredients": [
    {
      "name": "<ingredient name, e.g. Chana Dal>",
      "quantity": "<amount, e.g. 250>",
      "unit": "<g / kg / ml / L / pcs / tbsp / tsp / pack>",
      "category": "<Pulses / Spices / Dairy / Flour / Oil / Vegetables / Fruits / Pantry / Other>"
    }
  ],
  "recipe_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ]
}

Rules:
- Use commonly available Indian grocery product names.
- Always include oil, salt, and water if genuinely needed.
- Quantities must be realistic for home cooking.
- Keep ingredient names short and generic (not brand names).
- Recipe steps should be clear, concise and numbered.
"""


def parse_dish_request(user_input: str) -> dict:
    """Send the user's natural-language request to OpenAI and return parsed JSON."""
    client = _get_openai()
    if client is None:
        return _fallback_parse_dish_request(user_input)

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
        return _fallback_parse_dish_request(user_input)
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        return _fallback_parse_dish_request(user_input)


# ---------------------------------------------------------------------------
# Step 2: Match each ingredient to real products in MongoDB
# ---------------------------------------------------------------------------


def match_ingredients_to_products(ingredients: list) -> list:
    """
    For each ingredient from the AI, search MongoDB for the best matching
    product and return enriched items with product info + price.
    """
    matched_items = []
    global _mongo_lookup_available

    for ing in ingredients:
        name = ing.get("name", "")
        quantity = ing.get("quantity", "")
        unit = ing.get("unit", "")
        category = ing.get("category", "Other")

        # Search for this ingredient in the products DB
        product = None
        if _mongo_lookup_available:
            try:
                product = mongo_client.search_product_by_name(name)
            except Exception as exc:
                _mongo_lookup_available = False
                logger.warning("Mongo lookup disabled for this run: %s", exc)

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
    recipe_steps = parsed.get("recipe_steps", [])
    description = parsed.get("description", "")
    prep_time = parsed.get("prep_time", "")
    cook_time = parsed.get("cook_time", "")

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
        "description": description,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "recipe_steps": recipe_steps,
        "items": matched_items,
        "total_price": round(total_price, 2),
        "matched_count": matched_count,
        "total_count": total_count,
    }
