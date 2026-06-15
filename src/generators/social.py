import json
from pathlib import Path
from src.content_engine import ContentEngine
from src.config import COURSES, BRAND


class SocialPostGenerator:
    READY_TO_USE_POSTS = [
        {
            "platform": "skool_free",
            "title": "Engagement Hook — Free Group",
            "content": (
                "You uploaded your trust documents. NotebookLM turned them into a podcast.\n\n"
                "That's not the future. That's what I'm doing right now inside 1787 Wealth Academy.\n\n"
                "Upload your course material. Get flashcards. Get quizzes. Get an audio breakdown "
                "you can listen to on the way to work.\n\n"
                "The system is built. You just have to show up and use it.\n\n"
                "Drop a 🔥 if you want the walkthrough inside the community."
            ),
        },
        {
            "platform": "skool_paid",
            "title": "Value Drop — Paid Group",
            "content": (
                "Your trust is only as powerful as your understanding of it.\n\n"
                "If you can't explain what your irrevocable trust does — to your banker, "
                "your attorney, your family — it's just a document in a drawer.\n\n"
                "Inside the academy, I'm using AI tools to turn the legal language into plain "
                "English study guides, audio breakdowns, and quizzes you can actually retain.\n\n"
                "Because infrastructure you don't understand is infrastructure you won't use."
            ),
        },
        {
            "platform": "skool_free",
            "title": "Membership Pitch — Free Group",
            "content": (
                "The Wealth Academy just leveled up.\n\n"
                "Every course module now comes with an AI-generated audio breakdown — "
                "two hosts, walking you through the material like a podcast.\n\n"
                "Irrevocable trusts. Credit stacking. The Singleton Structure. All of it.\n\n"
                "This is what paid looks like."
            ),
        },
    ]

    def __init__(self, engine: ContentEngine):
        self.engine = engine
        self.output_dir = Path("outputs/social_posts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_skool_posts(self, course_key: str, count: int = 3) -> list[dict]:
        course = COURSES[course_key]

        prompt = f"""Write {count} Skool community posts for the course: {course['title']}

{course['description']}

Write {count} posts — mix of free group (engagement/teaser) and paid group (deep value drop).

For each post:
- platform: "skool_free" or "skool_paid"
- title: short description of the post's purpose
- content: the full post text

Format as JSON array with objects containing "platform", "title", and "content".

Voice rules:
- Peer-to-peer, warm but credible
- NEVER open with: "Most people...", "Did you know...", "Hot take:", "Unpopular opinion:"
- Short sentences. No filler. Authority without arrogance."""

        response = self.engine.generate_long(prompt)
        start = response.find("[")
        end = response.rfind("]") + 1
        posts = json.loads(response[start:end])

        output_path = self.output_dir / f"{course_key}_skool_posts.json"
        with open(output_path, "w") as f:
            json.dump({"course": course["title"], "posts": posts}, f, indent=2)

        md_path = self.output_dir / f"{course_key}_skool_posts.md"
        self._write_markdown(course["title"], "Skool", posts, md_path)

        print(f"  ✓ {len(posts)} Skool posts → {output_path}")
        return posts

    def generate_tiktok_scripts(self, course_key: str, count: int = 3) -> list[dict]:
        course = COURSES[course_key]

        prompt = f"""Write {count} TikTok/Instagram Reel scripts for: {course['title']}

Course: {course['description']}

Each script should:
- Be 45–75 seconds when spoken at normal pace (roughly 110–150 words)
- Follow the Think Like Money framework: Desire → Pain → Hope → CTA
- Tease the NotebookLM audio overview as a paid membership benefit
- End with a CTA to join 1787 Wealth Academy on Skool

Voice: casual/punchy for TikTok, bold/aspirational for Instagram.

Format as JSON array, each object with:
- "title": hook/topic of the script
- "platform": "tiktok" or "instagram"
- "hook": first line (make it a stopper)
- "body": main content
- "cta": call to action
- "full_script": complete script as single string"""

        response = self.engine.generate_long(prompt)
        start = response.find("[")
        end = response.rfind("]") + 1
        scripts = json.loads(response[start:end])

        output_path = self.output_dir / f"{course_key}_tiktok_scripts.json"
        with open(output_path, "w") as f:
            json.dump({"course": course["title"], "scripts": scripts}, f, indent=2)

        md_path = self.output_dir / f"{course_key}_tiktok_scripts.md"
        self._write_markdown(course["title"], "TikTok/IG", scripts, md_path)

        print(f"  ✓ {len(scripts)} TikTok/IG scripts → {output_path}")
        return scripts

    def save_ready_to_use_posts(self):
        output_path = self.output_dir / "ready_to_use_posts.json"
        with open(output_path, "w") as f:
            json.dump(self.READY_TO_USE_POSTS, f, indent=2)

        md_path = self.output_dir / "ready_to_use_posts.md"
        self._write_markdown("1787 Wealth Academy", "Ready-to-Use", self.READY_TO_USE_POSTS, md_path)

        print(f"  ✓ {len(self.READY_TO_USE_POSTS)} ready-to-use posts → {output_path}")

    def _write_markdown(self, course_title: str, platform: str, items: list[dict], path: Path):
        lines = [f"# {platform} Posts: {course_title}\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"## Post {i}: {item.get('title', '')}")
            if "platform" in item:
                lines.append(f"*Platform: {item['platform']}*\n")
            content = item.get("content") or item.get("full_script", "")
            lines.append(content)
            lines.append("\n---\n")
        path.write_text("\n".join(lines))
