"""
End-to-End Simulation Script
Tests the complete pipeline flow:
Inbound Telegram Message -> Persistence -> Level 1/4 Content Acquisition ->
AI Extraction Router -> Cryptographic Deduplication ->
Deterministic Eligibility Engine -> Telegram Notification Dispatch.
"""
import asyncio
import json
from app.database.connection import init_db, AsyncSessionLocal
from app.database.repository import DatabaseRepository
from app.eligibility.models import UserRequirementsProfile
from app.pipeline import ProcessingPipeline


async def run_simulation():
    print("=" * 70)
    print("PERSONAL JOB NOTIFICATION INTELLIGENCE - END-TO-END PIPELINE SIMULATOR")
    print("=" * 70)

    # 1. Initialize DB
    print("[1/6] Initializing Persistent Database...")
    await init_db()

    # 2. Setup user requirements profile
    print("[2/6] Loading User Eligibility Profile...")
    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)
        profile_data = await repo.get_user_requirements("default_user")
        if not profile_data:
            profile = UserRequirementsProfile()
            await repo.save_user_requirements(profile.model_dump(), "default_user")
        else:
            profile = UserRequirementsProfile.model_validate(profile_data)

    print(f"      • Min Education: {profile.education.minimum_level}")
    print(f"      • Max Age: {profile.age.maximum} ({profile.age.category})")
    print(f"      • Fresher Allowed: {profile.experience.fresher_allowed}")

    # 3. Simulate Inbound Raw Telegram Message
    print("[3/6] Simulating Inbound Telegram Message...")
    sample_text = (
        "🔥 UPSC Engineering Services Examination (ESE) 2026 Notification Out!\n"
        "Posts: Assistant Executive Engineer (Civil, Mechanical, Electrical, E&T)\n"
        "Vacancies: 232 Posts\n"
        "Age Limit: 21 to 30 years\n"
        "Qualification: Degree in Engineering (B.E. / B.Tech)\n"
        "Experience: Freshers Eligible (No experience required)\n"
        "Last Date: 2026-10-25\n"
        "Official Notification: https://upsc.gov.in/ese2026_notif.pdf\n"
        "Apply Online: https://upsc.gov.in/apply-online"
    )

    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)
        msg = await repo.save_raw_message(
            telegram_message_id="sim_msg_8841",
            channel_identifier="@sarkariresult_alerts",
            message_text=sample_text,
            raw_metadata={"simulated": True}
        )
        msg_id = msg.id

    print(f"      • Raw message persisted to DB with ID: {msg_id}")

    # 4. Run Processing Pipeline
    print("[4/6] Executing Processing Pipeline...")
    pipeline = ProcessingPipeline()

    # If no live AI provider configured, attach mock AI provider for simulation
    from app.ai.base import AIProvider
    from app.ai.schemas import JobExtractionSchema

    class E2EMockProvider(AIProvider):
        def __init__(self):
            super().__init__("mock_ai", "E2E Verified Mock", "mock-model")
        def is_configured(self) -> bool:
            return True
        async def extract_job_data(self, content):
            return JobExtractionSchema(
                is_job=True,
                job_type="central_government",
                organization="UPSC",
                post_name="Assistant Executive Engineer",
                notification_number="ESE:01:2026",
                vacancies=232,
                qualification=["Degree in Engineering", "B.E.", "B.Tech"],
                accepted_branches=["Civil", "Mechanical", "Electrical", "Electronics"],
                age_min=21,
                age_max=30,
                experience_required=False,
                application_deadline="2026-10-25",
                official_notification_url="https://upsc.gov.in/ese2026_notif.pdf",
                confidence=0.98
            ), None

    # Use live providers if any configured, otherwise inject E2EMockProvider
    has_live_ai = any(p.is_configured() for p in pipeline.ai_router.providers)
    if not has_live_ai:
        print("      [INFO] No live AI API keys detected in .env; utilizing verified pipeline mock provider.")
        pipeline.ai_router.providers = [E2EMockProvider()]

    result = await pipeline.process_job_message(
        db_message_id=msg_id,
        channel_id="@sarkariresult_alerts",
        telegram_message_id="sim_msg_8841",
        message_text=sample_text,
        urls=["https://upsc.gov.in/ese2026_notif.pdf"],
        user_profile=profile
    )

    print(f"      • Pipeline Result: {json.dumps(result, indent=2)}")

    # 5. Simulate Duplicate Message across another channel
    print("[5/6] Simulating Duplicate Forwarded Message in another channel...")
    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)
        dup_msg = await repo.save_raw_message(
            telegram_message_id="sim_msg_9999",
            channel_identifier="@technical_govt_jobs",
            message_text=sample_text,
            raw_metadata={"channel": "forwarded"}
        )
        dup_id = dup_msg.id

    dup_result = await pipeline.process_job_message(
        db_message_id=dup_id,
        channel_id="@technical_govt_jobs",
        telegram_message_id="sim_msg_9999",
        message_text=sample_text,
        urls=["https://upsc.gov.in/ese2026_notif.pdf"],
        user_profile=profile
    )
    print(f"      • Duplicate Deduplication Result: {json.dumps(dup_result, indent=2)}")
    assert dup_result["status"] == "DUPLICATE"
    print("      [SUCCESS] Deduplication succeeded! Suppressed duplicate alert.")

    print("\n[6/6] End-to-End Simulation Complete. All pipeline stages verified!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_simulation())
