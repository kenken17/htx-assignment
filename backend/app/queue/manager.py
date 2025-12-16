import asyncio
import random
import traceback
from typing import Awaitable, Callable

from app.queue.errors import NonRetryableJobError
from app.queue.models import Job

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
        self.jobs[job.id] = job
        self._done[job.id] = asyncio.Event()
        return job

    async def enqueue(self, job_id: str) -> None:
        await self._q.put(job_id)

    async def wait(self, job_id: str) -> Job:
        await self._done[job_id].wait()
        return self.jobs[job_id]

    async def start(self, worker_count: int, processor: Processor) -> None:
        for _ in range(worker_count):
            self._workers.append(asyncio.create_task(self._worker_loop(processor)))

    async def shutdown(self) -> None:
        for t in self._workers:
            t.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)

    async def _worker_loop(self, processor: Processor) -> None:
        while True:
            job_id = await self._q.get()
            job = self.jobs[job_id]

            job.attempt += 1
            job.status = "running"
            job.progress = max(job.progress, 1)
            job.message = "Starting"
            job.last_error = None
            job.touch()

            try:
                await processor(job)

                job.status = "succeeded"
                job.progress = 100
                job.message = "Completed"
                job.touch()

            except NonRetryableJobError as e:
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
                    job.status = "failed"
                    job.message = "Failed"
                    job.touch()

            finally:
                self._done[job_id].set()
                self._q.task_done()
