"""
engine.py  —  the calculation (same logic as the web app, moved server-side).

Given a batch of orders (product + kg), the ingredient master (with stock) and
the recipes, work out how much of each raw ingredient must be ORDERED.

  raw factor      = order kg / yield            (lower yield => order more)
  ingredient need = grams_per_kg / 1000 * raw factor   (summed across batch)
  to order        = max(0, need - stock), rounded up to the supplier pack size
"""

import math


def calculate(orders: list[dict], ingredients: list[dict], recipes: list[dict]) -> dict:
    ing_by_id = {i["id"]: i for i in ingredients}
    rec_by_id = {r["id"]: r for r in recipes}

    required: dict[str, float] = {}      # ingredient_id -> total qty needed (kg/L)
    total_finished = 0.0
    total_raw = 0.0

    for o in orders:
        recipe = rec_by_id.get(o.get("recipeId"))
        qty = float(o.get("qty") or 0)
        if not recipe or qty <= 0:
            continue
        raw_factor = qty / recipe["yield"]        # kg of raw input for qty finished
        total_finished += qty
        total_raw += raw_factor
        for it in recipe["items"]:
            required[it["id"]] = required.get(it["id"], 0.0) + (it["qty"] / 1000.0) * raw_factor

    lines = []
    for mat_id, need in required.items():
        ing = ing_by_id[mat_id]
        gap = max(0.0, need - ing["stock"])
        packs = math.ceil(gap / ing["pack"]) if gap > 0 else 0
        order_qty = packs * ing["pack"]
        cost = order_qty * ing["cost"]
        lines.append({
            "id": mat_id, "name": ing["name"], "supplier": ing["supplier"], "unit": ing["unit"],
            "need": round(need, 3), "stock": ing["stock"], "gap": round(gap, 3),
            "pack": ing["pack"], "packs": packs, "orderQty": order_qty, "cost": round(cost, 2),
            "status": "buy" if gap > 0 else "ok",
        })

    lines.sort(key=lambda l: (l["cost"], l["gap"]), reverse=True)
    return {
        "lines": lines,
        "totalCost": round(sum(l["cost"] for l in lines), 2),
        "toBuyCount": sum(1 for l in lines if l["status"] == "buy"),
        "orderLines": sum(1 for o in orders if float(o.get("qty") or 0) > 0),
        "totalFinished": round(total_finished, 2),
        "totalRaw": round(total_raw, 2),
    }
