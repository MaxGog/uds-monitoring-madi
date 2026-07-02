<template>
  <div class="user-avatar" :title="fullName">
    <div class="avatar-circle" :style="{ background: color }">
      {{ initials }}
    </div>
    <span class="user-name" v-if="showName">{{ fullName }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  fullName?: string
  email?: string
  showName?: boolean
}>()

const initials = computed(() => {
  const name = props.fullName || props.email || 'U'
  return name.split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase()
})

const color = computed(() => {
  const hash = (props.email || 'user').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const hue = hash % 360
  return `hsl(${hue}, 70%, 60%)`
})
</script>

<style scoped>
.user-avatar {
    display: flex;
    align-items: center;
    gap: 10px;
}

.avatar-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 700;
    font-size: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}

.avatar-circle:hover {
    transform: scale(1.05);
}

.user-name {
    font-weight: 600;
    color: var(--text, #14133b);
}
</style>