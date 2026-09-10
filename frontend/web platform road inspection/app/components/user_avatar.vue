<template>
  <div class="user-avatar-container" :title="fullName || email">
    <div class="avatar-circle" :style="{ background: color }">
      {{ initials }}
    </div>

    <div class="user-info-block">
      <span class="info-name">{{ fullName || 'Пользователь' }}</span>
      <span v-if="email" class="info-email">{{ email }}</span>
      <span v-if="id" class="info-id">ID: {{ id }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  fullName?: string
  email?: string
  id?: string | number
}>()

const initials = computed(() => {
  const name = props.fullName || props.email || 'U'
  return name
    .trim()
    .split(/\s+/)
    .map(w => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
})

const color = computed(() => {
  const hash = (props.email || 'user')
    .split('')
    .reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const hue = hash % 360
  return `hsl(${hue}, 65%, 50%)`
})
</script>

<style scoped>
.user-avatar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-circle {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 700;
  font-size: 15px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.user-info-block {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  line-height: 1.2;
  text-align: left;
}

.info-name {
  font-size: 14px;
  font-weight: 600;
  color: #242424;
}

.info-email {
  font-size: 12px;
  color: #616161;
}

.info-id {
  font-size: 11px;
  color: #8a8a8a;
  font-family: monospace;
}
</style>