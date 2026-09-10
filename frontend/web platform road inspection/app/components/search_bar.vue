<template>
  <div class="search-bar">
    <div class="search-icon">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="11" cy="11" r="7" />
        <line x1="16" y1="16" x2="22" y2="22" />
      </svg>
    </div>
    <input
      type="text"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @keydown.enter="$emit('search')"
      placeholder="Введите название объекта для поиска..."
      class="search-input"
    />
    <button v-if="modelValue" class="clear-btn" @click="$emit('update:modelValue', ''); $emit('search')">
      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: string
  placeholder?: string
  clearable?: boolean
}>(), {
  placeholder: 'Поиск...📍',
  clearable: true
})

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'search'): void
}>()
</script>

<style scoped>
.search-bar {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
}

.search-input {
    width: 100%;
    height: 32px; /* Чуть компактнее в стиле Fluent */
    padding: 0 32px 0 36px;
    font-size: 13px;
    color: var(--fluent-gray-100);
    background-color: #f3f3f3; /* Изначально слегка сероватый как на скрине */
    border: 1px solid transparent;
    border-bottom: 1px solid #616161; /* Эффект подчеркивания Fluent */
    border-radius: 4px;
    transition: all 0.15s ease-in-out;
}

.search-input:hover {
    background-color: #eaeaea;
}

.search-input:focus {
    outline: none;
    background-color: #ffffff;
    border: 1px solid var(--fluent-blue);
    border-bottom: 2px solid var(--fluent-blue);
    box-shadow: none;
}

.search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    color: #616161;
    pointer-events: none;
}

.clear-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
    cursor: pointer;
    color: #616161;
    display: flex;
    align-items: center;
}

.clear-btn:hover {
    background-color: rgba(0, 0, 0, 0.06);
    color: #000000;
}
</style>