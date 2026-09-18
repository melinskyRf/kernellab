import pytest

from kernellab.application.job_service import JobService
from kernellab.application.lab_service import LabService
from kernellab.domain.enums import JobStatus, JobType
from kernellab.exceptions import JobNotFoundError


@pytest.fixture
def lab(lab_service: LabService):
    return lab_service.create_lab(name="job-test-lab")


@pytest.mark.unit
class TestCreateJob:
    def test_create_job(self, job_service: JobService, lab):
        job = job_service.create_job(lab_id=lab.id, job_type="RUN")
        assert job.type == JobType.RUN
        assert job.status == JobStatus.PENDING
        assert job.lab_id == lab.id


@pytest.mark.unit
class TestGetJob:
    def test_get_job(self, job_service: JobService, lab):
        created = job_service.create_job(lab_id=lab.id, job_type="RUN")
        fetched = job_service.get_job(created.id)
        assert fetched.id == created.id

    def test_get_job_not_found(self, job_service: JobService):
        with pytest.raises(JobNotFoundError):
            job_service.get_job("nonexistent-id")


@pytest.mark.unit
class TestListJobs:
    def test_list_jobs(self, job_service: JobService, lab):
        job_service.create_job(lab_id=lab.id, job_type="RUN")
        job_service.create_job(lab_id=lab.id, job_type="TEST")
        jobs = job_service.list_jobs()
        assert len(jobs) == 2

    def test_list_jobs_by_lab(self, job_service: JobService, lab_service: LabService):
        lab1 = lab_service.create_lab(name="lab-for-jobs-1")
        lab2 = lab_service.create_lab(name="lab-for-jobs-2")
        job_service.create_job(lab_id=lab1.id, job_type="RUN")
        job_service.create_job(lab_id=lab2.id, job_type="TEST")
        job_service.create_job(lab_id=lab1.id, job_type="BUILD")

        lab1_jobs = job_service.list_jobs(lab_id=lab1.id)
        assert len(lab1_jobs) == 2
        lab2_jobs = job_service.list_jobs(lab_id=lab2.id)
        assert len(lab2_jobs) == 1


@pytest.mark.unit
class TestMarkStatus:
    def test_mark_running(self, job_service: JobService, lab):
        job = job_service.create_job(lab_id=lab.id, job_type="RUN")
        updated = job_service.mark_running(job.id)
        assert updated.status == JobStatus.RUNNING
        assert updated.started_at is not None

    def test_mark_success(self, job_service: JobService, lab):
        job = job_service.create_job(lab_id=lab.id, job_type="RUN")
        updated = job_service.mark_success(job.id, exit_code=0, logs="all tests passed")
        assert updated.status == JobStatus.SUCCESS
        assert updated.exit_code == 0
        assert updated.logs == "all tests passed"
        assert updated.finished_at is not None

    def test_mark_failed(self, job_service: JobService, lab):
        job = job_service.create_job(lab_id=lab.id, job_type="RUN")
        updated = job_service.mark_failed(job.id, error="segfault", exit_code=139)
        assert updated.status == JobStatus.FAILED
        assert updated.error == "segfault"
        assert updated.exit_code == 139
        assert updated.finished_at is not None

    def test_mark_failed_not_found(self, job_service: JobService):
        with pytest.raises(JobNotFoundError):
            job_service.mark_running("nonexistent-id")
