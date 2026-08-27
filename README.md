# Car Wash Automation

Vercel-ready Flask + Vue application with an external MySQL database.

## Architecture

- `frontend/`: Vue + Vite application.
- `backend/`: Flask application, models, API routes and services.
- `api/index.py`: Vercel serverless entry point.
- `vercel.json`: Vercel routing and function configuration.

The Vue production build is included in the Flask serverless function. Flask serves the SPA and the `/api/*` endpoints from the same Vercel deployment.

## Database

The application does not create tables or seed data when Flask starts.

Configure an external MySQL connection with:

```text
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/DATABASE
SECRET_KEY=your-production-secret
```

`mysql://...` is also accepted and normalized automatically.

Database migrations/schema initialization should be handled separately from application startup.

## Vercel

Use the repository root (`./`) as the Root Directory.

Recommended project settings:

- Framework Preset: `Other` (the project is a custom Flask + Vite monorepo)
- Build Command: `cd frontend && npm install && npm run build`
- Root Directory: `./`
- Do not set a separate Output Directory; Flask serves the generated Vue build.
- Add `DATABASE_URL` and `SECRET_KEY` as environment variables when the external MySQL database is ready.

The deployment routes both the frontend and API through `api/index.py`.

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

For local frontend development, Vite can proxy API requests if configured later. In production, the Vue application and Flask API use the same Vercel domain.
