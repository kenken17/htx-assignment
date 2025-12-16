import asyncio
import logging
import random
import traceback
from typing import Awaitable, Callable

from app.queue.errors import NonRetryableJobError
from app.queue.models import Job

log = logging.getLogger("queue")

Processor = Callable[[Job], Awaitable[None]]


class QueueManager:
    """
    Unified queue for video/audio processing.
    """

    def __init__(self) -> None:
        self._q: asyncio.Queue[str] = asyncio.Queue()
        self.jobs: dict[str, Job] = {}
        self._done: dict[str, asyncio.Event] = {}
        self._workers: list[asyncio.Task] = []

    def create_job(self, job: Job) -> Job:
        log.info(
            "job_created job_id=%s type=%s payload_keys=%s",
            job.id,
            job.type,
            list(job.payload.keys()),
        )

        self.jobs[job.id] = job
        self._done[job.id] = asyncio.Event()
        return job

    async def enqueue(self, job_id: str) -> None:
        log.info("job_enqueued job_id=%s type=%s", job_id, self.jobs[job_id].type)

        await self._q.put(job_id)

    async def wait(self, job_id: str) -> Job:
        await self._done[job_id].wait()
        return self.jobs[job_id]

    async def start(self, worker_count: int, processor: Processor) -> None:
        for idx in range(worker_count):
            log.info("worker_started idx=%s", idx)

            self._workers.append(asyncio.create_task(self._worker_loop(processor)))

    async def shutdown(self) -> None:
        for t in self._workers:
            t.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)

    async def _worker_loop(self, processor: Processor) -> None:
        while True:
            job_id = await self._q.get()
            job = self.jobs[job_id]

            log.info("job_pulled job_id=%s type=%s", job.id, job.type)

            job.attempt += 1
            job.status = "running"
            job.progress = max(job.progress, 1)
            job.message = "Starting"
            job.last_error = None
            job.touch()

            log.info("job_started job_id=%s attempt=%s", job.id, job.attempt)

            try:
                await processor(job)

                log.info(
                    "job_succeeded job_id=%s type=%s attempt=%s",
                    job.id,
                    job.type,
                    job.attempt,
                )

                job.status = "succeeded"
                job.progress = 100
                job.message = "Completed"
                job.touch()

            except NonRetryableJobError as e:
                log.error(
                    "job_failed_nonretryable job_id=%s type=%s error=%s",
                    job.id,
                    job.type,
                    str(e),
                )

                # Fail immediately for non-retryable cases
                job.status = "failed"
                job.message = "Failed (non-retryable)"
                job.last_error = str(e)
                job.touch()

            except BaseException as e:
                # Retryable failure
                job.last_error = f"{e}\n{traceback.format_exc()}"
                job.touch()

                if job.attempt < job.max_attempts:
                    log.warning(
                        "job_retrying job_id=%s type=%s attempt=%s/%s delay_s=%.2f error=%s",
                        job.id,
                        job.type,
                        job.attempt,
                        job.max_attempts,
                        delay,
                        str(e),
                    )

                    # exponential backoff + small jitter
                    base_delay = min(2 ** (job.attempt - 1), 30)
                    jitter = random.uniform(0, 0.5)
                    delay = base_delay + jitter

                    job.status = "retrying"
                    job.message = f"Retrying in {delay:.1f}s (attempt {job.attempt}/{job.max_attempts})"
                    job.touch()

                    await asyncio.sleep(delay)
                    await self._q.put(job.id)
                else:
                    log.error(
                        "job_failed job_id=%s type=%s attempts=%s error=%s",
                        job.id,
                        job.type,
                        job.attempt,
                        str(e),
                    )

                    job.status = "failed"
                    job.message = "Failed"
                    job.touch()

            finally:
                self._done[job_id].set()
                self._q.task_done()

                log.info("job_done job_id=%s status=%s", job.id, job.status)
