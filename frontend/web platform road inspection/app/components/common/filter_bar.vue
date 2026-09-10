<template>
  <div class="filter-bar">
    <slot />
  </div>
</template>

<script setup lang="ts" />

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  background: #ffffff;
  padding: 14px 20px;
  border: 1px solid #e1e3e8;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
</style>
