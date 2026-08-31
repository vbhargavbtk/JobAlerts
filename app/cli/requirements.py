"""
Command-Line Interface (CLI) Utility for User Requirements
Allows terminal-based inspection and updates to user eligibility criteria.
Usage:
  .venv/Scripts/python -m app.cli.requirements view
  .venv/Scripts/python -m app.cli.requirements set-age 32
  .venv/Scripts/python -m app.cli.requirements set-category OBC
"""
import sys
import asyncio
import json
from app.database.connection import AsyncSessionLocal, init_db
from app.database.repository import DatabaseRepository
from app.eligibility.models import UserRequirementsProfile


async def view_requirements():
    await init_db()
    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)
        reqs = await repo.get_user_requirements("default_user")
        if not reqs:
            reqs = UserRequirementsProfile().model_dump()
        print("\n" + "=" * 60)
        print("CURRENT USER ELIGIBILITY REQUIREMENTS PROFILE")
        print("=" * 60)
        print(json.dumps(reqs, indent=2))
        print("=" * 60 + "\n")


async def update_age(new_age: int):
    await init_db()
    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)
        reqs = await repo.get_user_requirements("default_user") or UserRequirementsProfile().model_dump()
        profile = UserRequirementsProfile.model_validate(reqs)
        profile.age.maximum = new_age
        saved = await repo.save_user_requirements(profile.model_dump(), "default_user")
        print(f"Updated maximum age to: {new_age} (Profile version: {saved.version})")


def main():
    if len(sys.argv) < 2:
        print("Usage: py -m app.cli.requirements [view | set-age <num>]")
        return

    cmd = sys.argv[1].lower()
    if cmd == "view":
        asyncio.run(view_requirements())
    elif cmd == "set-age" and len(sys.argv) > 2:
        age = int(sys.argv[2])
        asyncio.run(update_age(age))
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
