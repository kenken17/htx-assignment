from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job(job_id: str, request: Request):
    qm = request.app.state.queue
    job = qm.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    return {
        "job_id": job.id,
        "type": job.type,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "error": job.error,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.get("/jobs/{job_id}/result")
def get_job_result(job_id: str, request: Request):
    qm = request.app.state.queue
    job = qm.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    if job.status == "queued" or job.status == "running":
        raise HTTPException(status_code=409, detail="job not completed yet")

    if job.status == "failed":
        raise HTTPException(
            status_code=500,
            detail={
                "message": "job failed",
                "error": job.error,
            },
        )

    # succeeded
    return {
        "job_id": job.id,
        "result": job.result,
    }
