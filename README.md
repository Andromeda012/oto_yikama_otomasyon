# Car Wash Automation

Vercel-ready Flask + Vue application with an external MySQL database.

## Architecture

- `frontend/`: Vue + Vite application and static production build.
- `backend/`: Flask application, models, API routes and services.
- `api/index.py`: Vercel Python serverless entry point for Flask API routes.
- `vercel.json`: Vercel build and routing configuration.

Vercel serves the Vue/Vite production build as the frontend and sends `/api/*` requests to the Flask serverless function. Persistent data lives in an external MySQL database.

## Database

The application never creates tables or seed data during Flask startup. This is intentional for serverless/production use.

Run migrations manually, in order, against the external MySQL database:

1. `backend/migrations/001_initial_schema.sql`
2. `backend/migrations/002_vehicle_tracking.sql`
3. `backend/migrations/003_sales_and_delivery.sql`

`003_sales_and_delivery.sql` adds the financial foundation used when a vehicle job is delivered:

- a service sale is created once per vehicle job;
- service lines are preserved in `sale_items`;
- an unpaid customer debit is created in `account_transactions`;
- the sale can later be marked paid, creating the matching payment transaction.

Configure the application with:

```text
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/DATABASE
SECRET_KEY=your-production-secret
```

`mysql://...` is also accepted and normalized automatically.

## Operational flow

```text
Appointment
    ↓
Vehicle Job
    ↓
Waiting → Checked In → Washing → Quality Check → Ready → Delivered
    ↓
Service Sale
    ↓
Customer Account / Payment
```

A vehicle can have only one active job at a time. A delivered or cancelled job is immutable from the status workflow.

## Vercel

Use the repository root (`./`) as the Root Directory.

Recommended settings:

- Framework Preset: `Vite`
- Build Command: `cd frontend && npm install && npm run build`
- Root Directory: `./`
- Output Directory: `frontend/dist`
- Environment variables: `DATABASE_URL`, `SECRET_KEY`

## Local development

Backend:

```bash
cd backend
python run.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

For local development, configure the frontend API base URL if the Vite app and Flask server run on different origins.

## Phase 2 database migration

After deploying Phase 2, run `backend/migrations/009_service_stock_and_indexes.sql` once against the external MySQL database. This creates the `service_products` table used to map service consumption to stock. Existing tables and data are not recreated.
