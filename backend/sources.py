"""
sources.py  —  THE INTEGRATION LAYER (this is the file you edit to go live).

Three data sources, three functions. Right now each returns MOCK data from
mock_data.json so the app runs immediately. To go live, fill in the TODO
sections with real API calls. Nothing else in the project needs to change.

  1. Centric  -> materials (ingredients) + recipes (BOMs) + yields
  2. ERP      -> live stock levels
  3. Power BI -> push the finished purchasing list to a dashboard

Secrets (tokens, URLs) come from the .env file — never hard-code them here.
"""

import json
import os
from pathlib import Path

import requests  # used by the real versions; harmless if you stay on mock

# Load the mock data once at startup.
_MOCK = json.loads((Path(__file__).parent / "mock_data.json").read_text(encoding="utf-8"))

# Read config from environment (.env). Empty string => stay on mock data.
CENTRIC_BASE_URL = os.getenv("CENTRIC_BASE_URL", "")
CENTRIC_TOKEN    = os.getenv("CENTRIC_TOKEN", "")
ERP_BASE_URL     = os.getenv("ERP_BASE_URL", "")
ERP_API_KEY      = os.getenv("ERP_API_KEY", "")
POWERBI_PUSH_URL = os.getenv("POWERBI_PUSH_URL", "")


def _expand_recipe(recipe: dict) -> dict:
    """Turn a compact recipe (dough name + fill list) into the full item list
    the calculator and the web UI expect: every item has id, qty (g/kg
    finished), and type ('dough' or 'fill')."""
    dough_items = [{**it, "type": "dough"} for it in _MOCK["dough"][recipe["dough"]]]
    fill_items  = [{**it, "type": "fill"}  for it in recipe["fill"]]
    return {
        "id": recipe["id"], "name": recipe["name"], "shape": recipe["shape"],
        "pcsPerKg": recipe["pcsPerKg"], "yield": recipe["yield"],
        "items": dough_items + fill_items,
    }


# ===========================================================================
# 1. CENTRIC  —  materials (ingredients) and recipes (BOMs + yields)
# ===========================================================================
def fetch_materials() -> list[dict]:
    """Ingredient master WITHOUT stock: id, name, unit, pack, cost, supplier."""
    if not CENTRIC_BASE_URL:
        return _MOCK["materials"]

    # ==== TODO: REAL CENTRIC CALL ====
    # r = requests.get(
    #     f"{CENTRIC_BASE_URL}/api/materials",
    #     headers={"Authorization": f"Bearer {CENTRIC_TOKEN}"},
    #     timeout=30,
    # )
    # r.raise_for_status()
    # return [
    #     {
    #         "id": d["code"], "name": d["description"], "unit": d["uom"],
    #         "pack": d["purchasePackSize"], "cost": d["standardCost"],
    #         "supplier": d["primarySupplier"],
    #     }
    #     for d in r.json()
    # ]
    raise NotImplementedError("Fill in the Centric materials call above.")


def fetch_recipes() -> list[dict]:
    """Top-10 product recipes, each fully expanded to dough + filling items
    (grams per kg finished) plus a process-yield fraction."""
    if not CENTRIC_BASE_URL:
        return [_expand_recipe(r) for r in _MOCK["recipes"]]

    # ==== TODO: REAL CENTRIC CALL ====
    # Pull each product's Bill of Materials + routing yield from Centric and
    # map it into: {id, name, shape, pcsPerKg, yield, items:[{id, qty, type}]}
    # where qty = grams of that material per 1 kg of finished product.
    raise NotImplementedError("Fill in the Centric recipes/BOM call above.")


# ===========================================================================
# 2. ERP  —  live stock levels (kept separate: it changes constantly)
# ===========================================================================
def fetch_stock() -> dict[str, float]:
    """Return {material_id: current_qty}. Keyed by the SAME id as Centric."""
    if not ERP_BASE_URL:
        return _MOCK["stock"]

    # ==== TODO: REAL ERP CALL ====
    # r = requests.get(
    #     f"{ERP_BASE_URL}/inventory/on-hand",
    #     headers={"x-api-key": ERP_API_KEY},
    #     timeout=30,
    # )
    # r.raise_for_status()
    # return {row["materialCode"]: row["onHandQty"] for row in r.json()}
    raise NotImplementedError("Fill in the ERP stock call above.")


# ===========================================================================
# 3. POWER BI  —  push the finished purchasing list to a dashboard
# ===========================================================================
def push_to_powerbi(rows: list[dict]) -> dict:
    """Send purchasing-list rows to a Power BI streaming/push dataset."""
    if not POWERBI_PUSH_URL:
        # Mock: pretend it worked so you can test the button end-to-end.
        return {"pushed": len(rows), "target": "mock (no POWERBI_PUSH_URL set)"}

    # ==== TODO: REAL POWER BI PUSH ====
    resp = requests.post(POWERBI_PUSH_URL, json=rows, timeout=30)
    resp.raise_for_status()
    return {"pushed": len(rows), "target": "Power BI"}
