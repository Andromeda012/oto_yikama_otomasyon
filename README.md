# Car Wash Automation System

Car wash operations platform using a Vue/Vite frontend and Flask API backend. The project is structured as a Vercel deployment: the Vue app is built as a static frontend and Flask runs as a Python serverless function under `/api`.

## Stack

- Frontend: Vue 3 + Vite + JavaScript
- Backend: Python + Flask + Flask-SQLAlchemy
- Database: MySQL (external/managed database recommended for Vercel)
- Deployment: Vercel + GitHub

## Structure

```text
car-wash-automation/
├── api/                    Vercel Python function entrypoint
│   └── index.py
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/         Flask API routes
│   │   ├── services/
│   │   └── utils/
│   ├── config/
│   ├── tests/
│   └── run.py              Local Flask entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── router/
│   │   ├── services/
│   │   └── views/
│   └── package.json
├── requirements.txt        Vercel Python dependencies
├── vercel.json
└── .gitignore
```

## Local development

### Backend

From the project root:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and configure the MySQL connection.

Then:

```bash
cd backend
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

During local development, set `VITE_API_BASE_URL=http://localhost:5000` in `frontend/.env` if the Vue app is running separately from Flask.

## Vercel deployment

Import the GitHub repository into Vercel. The repository already contains the Vercel configuration. Vercel builds the Vue application from `frontend/` and exposes the Flask application through `api/index.py`.

Set these environment variables in Vercel:

- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS`

For a same-domain deployment, `VITE_API_BASE_URL` can remain empty so the frontend calls `/api/...`.
