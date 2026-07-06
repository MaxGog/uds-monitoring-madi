<template>
  <div class="form-controls">
    <slot />
  </div>
</template>

<script setup lang="ts" />

<style scoped>
.form-controls {
  display: grid;
  gap: 12px;
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.fluent-input,
.fluent-select,
.fluent-textarea {
  width: 100%;
  border: 1px solid #d6d9dc;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  color: #242424;
  background: #ffffff;
  outline: none;
}

.fluent-input:focus,
.fluent-select:focus,
.fluent-textarea:focus {
  border-color: #0078d4;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.08);
}

.fluent-textarea {
  min-height: 100px;
  resize: vertical;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  color: #4b5563;
  font-weight: 600;
}
</style>
