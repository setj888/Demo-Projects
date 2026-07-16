# Backend — La Tua Pasta Ordering Planner

This small Python backend is the "middle layer" between the web app and your real
systems. It holds your secret tokens and does the actual API calls, so nothing
sensitive ever lives in the browser.

```
Centric ─┐
ERP      ├──►  this backend (tokens + maths)  ──►  web app (UI)
         │                    │
         └── Power BI ◄───────┘  (push purchasing results to a dashboard)
```

## Run it (one time setup)

This machine's uv needs the documented workaround (uv lives in `~\.local\bin`).
From **PowerShell**, in this `backend` folder:

```powershell
$env:Path = "C:\Users\sethl\.local\bin;$env:Path"
uv sync --no-managed-python -p "C:\Users\sethl\AppData\Local\Python\pythoncore-3.14-64\python.exe"
```

## Run it (every time)

```powershell
$env:Path = "C:\Users\sethl\.local\bin;$env:Path"
uv run uvicorn app:app --reload --port 8000
```

Then open **http://localhost:8000** (not the file — opening via http switches the
app from mock DEMO mode to live BACKEND mode automatically). Stop it with Ctrl+C.

## How "mock vs live" works

- Every source starts on **mock data** (from `mock_data.json`) so it runs today.
- Add a real URL/token in `.env` and *that one source* goes live. Blank = stays mock.
- So you can switch on Centric, then ERP, then Power BI **one at a time**.

## The only file you edit to go live: `sources.py`

It has exactly three jobs, each with a `TODO` and a commented example:

| Function | Wire it to | Returns |
|---|---|---|
| `fetch_materials()` | Centric material master | ingredients: id, name, unit, pack, cost, supplier |
| `fetch_recipes()` | Centric product BOMs + yields | recipes: items (g per kg finished) + yield |
| `fetch_stock()` | ERP inventory | `{ material_id: current_qty }` |
| `push_to_powerbi()` | Power BI push dataset | confirmation |

## Step-by-step go-live plan

1. **Copy `.env.example` to `.env`.** Leave everything blank for now.
2. **Centric first.** Get the API base URL + token from your Centric admin. Put them
   in `.env`, then fill in the real call inside `fetch_materials()` and
   `fetch_recipes()`. Reload and check the Ingredients / Recipes tabs show real data.
3. **ERP stock next.** Add `ERP_BASE_URL` + `ERP_API_KEY`, fill in `fetch_stock()`.
   The key rule: return stock keyed by the **same id** Centric uses for each material.
4. **Power BI last.** In Power BI, create a *Streaming dataset* (API type), copy its
   Push URL into `POWERBI_PUSH_URL`. The "Push to Power BI" button now feeds a live
   dashboard.
5. **Then the extras:** WhatsApp Business API webhook (replaces the paste box) and
   company SSO login.

## Important IDs must match

Centric materials, ERP stock and recipe ingredients are all linked by the material
**id**. Whatever code Centric uses for "Tipo 00 Flour", the ERP must use the same
code in its stock feed, and the recipes must reference it. Agree on one id scheme.

## Notes
- `.env` holds secrets — never commit it to git. `.env.example` is the safe template.
- `allow_origins=["*"]` in `app.py` is fine for local dev; lock it to your real
  domain before production.
- Want the calculation centralised too? The backend already exposes `/api/calculate`
  — the app can POST orders to it instead of computing in the browser.
