# Demo (Pasta Co.)- Batch Ordering Planner

A working prototype web app that turns a **batch of customer orders** (product + kg, arriving
via WhatsApp) into a **raw-ingredient purchasing list** — exploding each product into its pasta
dough + filling ingredients, applying a **process-yield %** for production waste, and only
ordering the shortfall against current stock.

## Run it
Double-click `index.html`. Opens in your browser — no install, no server, no internet.
**Demo login:** `admin` / `admin`

## How to use
1. **Order Batch & Plan** — paste a WhatsApp message and click *Parse* (or add orders manually).
2. Click **Calculate ingredient requirements**.
3. **Purchasing List** — what to order, rounded to supplier pack sizes, with cost. Export CSV /
   push to Power BI.
4. **Ingredients & Stock** / **Recipes & Yields** — edit numbers to test scenarios.

## The data model (built with synthetic recipe data approximating a typical fresh filled pasta manufacturer)
- Every filled product ≈ **50% pasta dough + 50% filling** by weight.
- **Standard dough (30% egg):** Tipo 00 flour + pasteurised free-range egg + durum wheat + salt.
- **Vegan line (Pea & Shallot):** dough swaps egg for water.
- Recipes store **grams of each ingredient per 1 kg of finished product**, tagged *dough* / *filling*.
- **Spinach & Ricotta** and **Braised Beef** use the *exact* published ingredient breakdowns.
  The other eight are close estimates from the product descriptions — tune the percentages to
  your real production specs.

### Top 10 products included
Ravioli: Spinach & Ricotta · Braised Beef · Four Cheese · Pumpkin & Ricotta ·
Pea & Shallot (Vegan) · Beetroot & Goat Cheese.
Tortelloni: Mushroom & Cheese · Spinach & Ricotta · Tomato & Mozzarella · Nduja & Mascarpone.

## The calculation (with yield factored in)
```
raw factor      = order kg ÷ yield%                     (lower yield ⇒ order more)
ingredient need = (grams per kg ÷ 1000) × raw factor    (summed across the batch)
to order        = max(0, need − current stock)          (rounded up to pack size)
```
Yields are per-product estimates (88%–93%): meat/wet fillings and hand-folded tortelloni are set
lower (more waste) than simple cheese ravioli. Adjust each on the **Recipes & Yields** tab data.

## Going live — what to wire up
Everything is in **one file**. Only the **INTEGRATION LAYER** (bottom of the `<script>`) changes.

| Function | Connect to | Feeds |
|---|---|---|
| `authenticate()` | Real auth / SSO / Centric identity | Login gate |
| `syncFromCentric()` | Centric REST/OData API (materials + product BOMs + yields + stock) | Ingredients & Recipes |
| `importWhatsAppOrders()` | WhatsApp Business API webhook + small backend | Order batch |
| `pushToPowerBI()` | Power BI streaming dataset push URL | Live dashboards |

Fill in `CENTRIC_TOKEN` and `POWERBI_PUSH_URL` at the very bottom of the script.

## Notes & caveats
- **Ingredient percentages / costs / stock are illustrative.** Replace via Centric before real use.
- The WhatsApp parser is a keyword matcher for the demo — replace with the Business API webhook
  for reliable automatic imports.
- Security: the demo runs entirely in the browser. Before real use, add proper auth and move the
  Centric/WhatsApp/Power BI calls behind a small backend so API tokens are never exposed.

## Suggested next steps
1. Confirm which 10 products are actually your top sellers, and load real filling percentages.
2. Map Centric field names for materials, BOMs, yields and stock.
3. Stand up a tiny backend (Node/Python) for API tokens + WhatsApp webhooks.
4. Replace each integration-layer stub with a real call, one at a time.
