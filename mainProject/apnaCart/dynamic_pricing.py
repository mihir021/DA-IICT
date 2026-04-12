"""
dynamic_pricing.py — Session-aware dynamic pricing engine for BasketIQ.

Algorithm: Adaptive Demand-Based Pricing (ADP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This implements a multi-factor pricing strategy that adjusts prices
in real-time based on:

1. **Time-of-Day Factor**  — Evening (5-9 PM) cooking hours get slight
   markup on fresh produce; late-night/early-morning gets discounts.

2. **Session Engagement**  — Tracks how many times a user views products
   in the same category. Repeated browsing triggers a small "nudge"
   discount to encourage conversion (diminishing returns).

3. **Demand Popularity**   — Best-sellers get a small premium; slow-moving
   items get a discount to clear stock.

4. **Cart Abandonment**    — If session has items viewed but no cart adds,
   offer an increasing micro-discount as an incentive.

Safety Rails:
- Maximum markup:  +8%  (from base price)
- Maximum discount: -15% (from base price)
- All adjustments are additive percentages, clamped to these limits.
- Original base price is NEVER modified in the database.
"""

import math
from datetime import datetime


# ── Configuration ────────────────────────────────────────────────────
MAX_MARKUP_PCT = 8       # Maximum price increase (%)
MAX_DISCOUNT_PCT = 15    # Maximum price decrease (%)

# Time-of-day brackets (hour of day → adjustment %)
_TIME_ADJUSTMENTS = {
    # Late night / early morning — small discount to attract orders
    range(0, 6):   -3,
    # Morning — neutral
    range(6, 11):   0,
    # Lunch prep — slight bump on fresh items
    range(11, 14):  2,
    # Afternoon — neutral, slight discount
    range(14, 17): -1,
    # Evening cooking rush (peak demand)
    range(17, 21):  4,
    # Night wind-down
    range(21, 24): -2,
}

# Category weights for time-based adjustments
# (fresh categories are more affected by time-of-day)
_TIME_SENSITIVE_CATEGORIES = {
    "Vegetables": 1.5,
    "Fruits": 1.3,
    "Dairy": 1.2,
    "default": 0.5,
}

# Engagement thresholds
_ENGAGEMENT_DISCOUNTS = [
    # (min_views, discount_pct)
    (3, -2),    # 3 views in category → 2% off
    (5, -4),    # 5 views → 4% off
    (8, -6),    # 8 views → 6% off (max engagement discount)
]

# Popularity adjustments
_BEST_SELLER_PREMIUM = 3    # +3% for best sellers
_LOW_DISCOUNT_BOOST = -3    # -3% extra for items with no existing offer


def _get_time_adjustment(category: str) -> float:
    """Calculate time-of-day based price adjustment."""
    hour = datetime.now().hour
    base_adj = 0
    for time_range, adj in _TIME_ADJUSTMENTS.items():
        if hour in time_range:
            base_adj = adj
            break

    # Apply category sensitivity multiplier
    multiplier = _TIME_SENSITIVE_CATEGORIES.get(
        category,
        _TIME_SENSITIVE_CATEGORIES["default"]
    )
    return base_adj * multiplier


def _get_engagement_adjustment(session_views: dict, category: str) -> float:
    """
    Calculate discount based on how many products in this category
    the user has viewed in their current session.
    """
    view_count = session_views.get(category, 0)
    discount = 0
    for min_views, disc in _ENGAGEMENT_DISCOUNTS:
        if view_count >= min_views:
            discount = disc
    return discount


def _get_popularity_adjustment(is_best_seller: bool, has_existing_discount: bool) -> float:
    """Best sellers get a small premium; items with no offers get a boost."""
    if is_best_seller:
        return _BEST_SELLER_PREMIUM
    if not has_existing_discount:
        return _LOW_DISCOUNT_BOOST
    return 0


def _get_cart_abandonment_adjustment(
    session_views_total: int,
    cart_item_count: int
) -> float:
    """
    If user has browsed many products but hasn't added to cart,
    offer a gentle nudge discount.
    """
    if cart_item_count > 0 or session_views_total < 5:
        return 0

    # Logarithmic decay — more views without cart = bigger nudge
    # but caps out at about -5%
    nudge = -min(5, math.log2(max(1, session_views_total - 4)) * 1.5)
    return round(nudge, 1)


def calculate_dynamic_price(
    base_price: float,
    existing_discount_pct: float,
    category: str,
    is_best_seller: bool,
    session_data: dict = None,
) -> dict:
    """
    Calculate the dynamically adjusted price for a product.

    Args:
        base_price:          Original MRP / list price
        existing_discount_pct: Current static discount % (e.g., 10 for 10%)
        category:            Product category string
        is_best_seller:      Whether product is flagged as best-seller
        session_data:        Dict with keys:
                             - 'category_views': {category: count}
                             - 'total_views': int
                             - 'cart_count': int

    Returns:
        dict with:
            - 'original_price': base_price
            - 'static_discount': existing_discount_pct
            - 'dynamic_adjustment': float (total dynamic % change)
            - 'final_price': int (rounded final price)
            - 'effective_discount': float (total effective discount %)
            - 'factors': list of (label, pct) tuples explaining adjustments
            - 'savings': int (amount saved)
    """
    session_data = session_data or {}
    category_views = session_data.get("category_views", {})
    total_views = session_data.get("total_views", 0)
    cart_count = session_data.get("cart_count", 0)

    factors = []

    # 1. Time-of-day
    time_adj = _get_time_adjustment(category)
    if time_adj != 0:
        label = "Peak demand" if time_adj > 0 else "Off-peak discount"
        factors.append((label, time_adj))

    # 2. Engagement
    eng_adj = _get_engagement_adjustment(category_views, category)
    if eng_adj != 0:
        factors.append(("Browsing reward", eng_adj))

    # 3. Popularity
    pop_adj = _get_popularity_adjustment(
        is_best_seller,
        existing_discount_pct > 0
    )
    if pop_adj != 0:
        label = "Popular item" if pop_adj > 0 else "Special offer"
        factors.append((label, pop_adj))

    # 4. Cart nudge
    cart_adj = _get_cart_abandonment_adjustment(total_views, cart_count)
    if cart_adj != 0:
        factors.append(("Just for you", cart_adj))

    # Sum all dynamic adjustments
    total_dynamic = sum(f[1] for f in factors)

    # Clamp to safety rails
    total_dynamic = max(-MAX_DISCOUNT_PCT, min(MAX_MARKUP_PCT, total_dynamic))

    # Calculate prices
    static_price = base_price * (1 - existing_discount_pct / 100)
    dynamic_multiplier = 1 + (total_dynamic / 100)
    final_price = max(1, round(static_price * dynamic_multiplier))
    savings = round(base_price - final_price)
    effective_discount = round((1 - final_price / base_price) * 100, 1) if base_price > 0 else 0

    return {
        "original_price": base_price,
        "static_discount": existing_discount_pct,
        "dynamic_adjustment": round(total_dynamic, 1),
        "final_price": final_price,
        "effective_discount": effective_discount,
        "savings": max(0, savings),
        "factors": factors,
    }
