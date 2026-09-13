import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.database.connection import init_db, AsyncSessionLocal
from app.database.repository import DatabaseRepository
from app.database.models import Job, Source, Alert, UserJobStatus, ProcessedMessage


@pytest.mark.asyncio
async def test_repository_delete_single_job():
    await init_db()

    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)

        # 1. Create a dummy job
        fp = f"test_delete_{uuid.uuid4()}"
        job = await repo.create_job(
            fingerprint=fp,
            organization="Test Commission",
            post_name="Assistant Engineer",
            notification_number="EN/2026/01",
            structured_data={"title": "Assistant Engineer", "vacancies": 10},
            eligibility_status="ELIGIBLE"
        )
        job_id = job.id

        # 2. Add dependent records: Source, Alert, UserJobStatus, and a linked ProcessedMessage
        await repo.add_source(job_id=job_id, url="https://example.com/notif.pdf")
        await repo.record_alert(job_id=job_id, telegram_chat_id="123456", alert_type="ELIGIBLE")
        await repo.set_user_job_status(job_id=job_id, status="plan_to_apply")

        msg = await repo.save_raw_message(
            telegram_message_id=str(uuid.uuid4()),
            channel_identifier="test_channel",
            message_text="Recruitment announcement",
            raw_metadata={"raw": True}
        )
        await repo.update_message_status(message_id=msg.id, status="PROCESSED", job_id=job_id)

        # 3. Delete the job
        deleted = await repo.delete_job(job_id)
        assert deleted is True

        # 4. Verify job is gone
        assert await repo.get_job_by_id(job_id) is None

        # 5. Verify dependent records are cleanly removed
        src_res = await session.execute(select(Source).where(Source.job_id == job_id))
        assert src_res.scalar_one_or_none() is None

        alert_res = await session.execute(select(Alert).where(Alert.job_id == job_id))
        assert alert_res.scalar_one_or_none() is None

        status_res = await session.execute(select(UserJobStatus).where(UserJobStatus.job_id == job_id))
        assert status_res.scalar_one_or_none() is None

        # 6. Verify linked processed message is NOT deleted, but job_id is nullified
        refreshed_msg = await repo.get_message_by_telegram_id("test_channel", msg.telegram_message_id)
        assert refreshed_msg is not None
        assert refreshed_msg.job_id is None

        # 7. Deleting a non-existent job returns False
        assert await repo.delete_job("non-existent-id") is False


@pytest.mark.asyncio
async def test_repository_delete_jobs_by_status():
    await init_db()

    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)

        # Create two eligible jobs and one ineligible
        j1 = await repo.create_job(
            fingerprint=f"el1_{uuid.uuid4()}",
            organization="Org 1",
            post_name="Role 1",
            notification_number="NOTIF1",
            structured_data={},
            eligibility_status="ELIGIBLE"
        )
        j2 = await repo.create_job(
            fingerprint=f"el2_{uuid.uuid4()}",
            organization="Org 2",
            post_name="Role 2",
            notification_number="NOTIF2",
            structured_data={},
            eligibility_status="ELIGIBLE"
        )
        j3 = await repo.create_job(
            fingerprint=f"in1_{uuid.uuid4()}",
            organization="Org 3",
            post_name="Role 3",
            notification_number="NOTIF3",
            structured_data={},
            eligibility_status="NOT_ELIGIBLE"
        )

        deleted_count = await repo.delete_jobs_by_status("ELIGIBLE")
        assert deleted_count >= 2

        assert await repo.get_job_by_id(j1.id) is None
        assert await repo.get_job_by_id(j2.id) is None
        assert await repo.get_job_by_id(j3.id) is not None

        # Clean up j3
        await repo.delete_job(j3.id)


@pytest.mark.asyncio
async def test_api_delete_endpoints():
    await init_db()

    # Create a job via repository
    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)
        job = await repo.create_job(
            fingerprint=f"api_test_{uuid.uuid4()}",
            organization="API Org",
            post_name="API Specialist",
            notification_number="API-101",
            structured_data={},
            eligibility_status="ELIGIBLE"
        )
        job_id = job.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test DELETE /api/jobs/{job_id}
        res = await client.delete(f"/api/jobs/{job_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"

        # Test DELETE on already deleted job -> 404
        res404 = await client.delete(f"/api/jobs/{job_id}")
        assert res404.status_code == 404

        # Test DELETE /api/jobs?status=ELIGIBLE
        res_bulk = await client.delete("/api/jobs?status=ELIGIBLE")
        assert res_bulk.status_code == 200
        assert "deleted_count" in res_bulk.json()
