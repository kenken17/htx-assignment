import { ref, watchEffect } from "vue";
import { getJob, getJobResult } from "./api";

export function useJob(jobId: () => string | null) {
  const job = ref<any | null>(null);
  const result = ref<any | null>(null);
  const error = ref<string | null>(null);

  watchEffect((onCleanup) => {
    const id = jobId();
    job.value = null;
    result.value = null;
    error.value = null;
    if (!id) return;

    let cancelled = false;
    let timer: number | null = null;

    const tick = async () => {
      try {
        const j = await getJob(id);
        if (cancelled) return;
        job.value = j;

        if (j.status === "succeeded") {
          const r = await getJobResult(id);
          if (!cancelled) result.value = r.result ?? r;
          return;
        }
        if (j.status === "failed") {
          error.value = j.last_error ?? j.error ?? "Job failed";
          return;
        }
        timer = window.setTimeout(tick, 1000);
      } catch (e: any) {
        if (!cancelled) error.value = e?.message ?? String(e);
      }
    };

    tick();

    onCleanup(() => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    });
  });

  return { job, result, error };
}
