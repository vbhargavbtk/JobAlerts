import pytest
import pytest_asyncio
from app.database.connection import init_db, AsyncSessionLocal
from app.database.repository import DatabaseRepository
from app.eligibility.models import UserRequirementsProfile


@pytest.mark.asyncio
async def test_user_requirements_database_editing():
    await init_db()

    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)

        # 1. Read default or save new
        profile = UserRequirementsProfile()
        profile.age.maximum = 32
        profile.education.branches.append("Data Science")

        saved = await repo.save_user_requirements(profile.model_dump(), "test_user")
        assert saved.version >= 1
        assert saved.configuration["age"]["maximum"] == 32
        assert "Data Science" in saved.configuration["education"]["branches"]

        # 2. Update existing profile (user edit)
        initial_version = saved.version
        profile.age.maximum = 35
        updated = await repo.save_user_requirements(profile.model_dump(), "test_user")
        assert updated.version == initial_version + 1
        assert updated.configuration["age"]["maximum"] == 35

        # 3. Read back from database
        fetched = await repo.get_user_requirements("test_user")
        assert fetched["age"]["maximum"] == 35
