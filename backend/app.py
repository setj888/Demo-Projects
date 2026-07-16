"""
app.py  —  the small backend that ties everything together.

It:
  • serves the existing web app (index.html) at http://localhost:8000
  • exposes a few /api endpoints the app calls
  • holds your secret tokens (via .env) and talks to Centric / ERP / Power BI
    through sources.py

Run it:   uv run uvicorn app:app --reload --port 8000
Then open http://localhost:8000  (NOT the file directly — the app auto-detects
it is being served and switches from mock mode to live-backend mode).
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import engine
import sources

load_dotenv()  # read backend/.env if present

app = FastAPI(title="La Tua Pasta — Ordering Planner API")

# During development, allow the browser app to call these endpoints.
# Tighten `allow_origins` to your real domain before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/ingredients")
def get_ingredients():
    """Centric materials + ERP stock, merged into the shape the app expects."""
    materials = sources.fetch_materials()
    stock = sources.fetch_stock()
    return [{**m, "stock": stock.get(m["id"], 0)} for m in materials]


@app.get("/api/recipes")
def get_recipes():
    """Top-10 product recipes (dough + filling items, per kg finished) + yields."""
    return sources.fetch_recipes()


@app.post("/api/calculate")
def calculate(payload: dict):
    """Optional: run the requirements calc server-side instead of in the browser.
    Body: {"orders": [{"recipeId": "...", "qty": 40}, ...]}"""
    ingredients = get_ingredients()
    recipes = sources.fetch_recipes()
    return engine.calculate(payload.get("orders", []), ingredients, recipes)


@app.post("/api/push-powerbi")
def push_powerbi(rows: list[dict]):
    """Push the finished purchasing list to Power BI (keeps the token server-side)."""
    return sources.push_to_powerbi(rows)


# Serve the web app (index.html lives one folder up). Keep this LAST so the
# /api routes above take priority.
STATIC_DIR = Path(__file__).resolve().parent.parent
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
