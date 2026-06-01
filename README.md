# NOX — Elite AI Fitness Coach

NOX is a fully autonomous, data-driven fitness and nutrition agent designed for serious athletes. It combines the tactical intelligence of a strength coach, the precise macro tracking of a sports dietitian, and the motivational energy of a world-class mentor.

## Core Features

1. **The Great Lock-In**: A focus-mode scheduling engine that analyzes your performance history to recommend the optimal times and days to train.
2. **Workout Tracker**: Real-time logging, progressive overload calculations, and PR detection using a robust exercise library.
3. **Training Splits**: Expert-curated programs (Dorian Yates HIT, Bro Split, PPL, etc.) mapped directly to your profile.
4. **Knowledge Vault**: A searchable database of training wisdom from legends like Mike Mentzer, Arnold, and Jay Cutler.
5. **Nutrition Engine**: TDEE-driven macro tracking, automatic diet chart generation, and compliance scoring.
6. **NOX AI**: A localized LLM coach (powered by Ollama/Llama 3.1) that reads all your live telemetry and responds dynamically using a Multi-Armed Bandit strategy selector (Motivational vs Analytical vs Concise).

## Architecture

- **Backend**: Python 3.10+ with SQLite (WAL mode)
- **Frontend**: React 18 SPA (Vanilla CSS, Glassmorphic dark theme)
- **AI Core**: Ollama (Local)

## Getting Started

1. **Install Requirements**:
   No external Python dependencies are required (uses standard library).
   Make sure you have Ollama installed locally to power the AI coach.

2. **Pull the AI Model**:
   ```bash
   ollama pull llama3.1:8b
   ```

3. **Start the Engine**:
   ```bash
   python -m fitness_nutrition_agent.agent --port 8080
   ```

4. **Access the Dashboard**:
   Open `http://localhost:8080` in your web browser.

## Directory Structure

```
├── fitness_nutrition_agent/
│   ├── agent.py            # Main orchestrator
│   ├── db.py               # SQLite Database engine
│   ├── fitness.py          # Session and PR tracking
│   ├── nutrition.py        # Macro tracking and TDEE
│   ├── lock_in.py          # Scheduling engine
│   ├── llm_coach.py        # NOX Persona and UCB1 logic
│   ├── knowledge_vault.py  # Wisdom search
│   ├── foods.py            # 100+ food database
│   ├── exercise_library.py # 80+ exercise database
│   ├── splits.py           # Training split templates
│   └── data/               # Seed data (knowledge, recipes)
├── web/
│   ├── index.html          # NOX UI shell
│   ├── app.js              # React Frontend
│   └── styles.css          # Premium Dark Theme
└── README.md
```
