<script setup lang="ts">
import { onMounted, ref } from "vue";
import { getTranscriptions, getVideos } from "../api";
import ResultViewer from "./viewers/ResultViewer.vue";

const videos = ref<any[]>([]);
const transcriptions = ref<any[]>([]);
const error = ref<string | null>(null);
const selected = ref<any | null>(null);

async function refresh() {
  error.value = null;
  try {
    videos.value = await getVideos();
    transcriptions.value = await getTranscriptions();
  } catch (e: any) {
    error.value = e?.message ?? String(e);
  }
}

onMounted(refresh);
</script>

<template>
  <section class="grid">
    <div class="card">
      <div class="row">
        <h3>Videos</h3>
        <button class="btn" @click="refresh">Refresh</button>
      </div>
      <ul class="list">
        <li v-for="v in videos" :key="v.id ?? v.filename" class="item">
          <button class="link" @click="selected = v">
            {{ v.filename ?? v.id }}
          </button>
          <span class="muted" v-if="v.created_at"> — {{ v.created_at }}</span>
        </li>
      </ul>
    </div>

    <div class="card">
      <div class="row">
        <h3>Transcriptions</h3>
        <button class="btn" @click="refresh">Refresh</button>
      </div>
      <ul class="list">
        <li v-for="t in transcriptions" :key="t.id ?? t.filename" class="item">
          <button class="link" @click="selected = t">
            {{ t.filename ?? t.id }}
          </button>
          <span class="muted" v-if="t.created_at"> — {{ t.created_at }}</span>
        </li>
      </ul>
    </div>

    <div v-if="error" class="error">
      <strong>Error</strong>
      <pre>{{ error }}</pre>
    </div>

    <div v-if="selected" class="card" style="grid-column: 1 / -1">
      <div class="row">
        <h3>Details</h3>
        <button class="btn" @click="selected = null">Close</button>
      </div>
      <ResultViewer :result="selected" />
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
  justify-content: space-between;
  align-items: center;
}
.btn {
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
}
.list {
  padding-left: 18px;
}
.item {
  margin-bottom: 6px;
}
.link {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
}
.error {
  grid-column: 1 / -1;
  border: 1px solid #fecaca;
  background: #fff1f2;
  padding: 12px;
  border-radius: 12px;
  overflow: auto;
}
.muted {
  color: #6b7280;
}
</style>
