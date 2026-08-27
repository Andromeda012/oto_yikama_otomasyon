# Car Wash Automation

Vercel-ready Flask + Vue application with an external MySQL database.

## Architecture

- `frontend/`: Vue + Vite application.
- `backend/`: Flask application, models, API routes and services.
- `api/index.py`: Vercel serverless entry point.
- `vercel.json`: Vercel routing and function configuration.

Vercel serves the Vue/Vite production build as the static frontend. Flask runs as a Python serverless function for the `/api/*` endpoints in the same Vercel deployment.

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

- Framework Preset: `Vite`
- Build Command: `cd frontend && npm install && npm run build`
- Root Directory: `./`
- Output Directory: `frontend/dist`
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
