<template>
  <div class="task-row" :class="['status-' + statusClass, { 'is-completed': task.completed }]">
    <div class="task-checkbox-wrapper">
      <input
        type="checkbox"
        :id="'task-' + task.id"
        :checked="task.completed"
        :disabled="!isAdmin"
        @change="$emit('toggle', task.id)"
        class="fluent-checkbox"
      />
      <label :for="'task-' + task.id" class="fluent-checkbox-label"></label>
    </div>

    <div class="task-info">
      <div class="task-header-row">
        <span class="task-title">{{ task.title }}</span>
        <div class="task-pill-group">
          <span class="task-status-pill" :class="statusClass">{{ task.status }}</span>
          <span class="task-type-pill">{{ task.type }}</span>
        </div>
      </div>

      <p v-if="task.description" class="task-desc">{{ task.description }}</p>

      <div class="task-meta">
        <span class="meta-item">📁 {{ task.objectTitle }}</span>
        <span v-if="task.dueDate" class="meta-item">📅 {{ task.dueDate }}</span>
        <span class="meta-item">👤 {{ task.responsibleNames.join(', ') }}</span>
      </div>
    </div>

    <div class="task-actions">
      <button
        v-if="isAdmin"
        class="icon-action-btn"
        title="Удалить"
        @click="$emit('delete', task.id)"
      >
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Task {
  id: number
  title: string
  description?: string
  priority: string
  priorityLabel: string
  objectTitle: string
  dueDate?: string
  assignee: string
  responsibleNames: string[]
  type: string
  status: string
  scope: string
  completed: boolean
  createdAt: string
  authorName: string
}

const props = defineProps<{
  task: Task
  isAdmin: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle', id: number): void
  (e: 'delete', id: number): void
}>()

const statusClass = computed(() => {
  if (props.task.status === 'Просрочена') return 'danger'
  if (props.task.status === 'Скоро дедлайн') return 'warn'
  if (props.task.status === 'Выполнена') return 'done'
  return 'active'
})
</script>

<style scoped>
.task-row {
  display: flex;
  align-items: flex-start;
  padding: 16px 18px;
  border-bottom: 1px solid #f3f3f3;
  transition: background-color 0.15s ease;
  gap: 14px;
}

.task-row:last-child {
  border-bottom: none;
}

.task-row:hover {
  background-color: #fafbff;
}

.task-checkbox-wrapper {
  margin-top: 2px;
  position: relative;
  width: 18px;
  height: 18px;
}

.fluent-checkbox {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
  z-index: 2;
  margin: 0;
}

.fluent-checkbox-label {
  position: absolute;
  top: 0;
  left: 0;
  width: 18px;
  height: 18px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  box-sizing: border-box;
}

.fluent-checkbox:hover + .fluent-checkbox-label {
  border-color: #0078d4;
}

.fluent-checkbox:checked + .fluent-checkbox-label {
  background-color: #0078d4;
  border-color: #0078d4;
}

.fluent-checkbox:checked + .fluent-checkbox-label::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.task-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.task-title {
  font-size: 15px;
  font-weight: 700;
  color: #121212;
}

.task-pill-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.task-status-pill,
.task-type-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 999px;
  text-transform: uppercase;
}

.task-status-pill.active {
  background: #e8f0fe;
  color: #0f62fe;
}

.task-status-pill.warn {
  background: #fff4ce;
  color: #a35400;
}

.task-status-pill.danger {
  background: #ffe7e5;
  color: #a4261d;
}

.task-status-pill.done {
  background: #e6f4ea;
  color: #107c41;
}

.task-type-pill {
  background: #f3f6ff;
  color: #1f3f8b;
}

.task-desc {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.5;
}

.task-row.is-completed .task-title {
  text-decoration: line-through;
  color: #8b8b8b;
}

.task-row.is-completed .task-desc {
  color: #9ca3af;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.task-actions {
  display: flex;
  align-items: center;
}

.icon-action-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.15s, background-color 0.15s;
}

.task-row:hover .icon-action-btn {
  opacity: 0.7;
}

.icon-action-btn:hover {
  background-color: #f3f4f6;
}
</style>
