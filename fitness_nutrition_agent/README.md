# NOX Fitness & Nutrition

This project includes:
- CLI app (terminal mode)
- Animated local website (React + HTML + CSS)
- Shared local SQLite backend for both interfaces
- Android download section placeholder in website UI
- Native Android project in `/Users/vivektripathi/Trial-Ai agent/nox-android`

## 1) Run Website (Recommended)

From workspace root:

```bash
cd "/Users/vivektripathi/Trial-Ai agent"
python3 -m fitness_nutrition_agent.web_server
```

Open:
- `http://127.0.0.1:8080`

LLM chatbot is currently hidden from the UI to reduce device load.

## 2) Run CLI (Optional)

```bash
cd "/Users/vivektripathi/Trial-Ai agent"
python3 -m fitness_nutrition_agent.main
```

## Local Data Storage

All logs are stored locally in:
- `fitness_nutrition_agent/agent_data.sqlite3`

## Android App

- Project path: `/Users/vivektripathi/Trial-Ai agent/nox-android`
- Android guide: `/Users/vivektripathi/Trial-Ai agent/nox-android/README.md`
- Website download link target: `/downloads/NOX-android-latest.apk`
- Publish helper script: `/Users/vivektripathi/Trial-Ai agent/scripts/publish_android_apk.sh`

## Global Hosting (Render)

This repo includes `/Users/vivektripathi/Trial-Ai agent/render.yaml` for one-click Render deploy.

1. Push this project to GitHub.
2. Create a new Render Blueprint service from that repo.
3. Deploy.
4. You will get a public URL like `https://nox-web.onrender.com`.

## Free Frontend Hosting (GitHub Pages)

You can host the NOX frontend for free on GitHub Pages.

1. Push repo to GitHub.
2. In repo settings, enable Pages with **GitHub Actions** source.
3. Keep this workflow file:
   - `/Users/vivektripathi/Trial-Ai agent/.github/workflows/deploy-pages.yml`
4. Push to `main`; the frontend from `fitness_nutrition_agent/web` deploys automatically.

Important:
- GitHub Pages hosts only static frontend.
- Backend API must still run separately (Render or your own server).
- Set backend URL in:
  - `/Users/vivektripathi/Trial-Ai agent/fitness_nutrition_agent/web/app.js`
  - `const API_BASE_URL = "https://your-backend-domain.com"`

### Custom Domain (`nox.in` / `nox.com`)

You need to purchase an available domain first (domain availability is external and not guaranteed).

After buying domain:
1. Open Render service settings -> Custom Domains.
2. Add your domain (for example `nox.in`).
3. Add the DNS records Render gives you at your domain registrar.
4. Wait for SSL certificate provisioning.

## Website Features

- KPI dashboard (goal, calories, streak, target delta)
- Goal editor
- Workout logger with adaptive plan output
- Meal logger with calorie estimation
- Recipe suggestion engine with filters
- Athlete hero visuals (Usain Bolt, CBum, Michael Phelps)
- Animated glassmorphism UI

## Local Athlete Images

Place your image files here:
- `fitness_nutrition_agent/web/assets/athletes/usain-bolt.jpg`
- `fitness_nutrition_agent/web/assets/athletes/chris-bumstead.jpg`
- `fitness_nutrition_agent/web/assets/athletes/michael-phelps.jpg`

If any image is missing, the UI shows:
- `fitness_nutrition_agent/web/assets/athletes/placeholder.svg`

## API Endpoints (served by web server)

- `GET /api/dashboard`
- `GET /api/profile`
- `POST /api/profile`
- `GET /api/workouts?days=30`
- `POST /api/workouts`
- `GET /api/adaptive-plan`
- `GET /api/meals`
- `POST /api/meals`
- `GET /api/calorie-summary?date=YYYY-MM-DD`
- `GET /api/recipes?goal=&meal_type=&max_calories=`
- `GET /api/coach/status`
- `POST /api/coach/chat`
- `POST /api/coach/feedback`
