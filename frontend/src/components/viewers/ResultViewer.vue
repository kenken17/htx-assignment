<script setup lang="ts">
import { computed } from "vue";
const props = defineProps<{ result: any }>();
const r = computed(() => props.result ?? {});
</script>

<template>
  <div class="viewer">
    <!-- Video-like result -->
    <div v-if="r.summary || r.keyframes || r.objects" class="block">
      <h4>Summary</h4>
      <p v-if="r.summary">{{ r.summary }}</p>
      <p v-else class="muted">No summary field returned.</p>

      <div v-if="r.keyframes" class="block">
        <h4>Keyframes</h4>
        <ul class="list">
          <li v-for="(kf, idx) in r.keyframes" :key="idx">
            <span class="muted">t={{ kf.timestamp ?? kf.time ?? "?" }}</span>
            <span v-if="kf.image_url">
              — <a :href="kf.image_url" target="_blank">image</a></span
            >
          </li>
        </ul>
      </div>

      <div v-if="r.objects" class="block">
        <h4>Detected objects</h4>
        <ul class="list">
          <li v-for="(o, idx) in r.objects" :key="idx">
            <span>{{ o.label ?? o.class ?? "object" }}</span>
            <span class="muted"> @ {{ o.timestamp ?? "?" }}s</span>
            <span class="muted" v-if="o.confidence != null">
              ({{ o.confidence }})</span
            >
          </li>
        </ul>
      </div>
    </div>

    <!-- Audio-like result -->
    <div v-else-if="r.text || r.segments" class="block">
      <h4>Transcription</h4>
      <p v-if="r.text">{{ r.text }}</p>
      <p v-else class="muted">No text field returned.</p>

      <div v-if="r.segments" class="block">
        <h4>Segments</h4>
        <ul class="list">
          <li v-for="(s, idx) in r.segments" :key="idx">
            <span class="muted">[{{ s.start ?? 0 }} - {{ s.end ?? 0 }}]</span>
            <span> {{ s.text ?? "" }}</span>
            <span class="muted" v-if="s.confidence != null">
              (conf: {{ s.confidence }})</span
            >
          </li>
        </ul>
      </div>
    </div>

    <div class="block">
      <h4>Raw</h4>
      <pre>{{ JSON.stringify(r, null, 2) }}</pre>
    </div>
  </div>
</template>

<style scoped>
.viewer {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  background: #f9fafb;
}
.block {
  margin-bottom: 14px;
}
.list {
  padding-left: 18px;
}
pre {
  background: #fff;
  padding: 12px;
  border-radius: 10px;
  overflow: auto;
  border: 1px solid #e5e7eb;
}
.muted {
  color: #6b7280;
}
</style>
