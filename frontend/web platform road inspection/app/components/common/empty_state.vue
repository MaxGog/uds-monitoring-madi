<template>
  <div class="empty-state">
    <div class="empty-icon" v-if="icon">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <button v-if="buttonText" class="empty-action" @click="$emit('action')">{{ buttonText }}</button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  description: string
  icon?: string
  buttonText?: string
}>()

const emit = defineEmits<{
  (event: 'action'): void
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 32px;
  background: #ffffff;
  border: 1px dashed #d7dce3;
  border-radius: 14px;
  text-align: center;
  color: #4b5563;
}

.empty-icon {
  font-size: 40px;
}

.empty-state h3 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.empty-state p {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
}

.empty-action {
  border: none;
  background: #0078d4;
  color: #ffffff;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.empty-action:hover {
  background: #106ebe;
}
</style>
