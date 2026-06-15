#!/usr/bin/env python3
"""
1787 Wealth Academy — NotebookLM Content Engine
CLI entry point.

Usage:
  python main.py                          # Run full pipeline (all 4 courses)
  python main.py --course trust_os        # Single course
  python main.py --course credit_dispute --only flashcards,skool
  python main.py --list-courses           # Show available courses
  python main.py --audio trust_os         # Audio scripts only
  python main.py --ready-posts            # Save the ready-to-use Skool posts
"""

import argparse
import os
import sys
from src.pipeline import ContentPipeline, ALL_COURSES
from src.config import COURSES


def main():
    parser = argparse.ArgumentParser(
        description="1787 Wealth Academy — NotebookLM Content Engine"
    )
    parser.add_argument(
        "--course",
        choices=ALL_COURSES,
        help="Run pipeline for a single course",
    )
    parser.add_argument(
        "--only",
        help="Comma-separated list of steps to run: flashcards,skool,tiktok,slides,study_guide",
    )
    parser.add_argument(
        "--skip",
        help="Comma-separated list of steps to skip",
    )
    parser.add_argument(
        "--audio",
        choices=ALL_COURSES,
        metavar="COURSE",
        help="Generate audio overview + module intro scripts for a course",
    )
    parser.add_argument(
        "--ready-posts",
        action="store_true",
        help="Save the 3 ready-to-use Skool posts from the knowledge base",
    )
    parser.add_argument(
        "--list-courses",
        action="store_true",
        help="List all available courses",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ANTHROPIC_API_KEY"),
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )

    args = parser.parse_args()

    if args.list_courses:
        print("\nAvailable courses:")
        for key, course in COURSES.items():
            print(f"  {key:<25} {course['title']}")
            print(f"    Notebook: {course['notebook_name']}")
            print(f"    Modules: {course.get('modules', '?')}  |  Tier: {course['skool_tier']}")
        return

    if args.ready_posts:
        from src.generators.social import SocialPostGenerator
        sp = SocialPostGenerator(engine=None)
        sp.save_ready_to_use_posts()
        return

    if not args.api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Set it with: export ANTHROPIC_API_KEY=your_key_here")
        print("Or pass --api-key your_key_here")
        sys.exit(1)

    pipeline = ContentPipeline(api_key=args.api_key)

    if args.ready_posts:
        pass  # handled above before API key check

    if args.audio:
        pipeline.run_audio_scripts(args.audio)
        return

    # Build skip list
    all_steps = {"flashcards", "skool", "tiktok", "slides", "study_guide"}
    skip = set()

    if args.only:
        only = set(args.only.split(","))
        skip = all_steps - only
    elif args.skip:
        skip = set(args.skip.split(","))

    if args.course:
        pipeline.run_course(args.course, skip=list(skip))
        pipeline.run_audio_scripts(args.course)
    else:
        pipeline.run_all(skip=list(skip))


if __name__ == "__main__":
    main()
