<template>
  <div class="status-card">
    <div class="status-header">
      <p class="status-title">{{ status.objectName }}</p>
      <span class="status-badge">{{ status.stage }}</span>
    </div>

    <div class="status-row">
      <p class="info-label">Прогресс</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressValue + '%' }" />
      </div>
      <span class="progress-value">{{ status.progress }}</span>
    </div>

    <div class="status-grid">
      <div>
        <p class="info-label">Менеджер</p>
        <p class="info-value">{{ status.manager }}</p>
      </div>
      <div>
        <p class="info-label">Обновлено</p>
        <p class="info-value">{{ status.updatedAt }}</p>
      </div>
    </div>

    <p class="status-next">Следующее: {{ status.nextAction }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MockWorkStatus } from '~/composables/useMockData'

const props = defineProps<{ status: MockWorkStatus }>()

const progressValue = computed(() => {
  const parsed = Number(props.status.progress.replace('%', ''))
  return Number.isFinite(parsed) ? parsed : 0
})
</script>

<style scoped>
.status-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 18px;
  padding: 20px;
  display: grid;
  gap: 16px;
  min-height: 220px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.status-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}

.status-badge {
  background: #eef4ff;
  color: #005a9e;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-row {
  display: grid;
  gap: 8px;
}

.info-label {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.progress-bar {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: #f3f4f6;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0078d4 0%, #60a5fa 100%);
}

.progress-value {
  font-size: 12px;
  color: #475569;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.info-value {
  margin: 4px 0 0;
  font-size: 13px;
  color: #111827;
  font-weight: 600;
}

.status-next {
  margin: 0;
  font-size: 13px;
  color: #475569;
}

@media (max-width: 780px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
