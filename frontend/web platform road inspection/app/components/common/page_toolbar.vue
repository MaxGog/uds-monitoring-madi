<template>
  <div class="page-toolbar">
    <div class="toolbar-left">
      <div class="title-block">
        <h2 class="page-title">{{ title }}</h2>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
      </div>
      <p v-if="countText" class="toolbar-count">{{ countText }}</p>
    </div>

    <div class="toolbar-right">
      <div v-if="tabs?.length" class="fluent-pivot">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="pivot-item"
          :class="{ active: activeTab === tab.value }"
          type="button"
          @click="updateTab(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="toolbar-actions">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  subtitle?: string
  countText?: string
  tabs?: Array<{ label: string; value: string }>
  activeTab?: string
}>()

const emit = defineEmits<{
  (event: 'update:activeTab', value: string): void
}>()

const updateTab = (value: string) => {
  emit('update:activeTab', value)
}
</script>

<style scoped>
.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  background: #ffffff;
  padding: 18px 22px;
  border-radius: 10px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 240px;
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: #616161;
}

.toolbar-count {
  font-size: 13px;
  color: #616161;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.fluent-pivot {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pivot-item {
  background: none;
  border: none;
  padding: 8px 14px;
  font-size: 13px;
  color: #616161;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.pivot-item:hover {
  background: #f3f4f3;
  color: #111827;
}

.pivot-item.active {
  background: #0078d4;
  color: #ffffff;
}
</style>
