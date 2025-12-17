<script setup lang="ts">
import { ref } from "vue";
import { search, getVideos, getTranscriptions } from "../api";

const q = ref("");
const topK = ref(3);
const results = ref<any[] | null>(null);
const error = ref<string | null>(null);

const videos = ref<any[]>([]);
const transcriptions = ref<any[]>([]);

async function runSearch() {
  error.value = null;
  results.value = null;
  try {
    const resp = await search(q.value, topK.value);
    results.value = resp.results ?? [];
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  }
}

async function loadRefs() {
  error.value = null;
  try {
    videos.value = await getVideos();
    transcriptions.value = await getTranscriptions();
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  }
}

function useVideoAsReference(v: any) {
  // Visual similarity proxy: use the video's summary (or filename) as the search query
  q.value = v.summary ?? v.filename ?? "";
  runSearch();
}

function useAudioAsReference(t: any) {
  // Audio similarity proxy: use transcription text (or filename) as the search query
  q.value = t.text ?? t.transcribed_text ?? t.filename ?? "";
  runSearch();
}

loadRefs();
</script>

<template>
  <section class="grid">
    <div class="card">
      <h3>Text Search</h3>
      <div class="row">
        <input
          v-model="q"
          placeholder="Search: objects, filenames, transcriptions..."
        />
        <input v-model.number="topK" type="number" min="1" max="20" />
        <button class="btn" @click="runSearch" :disabled="!q">Search</button>
      </div>

      <div v-if="error" class="error">
        <strong>Error</strong>
        <pre>{{ error }}</pre>
      </div>

      <div v-if="results" class="results">
        <h4>Results</h4>
        <ol class="list">
          <li v-for="(r, idx) in results" :key="idx">
            <pre class="mini result-text">{{ JSON.stringify(r, null, 2) }}</pre>
          </li>
        </ol>
      </div>
    </div>

    <div class="card">
      <h3>Reference Search</h3>
      <p class="muted">
        Use an existing video/transcription as a reference. This UI uses the
        item's summary/text as the query (acts as a proxy for visual/audio
        similarity when the backend exposes only a text-based search endpoint).
      </p>

      <div class="refs">
        <div>
          <h4>Videos</h4>
          <ul class="list">
            <li v-for="v in videos" :key="v.id ?? v.filename">
              <button class="link" @click="useVideoAsReference(v)">
                {{ v.filename ?? v.id }}
              </button>
            </li>
          </ul>
        </div>

        <div>
          <h4>Transcriptions</h4>
          <ul class="list">
            <li v-for="t in transcriptions" :key="t.id ?? t.filename">
              <button class="link" @click="useAudioAsReference(t)">
                {{ t.filename ?? t.id }}
              </button>
            </li>
          </ul>
        </div>
      </div>

      <button class="btn" style="margin-top: 10px" @click="loadRefs">
        Reload references
      </button>
    </div>
  </section>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  background: #fff;
}
.row {
  display: flex;
  gap: 10px;
  align-items: center;
}
input {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px;
  flex: 1;
}
input[type="number"] {
  max-width: 90px;
}
.btn {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
}
.list {
  padding-left: 18px;
}
.link {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
}
.error {
  margin-top: 10px;
  border: 1px solid #fecaca;
  background: #fff1f2;
  padding: 12px;
  border-radius: 12px;
  overflow: auto;
}
.results {
  margin-top: 10px;
}
.mini {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 10px;
  border-radius: 10px;
  overflow: auto;
}
.result-text {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  max-height: 150px;
  overflow-y: auto;
  font-size: 0.9rem;
  line-height: 1.4;
}
.refs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.muted {
  color: #6b7280;
}
</style>
