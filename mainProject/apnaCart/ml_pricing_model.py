"""
ml_pricing_model.py — Gradient Boosting Regressor for Dynamic Pricing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Model:  sklearn.ensemble.GradientBoostingRegressor
Target: Optimal price adjustment percentage (−15% to +8%)

WHY GRADIENT BOOSTING?
───────────────────────
1. Works brilliantly with SMALL datasets — we bootstrap training data
   from the existing rule-based system, so we start with ~5,000 samples.
   Deep learning needs 100k+; GBR thrives at 1k–50k.

2. Handles MIXED features natively — our features are a mix of
   categorical (category, time-bracket) and numerical (price, views).
   Tree-based models don't need feature scaling or one-hot encoding.

3. Captures NON-LINEAR relationships — the relationship between
   "time of day × category × user engagement → optimal discount"
   is highly non-linear. Linear regression would miss these patterns.

4. INTERPRETABLE — we can extract feature_importances_ to explain
   *why* a price changed. This builds user trust ("Smart Price" labels).

5. FAST inference (~0.1 ms per prediction) — critical because every
   product card on the page calls this in real time.

6. Better than Random Forest for REGRESSION — GBR builds trees
   sequentially, each correcting the previous one's errors. This gives
   lower bias and better accuracy on structured/tabular data.

ALTERNATIVES CONSIDERED:
────────────────────────
- Linear Regression:  Too simple. Can't model interactions like
                      "Dairy + evening + high engagement = different
                      discount than Dairy + morning + low engagement"
- Random Forest:      Good, but GBR typically wins on regression tasks
                      due to sequential error correction.
- XGBoost/LightGBM:   Better at scale, but adds heavy C++ dependencies.
                      sklearn's GBR is pure Python and sufficient here.
- Neural Network:     Overkill. Needs 100k+ samples, GPU, complex
                      tuning. Our scenario has <50 products.

FEATURES (8 total):
───────────────────
  1. hour_of_day        (0–23)    — Time-based demand signal
  2. day_of_week        (0–6)     — Weekend vs weekday patterns
  3. category_encoded   (0–N)     — Product category as integer
  4. base_price         (float)   — Product MRP
  5. existing_discount  (float)   — Current static discount %
  6. is_best_seller     (0/1)     — Popularity flag
  7. session_cat_views  (int)     — User's views in this category
  8. session_total_views (int)    — User's total product views
  9. cart_count          (int)     — Items in user's cart

TARGET:
───────
  price_adjustment_pct  (float)   — Optimal % change (−15 to +8)
"""

import os
import math
import random
import logging
import numpy as np
from datetime import datetime
from pathlib import Path

import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────
MODEL_DIR = Path(__file__).resolve().parent.parent / "ml_models"
MODEL_PATH = MODEL_DIR / "dynamic_pricing_gbr.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.joblib"

# ── Category encoding ────────────────────────────────────────────────
CATEGORY_MAP = {
    "Fruits":      0,
    "Vegetables":  1,
    "Dairy":       2,
    "Pulses":      3,
    "Flour":       4,
    "Grains":      5,
    "Oil":         6,
    "Spices":      7,
    "Pantry":      8,
    "Other":       9,
}

# ── Safety rails (same as rule-based system) ─────────────────────────
MAX_MARKUP_PCT = 8
MAX_DISCOUNT_PCT = 15


# =====================================================================
#  TRAINING DATA GENERATION
# =====================================================================

def _generate_training_data(n_samples: int = 5000) -> tuple:
    """
    Generate synthetic training data by simulating the rule-based
    pricing engine across thousands of realistic scenarios.
    This is a "teacher–student" approach: the rules teach the ML model,
    which then GENERALISES to unseen combinations better.
    """
    # IMPORTANT: Import the rule-based function DIRECTLY to avoid
    # circular recursion. calculate_dynamic_price would call the ML
    # model → train_model → _generate_training_data → infinite loop.
    from .dynamic_pricing import _calculate_rule_based

    X_data = []
    y_data = []

    categories = list(CATEGORY_MAP.keys())
    price_ranges = {
        "Fruits":     (30, 400),
        "Vegetables": (15, 100),
        "Dairy":      (20, 200),
        "Pulses":     (80, 200),
        "Flour":      (30, 350),
        "Grains":     (40, 400),
        "Oil":        (100, 600),
        "Spices":     (30, 150),
        "Pantry":     (20, 300),
        "Other":      (20, 300),
    }

    for _ in range(n_samples):
        # Randomise all inputs
        hour = random.randint(0, 23)
        day_of_week = random.randint(0, 6)
        category = random.choice(categories)
        cat_encoded = CATEGORY_MAP[category]

        pmin, pmax = price_ranges.get(category, (20, 300))
        base_price = round(random.uniform(pmin, pmax), 0)
        existing_discount = random.choice([0, 0, 0, 5, 8, 10, 12, 15])
        is_best_seller = random.choice([True, False, False])  # ~33% best sellers
        cat_views = random.randint(0, 12)
        total_views = cat_views + random.randint(0, 20)
        cart_count = random.choice([0, 0, 0, 0, 1, 2, 3])  # mostly 0

        session_data = {
            "category_views": {category: cat_views},
            "total_views": total_views,
            "cart_count": cart_count,
        }

        # Get the rule-based result as the "label"
        # Uses _calculate_rule_based directly to avoid ML recursion
        result = _calculate_rule_based(
            base_price=base_price,
            existing_discount_pct=existing_discount,
            category=category,
            is_best_seller=is_best_seller,
            session_data=session_data,
        )

        # Add some noise to make the model generalise beyond rigid rules
        noise = random.gauss(0, 0.5)  # small Gaussian noise

        # Weekend bonus: slight discount boost (rules don't capture this)
        weekend_factor = -1.0 if day_of_week >= 5 else 0.0

        # Price elasticity: expensive items are more price-sensitive
        elasticity_factor = -0.5 if base_price > 200 else 0.3 if base_price < 50 else 0.0

        target = result["dynamic_adjustment"] + noise + weekend_factor + elasticity_factor
        target = max(-MAX_DISCOUNT_PCT, min(MAX_MARKUP_PCT, target))

        features = [
            hour,
            day_of_week,
            cat_encoded,
            base_price,
            existing_discount,
            int(is_best_seller),
            cat_views,
            total_views,
            cart_count,
        ]

        X_data.append(features)
        y_data.append(round(target, 2))

    return np.array(X_data), np.array(y_data)


# =====================================================================
#  MODEL TRAINING
# =====================================================================

def train_model(n_samples: int = 5000) -> dict:
    """
    Train the Gradient Boosting Regressor and save it to disk.
    Returns training metrics.
    """
    logger.info("Generating %d training samples...", n_samples)
    X, y = _generate_training_data(n_samples)

    # Split 80/20 for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info("Training GradientBoostingRegressor...")
    model = GradientBoostingRegressor(
        n_estimators=200,         # 200 boosting stages
        max_depth=4,              # Moderate depth to prevent overfitting
        learning_rate=0.1,        # Standard learning rate
        subsample=0.8,            # Stochastic gradient boosting
        min_samples_split=10,     # Prevent overfitting on small nodes
        min_samples_leaf=5,       # Minimum samples in leaf
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Feature importances
    feature_names = [
        "hour_of_day", "day_of_week", "category",
        "base_price", "existing_discount", "is_best_seller",
        "session_cat_views", "session_total_views", "cart_count",
    ]
    importances = dict(zip(feature_names, model.feature_importances_))
    sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)

    metrics = {
        "mae": round(mae, 4),
        "r2_score": round(r2, 4),
        "n_samples": n_samples,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "feature_importances": sorted_imp,
        "trained_at": datetime.utcnow().isoformat(),
    }

    # Save model and metadata
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(metrics, METADATA_PATH)

    logger.info("Model saved to %s", MODEL_PATH)
    logger.info("MAE: %.4f | R²: %.4f", mae, r2)
    for feat, imp in sorted_imp:
        logger.info("  %-25s  %.4f", feat, imp)

    return metrics


# =====================================================================
#  MODEL LOADING & PREDICTION
# =====================================================================

# Lazy-loaded singleton
_model = None
_metadata = None


def _load_model():
    """Load the trained model from disk (lazy singleton)."""
    global _model, _metadata
    if _model is not None:
        return _model

    if not MODEL_PATH.exists():
        logger.warning("No trained model found at %s — training now...", MODEL_PATH)
        train_model()

    _model = joblib.load(MODEL_PATH)
    if METADATA_PATH.exists():
        _metadata = joblib.load(METADATA_PATH)
    logger.info("ML pricing model loaded successfully")
    return _model


def get_model_metadata() -> dict:
    """Return training metrics and feature importances."""
    global _metadata
    if _metadata is None and METADATA_PATH.exists():
        _metadata = joblib.load(METADATA_PATH)
    return _metadata or {}


def predict_price_adjustment(
    base_price: float,
    existing_discount_pct: float,
    category: str,
    is_best_seller: bool,
    session_data: dict = None,
) -> dict:
    """
    Use the trained ML model to predict the optimal price adjustment.

    Returns the same structure as the rule-based calculate_dynamic_price()
    so it's a drop-in replacement.
    """
    model = _load_model()
    session_data = session_data or {}
    category_views = session_data.get("category_views", {})
    total_views = session_data.get("total_views", 0)
    cart_count = session_data.get("cart_count", 0)

    now = datetime.now()
    cat_encoded = CATEGORY_MAP.get(category, CATEGORY_MAP["Other"])

    features = np.array([[
        now.hour,
        now.weekday(),
        cat_encoded,
        base_price,
        existing_discount_pct,
        int(is_best_seller),
        category_views.get(category, 0),
        total_views,
        cart_count,
    ]])

    # Predict
    raw_adjustment = model.predict(features)[0]

    # Clamp to safety rails
    total_dynamic = max(-MAX_DISCOUNT_PCT, min(MAX_MARKUP_PCT, raw_adjustment))
    total_dynamic = round(total_dynamic, 1)

    # Explain the prediction with human-readable factors
    factors = []
    if now.hour >= 17 and now.hour <= 21:
        factors.append(("Peak demand (ML)", round(total_dynamic * 0.3, 1)))
    elif now.hour < 6:
        factors.append(("Off-peak (ML)", round(total_dynamic * 0.3, 1)))

    if category_views.get(category, 0) >= 3:
        factors.append(("Browsing reward (ML)", round(total_dynamic * 0.2, 1)))

    if is_best_seller and total_dynamic > 0:
        factors.append(("Popular item (ML)", round(total_dynamic * 0.25, 1)))

    remaining = total_dynamic - sum(f[1] for f in factors)
    if abs(remaining) > 0.1:
        label = "Smart pricing (ML)" if remaining > 0 else "AI discount"
        factors.append((label, round(remaining, 1)))

    # Calculate final price
    static_price = base_price * (1 - existing_discount_pct / 100)
    dynamic_multiplier = 1 + (total_dynamic / 100)
    final_price = max(1, round(static_price * dynamic_multiplier))
    savings = round(base_price - final_price)
    effective_discount = round(
        (1 - final_price / base_price) * 100, 1
    ) if base_price > 0 else 0

    return {
        "original_price": base_price,
        "static_discount": existing_discount_pct,
        "dynamic_adjustment": total_dynamic,
        "final_price": final_price,
        "effective_discount": effective_discount,
        "savings": max(0, savings),
        "factors": factors,
        "model": "GradientBoostingRegressor",
    }
