# Car Wash Automation System

Car wash operations platform. This stage provides a navigable HTML interface and project structure. Business features, authentication, and the database are not implemented.

## Technology stack

- **Backend:** Python, Flask (HTML templates now; REST API later). MySQL planned for production.
- **Frontend:** HTML, CSS, JavaScript served by Flask. Vue.js is scaffolded in `frontend/` for a later component-based UI.
- **Deployment:** Docker, CapRover, GitHub

## Project structure

```text
car-wash-automation/
├── backend/
│   ├── app/
│   │   ├── routes/          HTML page routes + /api/health
│   │   ├── templates/       Admin interface (base + section pages)
│   │   ├── static/          CSS, JS, images
│   │   ├── models/          empty (later)
│   │   ├── services/        empty (later)
│   │   └── utils/
│   ├── config/
│   └── run.py
├── frontend/                Vue 3 + Vite scaffold for future SPA
├── docker/
└── docker-compose.yml
```

## Start the interface locally

From `backend/`:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`. Navigate Dashboard, Hesabım, Ayarlar, Tanımlar, Yönetim, and İstatistikler. Buttons and forms do not perform operations.

`/api/health` remains a process check only.

## Vue (later)

The current UI is Flask + Jinja. Vue lives in `frontend/` (`src/views`, `src/components`, `src/router`, `src/services/api.js`). When the SPA is built, it will call Flask REST APIs using `VITE_API_BASE_URL`. Do not run the Vue app to use the interface at this stage.

## Docker and CapRover

Backend and frontend stay independently deployable. Local compose:

```bash
docker compose up --build
```
