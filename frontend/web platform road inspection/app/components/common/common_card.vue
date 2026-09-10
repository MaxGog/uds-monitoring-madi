<template>
  <section class="common-card">
    <header v-if="title" class="common-card-header">
      <div>
        <p class="common-card-title">{{ title }}</p>
        <p v-if="subtitle" class="common-card-subtitle">{{ subtitle }}</p>
      </div>
      <slot name="action" />
    </header>

    <div class="common-card-body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.common-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}

.common-card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.common-card-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.common-card-subtitle {
  margin: 6px 0 0;
  color: #616161;
  font-size: 13px;
}

.common-card-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>