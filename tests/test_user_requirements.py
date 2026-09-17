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


@pytest.mark.asyncio
async def test_extended_personal_profile_roundtrip():
    """Tests saving and retrieving 3-tier profile (personal details, preferences, constraints)."""
    await init_db()

    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)

        profile = UserRequirementsProfile(
            avoid_organizations=["Avoided Corp"],
            preferred_organizations=["ISRO", "DRDO"],
            date_of_birth="2000-05-15",
        )
        profile.personal.full_name = "Candidate Name"
        profile.personal.willing_to_relocate_all_india = True
        profile.role_preferences.preferred_roles = ["Software / IT", "Technical"]
        profile.role_preferences.avoid_roles = ["Police / Uniformed"]
        profile.constraints.willing_physical_tests = False
        profile.constraints.max_application_fee = 500
        profile.classification_preferences.unknown_handling = "REVIEW"

        saved = await repo.save_user_requirements(profile.model_dump(), "extended_test_user")
        assert saved.version >= 1

        fetched = await repo.get_user_requirements("extended_test_user")
        loaded_profile = UserRequirementsProfile.model_validate(fetched)

        assert loaded_profile.personal.full_name == "Candidate Name"
        assert loaded_profile.personal.willing_to_relocate_all_india is True
        assert loaded_profile.avoid_organizations == ["Avoided Corp"]
        assert "ISRO" in loaded_profile.preferred_organizations
        assert loaded_profile.role_preferences.avoid_roles == ["Police / Uniformed"]
        assert loaded_profile.constraints.willing_physical_tests is False
        assert loaded_profile.constraints.max_application_fee == 500
        assert loaded_profile.classification_preferences.unknown_handling == "REVIEW"

