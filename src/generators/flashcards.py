import json
import os
from pathlib import Path
from src.content_engine import ContentEngine
from src.config import COURSES


class FlashcardGenerator:
    def __init__(self, engine: ContentEngine):
        self.engine = engine
        self.output_dir = Path("outputs/flashcards")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, course_key: str, count: int = 20) -> list[dict]:
        course = COURSES[course_key]
        concepts = "\n".join(f"- {c}" for c in course["key_concepts"])

        prompt = f"""Generate {count} flashcards for the course: {course['title']}

Course description: {course['description']}

Key concepts to cover:
{concepts}

Format each flashcard as JSON with "front" (question) and "back" (answer).
Return a JSON array of flashcard objects.

Requirements:
- Questions should be specific and testable
- Answers should be concise but complete (2-4 sentences max)
- Include legal citations where relevant
- Mix conceptual questions with practical application questions
- Make answers actionable — students should be able to DO something with the knowledge"""

        response = self.engine.generate_long(prompt)

        # Parse JSON from response
        start = response.find("[")
        end = response.rfind("]") + 1
        cards = json.loads(response[start:end])

        # Save to file
        output_path = self.output_dir / f"{course_key}_flashcards.json"
        with open(output_path, "w") as f:
            json.dump({"course": course["title"], "cards": cards}, f, indent=2)

        # Also save markdown version
        md_path = self.output_dir / f"{course_key}_flashcards.md"
        self._write_markdown(course["title"], cards, md_path)

        print(f"  ✓ {len(cards)} flashcards → {output_path}")
        return cards

    def _write_markdown(self, course_title: str, cards: list[dict], path: Path):
        lines = [f"# Flashcards: {course_title}\n"]
        for i, card in enumerate(cards, 1):
            lines.append(f"## Card {i}")
            lines.append(f"**Q:** {card['front']}\n")
            lines.append(f"**A:** {card['back']}\n")
        path.write_text("\n".join(lines))
