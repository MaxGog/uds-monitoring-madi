<template>
  <div class="summary-card">
    <div class="summary-header">
      <p class="summary-title">{{ title }}</p>
      <span class="summary-value">{{ value }}</span>
    </div>
    <p v-if="description" class="summary-description">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  title: String,
  value: [String, Number],
  description: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: '#0078d4'
  }
})
</script>

<style scoped>
.summary-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 14px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 210px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
}

.summary-title {
  font-size: 13px;
  color: #616161;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  margin: 0;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--summary-color, #0078d4);
}

.summary-description {
  margin: 0;
  color: #6b6b6b;
  font-size: 13px;
}
</style>