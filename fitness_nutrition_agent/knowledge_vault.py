from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------
# Knowledge Vault — Coach wisdom with keyword search & scoring
# ---------------------------------------------------------------

class KnowledgeVault:
    """Coach knowledge base with TF-IDF-style search (no vector DB needed)."""

    def __init__(self, knowledge_path: Path) -> None:
        self.chunks: list[dict[str, Any]] = []
        if knowledge_path.exists():
            with knowledge_path.open("r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        # Build inverted index
        self._index: dict[str, set[int]] = {}
        for i, chunk in enumerate(self.chunks):
            words = self._tokenize(chunk.get("content", "") + " " + " ".join(chunk.get("tags", [])))
            for word in words:
                self._index.setdefault(word, set()).add(i)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """Simple word tokenizer."""
        import re
        words = re.findall(r'[a-z]+', text.lower())
        # Remove stopwords
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "could",
                      "should", "may", "might", "can", "shall", "to", "of", "in", "for",
                      "on", "with", "at", "by", "from", "as", "into", "through", "during",
                      "before", "after", "above", "below", "between", "out", "off", "over",
                      "under", "again", "further", "then", "once", "and", "but", "or", "nor",
                      "not", "so", "yet", "both", "either", "neither", "each", "every", "all",
                      "any", "few", "more", "most", "other", "some", "such", "no", "only",
                      "own", "same", "than", "too", "very", "just", "because", "if", "when",
                      "that", "this", "these", "those", "i", "you", "he", "she", "it", "we",
                      "they", "me", "him", "her", "us", "them", "my", "your", "his", "its",
                      "our", "their", "what", "which", "who", "whom", "how", "why", "where"}
        return {w for w in words if w not in stopwords and len(w) > 2}

    def query(self, question: str, coach_filter: str | None = None,
              level: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        """Search knowledge base by keyword relevance."""
        query_words = self._tokenize(question)
        if not query_words:
            return self.chunks[:limit]

        # Score each chunk by keyword overlap (TF-IDF-ish)
        scores: list[tuple[int, float]] = []
        total_chunks = len(self.chunks)

        for i, chunk in enumerate(self.chunks):
            # Filter by coach
            if coach_filter and chunk.get("coach", "").lower() != coach_filter.lower():
                continue
            # Filter by level
            if level and chunk.get("difficulty_level", "").lower() != level.lower():
                continue

            chunk_words = self._tokenize(chunk.get("content", "") + " " + " ".join(chunk.get("tags", [])))
            if not chunk_words:
                continue

            # Calculate score: weighted overlap
            overlap = query_words & chunk_words
            if not overlap:
                continue

            # IDF-weighted score
            score = 0.0
            for word in overlap:
                doc_freq = len(self._index.get(word, set()))
                idf = math.log(total_chunks / (1 + doc_freq)) if total_chunks > 0 else 1
                score += idf

            # Boost for topic match
            topic = chunk.get("topic", "").lower()
            for qw in query_words:
                if qw in topic:
                    score *= 1.5

            scores.append((i, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scores[:limit]:
            chunk = self.chunks[idx]
            results.append({
                **chunk,
                "relevance_score": round(score, 2),
            })

        return results

    def get_coaches(self) -> list[str]:
        """Get list of all coaches in the knowledge base."""
        return sorted(set(c.get("coach", "") for c in self.chunks if c.get("coach")))

    def get_topics(self) -> list[str]:
        """Get list of all topics."""
        return sorted(set(c.get("topic", "") for c in self.chunks if c.get("topic")))

    def get_by_coach(self, coach: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get all knowledge chunks by a specific coach."""
        return [
            c for c in self.chunks
            if c.get("coach", "").lower() == coach.lower()
        ][:limit]
