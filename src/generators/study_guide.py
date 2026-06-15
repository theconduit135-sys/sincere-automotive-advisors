import json
from pathlib import Path
from src.content_engine import ContentEngine
from src.config import COURSES


class StudyGuideGenerator:
    def __init__(self, engine: ContentEngine):
        self.engine = engine
        self.output_dir = Path("outputs/study_guides")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, course_key: str) -> dict:
        course = COURSES[course_key]

        prompt = f"""Create a comprehensive student study guide for: {course['title']}

{course['description']}

The study guide should include:
1. Course overview (2-3 paragraphs in plain English — no legal/financial jargon)
2. Module-by-module breakdown ({course.get('modules', 'multiple')} modules)
   - Module title
   - What students will learn
   - 3-5 key takeaways
   - One action item per module
3. Key terms glossary (define every technical term in plain language)
4. "Put It Into Practice" section — 3-5 real steps a student takes after finishing the course
5. Common mistakes to avoid (3-5 pitfalls)
6. Resources referenced in the course

Return as JSON with sections: overview, modules, glossary, action_steps, mistakes, resources"""

        response = self.engine.generate_long(prompt)
        start = response.find("{")
        end = response.rfind("}") + 1
        guide = json.loads(response[start:end])

        output_path = self.output_dir / f"{course_key}_study_guide.json"
        with open(output_path, "w") as f:
            json.dump({"course": course["title"], **guide}, f, indent=2)

        md_path = self.output_dir / f"{course_key}_study_guide.md"
        self._write_markdown(course["title"], guide, md_path)

        print(f"  ✓ Study guide → {output_path}")
        return guide

    def _write_markdown(self, course_title: str, guide: dict, path: Path):
        lines = [f"# Study Guide: {course_title}\n"]

        if overview := guide.get("overview"):
            lines.append("## Course Overview")
            lines.append(overview if isinstance(overview, str) else "\n".join(overview))
            lines.append("")

        if modules := guide.get("modules"):
            lines.append("## Module Breakdown")
            for m in modules:
                lines.append(f"\n### {m.get('title', 'Module')}")
                lines.append(m.get("description", ""))
                if takeaways := m.get("takeaways"):
                    lines.append("\n**Key Takeaways:**")
                    for t in takeaways:
                        lines.append(f"- {t}")
                if action := m.get("action_item"):
                    lines.append(f"\n**Action Item:** {action}")

        if glossary := guide.get("glossary"):
            lines.append("\n## Key Terms Glossary")
            if isinstance(glossary, dict):
                for term, definition in glossary.items():
                    lines.append(f"\n**{term}:** {definition}")
            elif isinstance(glossary, list):
                for item in glossary:
                    lines.append(f"\n**{item.get('term', '')}:** {item.get('definition', '')}")

        if steps := guide.get("action_steps"):
            lines.append("\n## Put It Into Practice")
            for i, step in enumerate(steps, 1):
                lines.append(f"{i}. {step}")

        if mistakes := guide.get("mistakes"):
            lines.append("\n## Common Mistakes to Avoid")
            for m in mistakes:
                lines.append(f"- {m}")

        if resources := guide.get("resources"):
            lines.append("\n## Resources")
            for r in resources:
                lines.append(f"- {r}")

        path.write_text("\n".join(lines))
