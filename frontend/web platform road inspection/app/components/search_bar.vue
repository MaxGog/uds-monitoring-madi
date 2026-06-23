<template>
  <div class="search-bar">
    <div class="search-icon">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="7" />
        <line x1="16" y1="16" x2="22" y2="22" />
      </svg>
    </div>
    <input
      type="text"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @keydown.enter="$emit('search')"
      placeholder="Поиск объекта..."
      class="search-input"
    />
    <button v-if="modelValue" class="clear-btn" @click="$emit('update:modelValue', ''); $emit('search')">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
}>()
defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'search'): void
}>()
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid var(--line, #e8ebf5);
  border-radius: 32px;
  padding: 0 16px;
  height: 44px;
  box-shadow: 0 8px 20px rgba(34, 29, 84, 0.06);
  transition: box-shadow 0.2s, border-color 0.2s;
  flex: 1;
  max-width: 540px;
}
.search-bar:focus-within {
  border-color: var(--violet, #6752f5);
  box-shadow: 0 8px 24px rgba(103, 82, 245, 0.15), 0 0 0 4px rgba(103, 82, 245, 0.08);
}
.search-icon {
  color: var(--muted, #737895);
  flex-shrink: 0;
  display: flex;
  align-items: center;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--text, #14133b);
  outline: none;
}
.search-input::placeholder {
  color: var(--muted, #737895);
  font-weight: 400;
}
.clear-btn {
  background: none;
  border: none;
  color: var(--muted, #737895);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.clear-btn:hover {
  background: rgba(103, 82, 245, 0.08);
  color: var(--violet, #6752f5);
}
</style>