from __future__ import annotations

import argparse
from pathlib import Path

from .db import Database
from .fitness import FitnessCoach
from .knowledge_vault import KnowledgeVault
from .llm_coach import LLMCoach
from .lock_in import LockIn
from .nutrition import NutritionAssistant
from .web_server import run_server


class FitnessAgent:
    def __init__(self, db_path: Path, data_dir: Path) -> None:
        self.db = Database(db_path)
        self.fitness = FitnessCoach(self.db)
        self.nutrition = NutritionAssistant(self.db, data_dir / "recipes.json")
        self.lock_in = LockIn(self.db)
        self.knowledge = KnowledgeVault(data_dir / "knowledge.json")
        self.coach = LLMCoach(self.db)

    def chat(self, user_message: str) -> dict:
        return self.coach.chat(user_message)


def main() -> None:
    parser = argparse.ArgumentParser(description="NOX AI Fitness Coach")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the web server on")
    args = parser.parse_args()

    # Determine paths
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / "agent_data.sqlite3"
    data_dir = base_dir / "fitness_nutrition_agent" / "data"

    print("Initializing NOX Agent...")
    agent = FitnessAgent(db_path, data_dir)
    status = agent.coach.status()

    print("\n" + "=" * 50)
    print("NOX AI COACH - INITIALIZATION COMPLETE")
    print("=" * 50)
    if status["enabled"]:
        print(f"[LLM] Ollama active (Model: {status['model']})")
    else:
        print(f"[LLM] WARNING: {status['message']}")
    print("=" * 50 + "\n")

    run_server(agent, port=args.port)


if __name__ == "__main__":
    main()
