<template>
  <div class="roadmap-card">
    <div class="roadmap-header">
      <p class="roadmap-title">{{ item.title }}</p>
      <span class="roadmap-risk">{{ item.risk }}</span>
    </div>

    <div class="roadmap-info">
      <span>{{ item.region }}</span>
      <span>{{ item.startDate }} – {{ item.endDate }}</span>
    </div>

    <p class="roadmap-phase">Фаза: {{ item.phase }}</p>
  </div>
</template>

<script setup lang="ts">
import type { MockRoadmapItem } from '~/composables/useMockData'

const props = defineProps<{ item: MockRoadmapItem }>()
</script>

<style scoped>
.roadmap-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 16px;
  padding: 20px;
  display: grid;
  gap: 12px;
}

.roadmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.roadmap-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #242424;
}

.roadmap-risk {
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #fef7f0;
  color: #a35400;
  font-weight: 700;
}

.roadmap-info {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #616161;
}

.roadmap-phase {
  margin: 0;
  color: #616161;
  font-size: 13px;
}
</style>