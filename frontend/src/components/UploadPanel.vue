<script setup lang="ts">
import { ref } from "vue";
import { upload } from "../api";
import { useJob } from "../useJob";

type Kind = "video" | "audio";

const kind = ref<Kind>("video");
const files = ref<File[]>([]);
const jobs = ref<{ filename: string; jobId: string }[]>([]);
const activeJobId = ref<string | null>(null);

const { job, result, error } = useJob(() => activeJobId.value);

function onPick(e: Event) {
  const input = e.target as HTMLInputElement;
  files.value = input.files ? Array.from(input.files) : [];
}

async function submit() {
  if (files.value.length === 0) return;
  jobs.value = [];
  activeJobId.value = null;

  for (const f of files.value) {
    const resp = await upload(
      kind.value === "video" ? "/process/video" : "/process/audio",
      f,
    );
    const jobId = resp.job_id ?? resp.jobId ?? resp.id ?? null;
    if (!jobId) {
      // Backend might be synchronous; treat response as result
      jobs.value.push({ filename: f.name, jobId: "(sync)" });
      activeJobId.value = null;
      continue;
    }
    jobs.value.push({ filename: f.name, jobId });
    // auto-follow the latest submitted job
    activeJobId.value = jobId;
  }
}
</script>

<template>
  <div>* Multiple files upload allowed</div>

  <section class="card">
    <div class="row">
      <label class="field">
        <span>Processing type</span>
        <select v-model="kind">
          <option value="video">Video</option>
          <option value="audio">Audio</option>
        </select>
      </label>

      <label class="field">
        <span>Select file(s)</span>
        <input
          type="file"
          :accept="kind === 'video' ? 'video/*' : 'audio/*'"
          multiple
          @change="onPick"
        />
      </label>

      <button class="primary" :disabled="files.length === 0" @click="submit">
        Submit
      </button>
    </div>

    <div></div>

    <br />
    <div v-if="jobs.length" class="jobs">
      <hr />

      <h3>Submitted jobs</h3>
      <ul>
        <li v-for="j in jobs" :key="j.filename">
          <button
            class="link"
            @click="activeJobId = j.jobId === '(sync)' ? null : j.jobId"
          >
            {{ j.filename }}
          </button>
          <span class="muted"> — {{ j.jobId }}</span>
        </li>
      </ul>
      <p class="muted">* Click a filename to view its job progress.</p>
    </div>

    <div v-if="job" class="status">
      <h3>Job status</h3>
      <div class="grid">
        <div>
          <span class="muted">ID</span>
          <div>{{ job.job_id || job.jobId }}</div>
        </div>
        <div>
          <span class="muted">Status</span>
          <div>{{ job.status }}</div>
        </div>
        <div>
          <span class="muted">Progress</span>
          <div>{{ job.progress ?? 0 }}%</div>
        </div>
      </div>
      <div class="msg">{{ job.message }}</div>
      <progress :value="job.progress ?? 0" max="100"></progress>
    </div>

    <div v-if="error" class="error">
      <strong>Error</strong>
      <pre>{{ error }}</pre>
    </div>

    <div v-if="result" class="result">
      <h3>Result</h3>
      <ResultViewer :result="result" />
    </div>
  </section>
</template>

<script lang="ts">
import ResultViewer from "./viewers/ResultViewer.vue";
export default { components: { ResultViewer } };
</script>

<style scoped>
.card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  background: #fff;
}
.row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 260px;
}
select,
input[type="file"] {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 8px;
}
.primary {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #111827;
  background: #111827;
  color: #fff;
  cursor: pointer;
}
.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.jobs {
  margin-top: 14px;
}
.link {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
}
.status {
  margin-top: 14px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.msg {
  margin: 8px 0;
}
.error {
  margin-top: 14px;
  border: 1px solid #fecaca;
  background: #fff1f2;
  padding: 12px;
  border-radius: 12px;
  overflow: auto;
}
.result {
  margin-top: 14px;
}
progress {
  width: 100%;
  height: 16px;
}
.muted {
  color: #6b7280;
}
</style>
