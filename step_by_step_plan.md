1) Scaffolding, Dev UX & Containers

Goal: one-command up (Docker) for React + FastAPI + Postgres.

Actions
- Repo layout

```
/app
  /frontend   (React + Vite + Tailwind)
  /backend    (FastAPI)
  /infra      (docker-compose, env, db init)
```

-   Docker Compose (infra/docker-compose.yml)
-   db: Postgres 16, named volume, healthcheck.
-   api: FastAPI (uvicorn) with live reload; mounts /backend.
-   web: React dev server; mounts /frontend.
-   Optional: pgadmin or adminer for manual DB inspection.
-   .env files
-   POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
-   API_PORT, WEB_PORT, CORS_ORIGINS
-   Backend bootstrap
-   FastAPI app with routers and CORS.
-   SQLAlchemy 2.0 + Alembic migrations (recommended) or SQLModel if you prefer.
-   Settings via pydantic-settings.
-   Frontend bootstrap
-   React + Vite + TypeScript.
-   TailwindCSS + PostCSS configured.
-   UI lib optional (headlessui/radix) kept minimal for v0.

Deliverables
-   docker compose up serves:
-   http://localhost:5173 (web) hitting
-   http://localhost:8000 (api)
-   DB reachable; GET /health returns {status:"ok"}.

Acceptance
-	Fresh clone → .env copy → single command boots all.
-	Frontend can call /health and show status “OK”.

⸻

2) Data Model, Migrations & CRUD API

Goal: solid schema + CRUD for Event, SellingPoint, EPT, Transaction.

Entities
-   Event
-   id (uuid), name (str, unique per org scope if needed), start_at (ts), end_at (ts)
-   SellingPoint
-   id (uuid), event_id (fk), name (str), location (POINT or lat/long numeric)
-   EPT
-   id (uuid), selling_point_id (fk), provider (enum: worldline,sumup,other), label (str)
-   Transaction
-   id (uuid), event_id (fk), selling_point_id (fk), ept_id (fk)
-   amount_cents (int), currency (char3, default CHF/EUR), occurred_at (ts)
-   card_last4 (char4)
-   source (str parser_name), source_row_hash (text, uniq for idempotency)

Indices/constraints
-	Index Transaction(event_id, occurred_at).
-	Unique (source, source_row_hash) to prevent duplicates.
-	FK cascade delete from Event → SellingPoints → EPTs → Transactions (or soft-delete if you prefer).

API (FastAPI)
-   GET/POST/PATCH/DELETE /events
-   GET/POST/PATCH/DELETE /events/{id}/selling-points
-   GET/POST/PATCH/DELETE /selling-points/{id}/epts
-   GET /events/{id}/summary → totals per selling point + per EPT
-   Pydantic schemas: Create/Update/Read variants; server-side validation.

Migrations
-	Alembic revision: create all tables + enums + indexes.

Deliverables
-	OpenAPI docs at /docs.
-	Alembic migration files checked in.
-	Seed script to create one sample event with 2 selling points, 3 EPTs.

Acceptance
-	CRUD roundtrips via curl/Swagger work.
-	Deleting an event removes its dependent data (by design).

⸻

3) CSV Import Pipeline (Mock now, pluggable later)

Goal: upload CSV, choose parser, ingest transactions with idempotency.

Design
-	Parser interface (strategy pattern)

```python
class BaseParser(Protocol):
    name: str
    def sniff(self, header: list[str]) -> bool: ...
    def parse(self, file_obj: IO[bytes]) -> Iterable[TransactionIn]: ...
PARSER_REGISTRY = {"mock_worldline": WorldlineMockParser()}
```

-	Mock parser: reads a simple CSV (checked in backend/samples/worldline_mock.csv) and yields consistent TransactionIn.
-	Import flow
-	POST /events/{id}/imports (multipart form):
-	fields: parser (select box), file (csv), optional ept_id fallback.
-	Synchronous for v0 (simple & predictable). If file > N MB later, flip to background task.
-	For each row:
-	Resolve SellingPoint/EPT (from CSV columns; if missing, fallback to provided ept_id).
-	Compute source_row_hash (e.g., SHA256 of normalized row).
-	Upsert Transaction; skip on unique-violation (idempotency).
-	Statuses
-	Return summary: {processed, inserted, skipped_duplicates, errors}.
-	Security
-	Max upload size, MIME/type check, CSV dialect sniffing.
-	Tests
-	Unit test parser; API test end-to-end on mock sample.

Deliverables
-	Parser interface + one mock_worldline implementation.
-	Upload endpoint + response summary.
-	Example CSV & Postman/Bruno collection.

Acceptance
-	Upload sample → transactions appear for the event.
-	Re-upload same file → 0 inserts, all skipped as duplicates.

⸻

4) Frontend: CRUD & Summaries

Goal: usable UI to manage data and see high-level numbers.

Pages & Components
-	Events List
-	Table of events, create button (modal or page).
-	Event Detail
-	Tabs: Summaries, Selling Points/EPTs, Import
-	Summaries tab
-	Card: totals (sum amount, count transactions).
-	Section: Selling Points list:
-	For each SP: name, location chip, totals, and nested EPT list with mini-totals.
-	Selling Points/EPTs tab
-	Inline CRUD (create/edit/delete) for SPs and EPTs.
-	Import tab
-	File picker + parser dropdown (default “Mock Worldline”).
-	On submit, show server summary {processed, inserted, skipped, errors}.

Tech choices
-	Data fetching: React Query (TanStack Query) with typed API client (OpenAPI generator or hand-rolled).
-	Forms: React Hook Form + Zod (client validation mirrors server).
-	Styling: Tailwind with small reusable components (Card, Badge, Table, Modal).
-	State: server-state only; keep client state minimal.

Deliverables
-	Navigable UI with working CRUD & import.
-	Summary numbers match API.
-	Empty states & error toasts.

Acceptance
-	Create event → add selling points/EPTs → import CSV → Summaries reflect imported totals.
-	Modify & delete flows work without page reloads.

⸻

5) Timeline Map View (Cumulative Bubble Animation)

Goal: show evolving totals on a map, circles sized by cumulative amount.

Data/Backend
-	Aggregation endpoint
-	GET /events/{id}/timeline?sellpoint=true&bucket=5m
-	Returns per selling point, time-bucketed cumulative totals:

```json
{
  "event": {"start_at": "...", "end_at": "..."},
  "buckets": ["2025-08-23T13:00:00Z", "2025-08-23T13:05:00Z", ...],
  "series": [
    {"selling_point_id":"...", "lat":46.52, "lng":6.57, "cumulative":[0, 1500, 2700, ...]},
    ...
  ]
}
```


-	Server computes:
-	bucket edges from event start/end,
-	sums amount_cents up to each bucket per SP (windowed cum-sum).
-	Keep it simple: one request returns the full series for v0.

Frontend
-	Map: Leaflet + OpenStreetMap tiles (fits the tech & licensing, no account).
-	UI
-	Time slider (range 0..N buckets).
-	Play/Pause button (simple setInterval).
-	Bubble sizing: radius = k * sqrt(amount) (square-root scaling keeps sizes readable).
-	Tooltip on hover: SP name, cum. amount formatted.
-	Legend: bubble size examples + currency.
-	Perf
-	≤ 50 SPs → render circles directly. (Cluster not needed v0.)
-	Debounce slider changes.

Deliverables
-	Map tab on Event Detail → “Timeline”.
-	Smooth animation across buckets; bubbles grow only (cumulative).

Acceptance
-	With mock data: moving the time slider increases circles at expected SPs.
-	Totals at final bucket match Summaries totals.

⸻

Cross-cutting notes
-	Deletion behavior
-	Confirm dialogs; show impact (“deletes X EPTs and Y transactions”).
-	Validation
-	Event: start_at < end_at.
-	SellingPoint: must have lat/lng.
-	Transaction: positive amount_cents, occurred_at within event window (warn but allow if slightly outside? For v0: enforce inside).
-	Currencies
-	v0: single currency per event (config on Event). Store in Transaction.currency anyway for v1 flexibility.
-	Testing
-	Minimal API unit tests + one UI smoke test (Playwright optional).
-	Docs
-	README with run, seed, and import instructions; screenshot/gif of timeline.