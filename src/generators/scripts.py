import json
from pathlib import Path
from src.content_engine import ContentEngine
from src.config import COURSES


class ScriptGenerator:
    """Generates Audio Overview scripts and HeyGen-style video scripts."""

    def __init__(self, engine: ContentEngine):
        self.engine = engine
        self.output_dir = Path("outputs/scripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_audio_overview_script(self, course_key: str) -> dict:
        """Two-host podcast-style script for NotebookLM Audio Overview style content."""
        course = COURSES[course_key]

        prompt = f"""Write a two-host podcast-style Audio Overview script for: {course['title']}

{course['description']}

Format: Two hosts — Host A (Alex) asks questions and represents the student perspective.
Host B (Morgan) is the expert who teaches the material clearly.

Requirements:
- 8–12 minutes when read at podcast pace (~140 words/minute = 1100–1680 words)
- Open with a hook that makes someone stop scrolling on their commute
- Cover the 3 most important concepts from the course
- Use real examples and plain English — no jargon without explanation
- End with a clear summary and CTA to 1787 Wealth Academy on Skool
- Feel like a real conversation, not a lecture

Return as JSON:
{{
  "title": "Audio Overview: [course title]",
  "runtime_estimate": "X minutes",
  "hosts": {{"A": "Alex", "B": "Morgan"}},
  "segments": [
    {{
      "segment": "Intro",
      "lines": [
        {{"host": "A", "line": "..."}}
      ]
    }}
  ],
  "full_script": "complete script as a single string with HOST A: / HOST B: labels"
}}"""

        response = self.engine.generate_long(prompt)
        start = response.find("{")
        end = response.rfind("}") + 1
        script = json.loads(response[start:end])

        output_path = self.output_dir / f"{course_key}_audio_overview_script.json"
        with open(output_path, "w") as f:
            json.dump(script, f, indent=2)

        txt_path = self.output_dir / f"{course_key}_audio_overview_script.txt"
        txt_path.write_text(script.get("full_script", ""))

        print(f"  ✓ Audio Overview script (~{script.get('runtime_estimate', '?')}) → {output_path}")
        return script

    def generate_module_intro_script(self, course_key: str, module_num: int = 1) -> dict:
        """HeyGen-ready avatar script for a course module intro."""
        course = COURSES[course_key]

        prompt = f"""Write a HeyGen avatar video script for Module {module_num} of: {course['title']}

This is Ashanté Richardson speaking directly to camera as his avatar.

Course: {course['description']}

Script requirements:
- 60–90 seconds (100–150 words)
- Opens with a bold statement or fact — never "Welcome to Module {module_num}"
- Tells students exactly what they'll be able to DO after this module
- One specific, concrete example or case study
- Ends with "Let's get into it." or a variation

Return as JSON:
{{
  "module": {module_num},
  "course": "{course['title']}",
  "runtime_estimate": "X seconds",
  "script": "full script as single string",
  "production_notes": "camera direction, tone notes for HeyGen"
}}"""

        response = self.engine.generate(prompt)
        start = response.find("{")
        end = response.rfind("}") + 1
        script = json.loads(response[start:end])

        output_path = self.output_dir / f"{course_key}_module{module_num}_intro_script.json"
        with open(output_path, "w") as f:
            json.dump(script, f, indent=2)

        print(f"  ✓ Module {module_num} intro script → {output_path}")
        return script
