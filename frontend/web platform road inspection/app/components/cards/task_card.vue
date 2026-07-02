<template>
  <div class="task-row" :class="{ 'is-completed': task.completed }">
    <div class="task-checkbox-wrapper">
      <input 
        type="checkbox" 
        :id="'task-' + task.id" 
        :checked="task.completed"
        @change="$emit('toggle', task.id)"
        class="fluent-checkbox"
      />
      <label :for="'task-' + task.id" class="fluent-checkbox-label"></label>
    </div>

    <div class="task-info">
      <div class="task-header-row">
        <span class="task-title">{{ task.title }}</span>
        <span class="task-priority" :class="'priority-' + task.priority">
          {{ task.priorityLabel }}
        </span>
      </div>
      
      <p v-if="task.description" class="task-desc">{{ task.description }}</p>
      
      <div class="task-meta">
        <span class="meta-item">📁 {{ task.objectTitle }}</span>
        <span v-if="task.dueDate" class="meta-item">📅 Срок: {{ task.dueDate }}</span>
        <span class="meta-item">👤 Исполнитель: {{ task.assignee }}</span>
      </div>
    </div>

    <div class="task-actions">
      <button class="icon-action-btn" title="Удалить" @click="$emit('delete', task.id)">
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Task {
  id: number
  title: string
  description?: string
  priority: string
  priorityLabel: string
  objectTitle: string
  dueDate?: string
  assignee: string
  scope: string
  completed: boolean
}

defineProps<{
  task: Task
}>()

defineEmits<{
  (e: 'toggle', id: number): void
  (e: 'delete', id: number): void
}>()
</script>

<style scoped>
.task-row {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f3f3;
  transition: background-color 0.15s ease;
  gap: 14px;
}

.task-row:last-child {
  border-bottom: none;
}

.task-row:hover {
  background-color: #fafafa;
}

.task-checkbox-wrapper {
  margin-top: 2px;
  position: relative;
  width: 16px;
  height: 16px;
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
  width: 16px;
  height: 16px;
  border: 1px solid #616161;
  border-radius: 2px;
  background: #ffffff;
  box-sizing: border-box;
}

.fluent-checkbox:hover + .fluent-checkbox-label {
  border-color: #242424;
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
  gap: 2px;
}

.task-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-title {
  font-size: 14px;
  font-weight: 600;
  color: #242424;
}

.task-row.is-completed .task-title {
  text-decoration: line-through;
  color: #a1a1a1;
}

.task-desc {
  font-size: 13px;
  color: #616161;
  margin: 2px 0 4px 0;
  line-height: 1.4;
}

.task-row.is-completed .task-desc {
  color: #c8c8c8;
}

.task-priority {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.priority-high { background: #fde7e9; color: #a80000; }
.priority-medium { background: #fff4ce; color: #a4261d; }
.priority-low { background: #f3f3f3; color: #616161; }

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 11px;
  color: #757575;
  margin-top: 2px;
}

.meta-item {
  display: flex;
  align-items: center;
}

/* Действия */
.task-actions {
  display: flex;
  align-items: center;
}

.icon-action-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  font-size: 13px;
  opacity: 0;
  transition: opacity 0.15s, background-color 0.15s;
}

.task-row:hover .icon-action-btn {
  opacity: 0.6;
}

.icon-action-btn:hover {
  opacity: 1 !important;
  background-color: #f3f3f3;
}
</style>