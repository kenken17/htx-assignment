export type JobStatus =
  | "queued"
  | "running"
  | "retrying"
  | "succeeded"
  | "failed";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function req(path: string, init?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res;
}

export async function upload(
  path: "/process/video" | "/process/audio",
  file: File,
) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await req(path, { method: "POST", body: fd });
  return res.json() as Promise<any>;
}

export async function getJob(jobId: string) {
  const res = await req(`/jobs/${encodeURIComponent(jobId)}`);
  return res.json() as Promise<any>;
}

export async function getJobResult(jobId: string) {
  const res = await req(`/jobs/${encodeURIComponent(jobId)}/result`);
  return res.json() as Promise<any>;
}

export async function getVideos() {
  const res = await req("/videos");
  return res.json() as Promise<any[]>;
}

export async function getTranscriptions() {
  const res = await req("/transcriptions");
  return res.json() as Promise<any[]>;
}

export async function search(q: string, topK = 5) {
  const res = await req(
    `/search?q=${encodeURIComponent(q)}&top_k=${encodeURIComponent(String(topK))}`,
  );
  return res.json() as Promise<any>;
}
