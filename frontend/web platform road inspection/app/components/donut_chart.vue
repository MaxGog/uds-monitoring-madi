<template>
  <div class="donut-chart-card">
    <div class="chart-title">{{ title }}</div>
    <div class="donut-wrap">
      <div
        class="donut"
        :style="{ background: `conic-gradient(${gradientSegments})` }"
      ></div>
      <div class="legend">
        <b>Всего: {{ total }}</b>
        <div
          v-for="(item, index) in legendData"
          :key="index"
          class="legend-item"
        >
          <span
            class="legend-dot"
            :style="{ background: colors[index % colors.length] }"
          ></span>
          {{ item.label }} — {{ item.count }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  items: any[]
  key: string
  colors?: string[]
}>()

const colors = props.colors || ['#6752f5', '#48d6d2', '#34c978', '#ffc247', '#ff5b66', '#8a6cff', '#7d82a0']

const grouped = computed(() => {
  const groups: Record<string, number> = {}
  props.items.forEach(item => {
    const value = String(item[props.key] || 'Не указано')
    groups[value] = (groups[value] || 0) + 1
  })
  return groups
})

const legendData = computed(() => {
  return Object.entries(grouped.value)
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
})

const total = computed(() => props.items.length)

const gradientSegments = computed(() => {
  const totalItems = total.value || 1
  let startDeg = 0
  return legendData.value
    .map((item, idx) => {
      const deg = (item.count / totalItems) * 360
      const endDeg = startDeg + deg
      const segment = `${colors[idx % colors.length]} ${startDeg}deg ${endDeg}deg`
      startDeg = endDeg
      return segment
    })
    .join(', ')
})
</script>

<style scoped>
.donut-chart-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  min-height: 180px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #242424;
  margin-bottom: 12px;
}

.donut-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
}

.donut {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  flex: 0 0 auto;
  position: relative;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.5);
}

.donut::after {
  content: '';
  position: absolute;
  inset: 20px;
  background: #ffffff;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px #e1e3e8;
}

.legend {
  flex: 1;
  font-size: 12px;
  color: #605e5c;
  max-height: 110px;
  overflow-y: auto;
  line-height: 1.4;
}

.legend b {
  display: block;
  color: #242424;
  margin-bottom: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>