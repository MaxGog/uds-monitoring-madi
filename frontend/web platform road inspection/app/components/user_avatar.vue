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