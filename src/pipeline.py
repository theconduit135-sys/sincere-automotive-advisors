"""
1787 Wealth Academy — NotebookLM Content Engine
Phase 2 content production pipeline.
"""

from pathlib import Path
from src.content_engine import ContentEngine
from src.generators import (
    FlashcardGenerator,
    SocialPostGenerator,
    SlideDeckGenerator,
    StudyGuideGenerator,
    ScriptGenerator,
)
from src.config import COURSES


ALL_COURSES = list(COURSES.keys())


class ContentPipeline:
    def __init__(self, api_key: str | None = None):
        self.engine = ContentEngine(api_key=api_key)
        self.flashcards = FlashcardGenerator(self.engine)
        self.social = SocialPostGenerator(self.engine)
        self.slides = SlideDeckGenerator(self.engine)
        self.study_guide = StudyGuideGenerator(self.engine)
        self.scripts = ScriptGenerator(self.engine)

    def run_course(self, course_key: str, skip: list[str] | None = None):
        skip = skip or []
        course = COURSES[course_key]
        print(f"\n{'='*60}")
        print(f"  {course['title']}")
        print(f"  Notebook: {course['notebook_name']}")
        print(f"{'='*60}")

        if "flashcards" not in skip:
            print("\n[1/5] Generating flashcards...")
            self.flashcards.generate(course_key)

        if "skool" not in skip:
            print("\n[2/5] Generating Skool posts...")
            self.social.generate_skool_posts(course_key)

        if "tiktok" not in skip:
            print("\n[3/5] Generating TikTok/IG scripts...")
            self.social.generate_tiktok_scripts(course_key)

        if "slides" not in skip:
            print("\n[4/5] Generating slide deck...")
            deck = self.slides.generate(course_key)
            self.slides.generate_pptx(course_key, deck)

        if "study_guide" not in skip:
            print("\n[5/5] Generating study guide...")
            self.study_guide.generate(course_key)

        print(f"\n  ✅ {course['title']} — complete")

    def run_audio_scripts(self, course_key: str):
        print(f"\n[Audio] Generating Audio Overview script...")
        self.scripts.generate_audio_overview_script(course_key)
        print(f"[Audio] Generating Module 1 intro script...")
        self.scripts.generate_module_intro_script(course_key, module_num=1)

    def run_all(self, skip: list[str] | None = None):
        print("\n🚀 1787 Wealth Academy — Content Production Pipeline")
        print(f"   Generating content for {len(ALL_COURSES)} courses\n")

        self.social.save_ready_to_use_posts()

        for course_key in ALL_COURSES:
            self.run_course(course_key, skip=skip)
            self.run_audio_scripts(course_key)

        self._print_summary()

    def _print_summary(self):
        print("\n" + "="*60)
        print("  PIPELINE COMPLETE — Output Summary")
        print("="*60)
        for folder in Path("outputs").iterdir():
            if folder.is_dir():
                files = list(folder.glob("*"))
                print(f"  {folder.name}/  ({len(files)} files)")
                for f in sorted(files):
                    size = f.stat().st_size
                    print(f"    ↳ {f.name}  ({size:,} bytes)")
        print("\n  Next steps (Phase 2 → 3):")
        print("  1. Create 4 notebooks at notebooklm.google.com")
        print("  2. Upload source files from Drive folder to each notebook")
        print("  3. Run Audio Overview generation in NotebookLM")
        print("  4. Post generated Skool content to free + paid groups")
        print("  5. Use TikTok scripts for content shoots")
