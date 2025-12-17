<script setup lang="ts">
import { computed, ref } from "vue";
import UploadPanel from "./components/UploadPanel.vue";
import HistoryPanel from "./components/HistoryPanel.vue";
import SearchPanel from "./components/SearchPanel.vue";

type Tab = "upload" | "history" | "search";
const tab = ref<Tab>("upload");

const title = computed(() => {
  if (tab.value === "upload") return "Upload & Process";
  if (tab.value === "history") return "Processed Media";
  return "Unified Search";
});
</script>

<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>Multimedia Processing</h1>
        <p class="muted">API client (Vue 3 SPA)</p>
      </div>
      <nav class="tabs">
        <button :class="{ active: tab === 'upload' }" @click="tab = 'upload'">
          Upload
        </button>
        <button :class="{ active: tab === 'history' }" @click="tab = 'history'">
          History
        </button>
        <button :class="{ active: tab === 'search' }" @click="tab = 'search'">
          Search
        </button>
      </nav>
    </header>

    <main class="content">
      <h2>{{ title }}</h2>

      <UploadPanel v-if="tab === 'upload'" />
      <HistoryPanel v-else-if="tab === 'history'" />
      <SearchPanel v-else />
    </main>
  </div>
</template>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
  font-family:
    ui-sans-serif,
    system-ui,
    -apple-system,
    Segoe UI,
    Roboto,
    Helvetica,
    Arial;
}
.header {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}
.tabs {
  display: flex;
  gap: 8px;
}
.tabs button {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
}
.tabs button.active {
  border-color: #111827;
}
.content {
  padding-top: 18px;
}
.footer {
  margin-top: 28px;
  padding-top: 14px;
  border-top: 1px solid #e5e7eb;
}
.muted {
  color: #6b7280;
}
code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 6px;
}
</style>
