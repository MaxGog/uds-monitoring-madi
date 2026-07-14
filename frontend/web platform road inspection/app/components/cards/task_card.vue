<template>
  <div 
    class="task-card" 
    :class="[
      'status-' + statusClass, 
      { 'is-completed': isCompleted, 'is-overdue': isOverdue }
    ]"
    @click="goToTask"
  >
    <div class="task-checkbox-wrapper" @click.stop>
      <input
        type="checkbox"
        :id="'task-' + task.id"
        :checked="isCompleted"
        :disabled="!isAdmin"
        @change="$emit('toggle', task)"
        class="fluent-checkbox"
      />
      <label :for="'task-' + task.id" class="fluent-checkbox-label" title="Отметить статус"></label>
    </div>

    <div class="task-content">
      <div class="task-header">
        <div class="task-title-group">
          <span class="task-id">#{{ task.id }}</span>
          <h3 class="task-title" :class="{ 'completed-text': isCompleted }">
            {{ task.title }}
          </h3>
        </div>

        <div class="task-badges">
          <span class="fluent-badge status-badge" :class="statusClass">
            {{ statusLabel }}
          </span>
          <span v-if="typeLabel" class="fluent-badge type-badge">
            {{ typeLabel }}
          </span>
        </div>
      </div>

      <p v-if="task.description" class="task-description">
        {{ task.description }}
      </p>

      <div class="task-meta-row">
        <span v-if="objectName" class="meta-item" title="Объект">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
            <path d="M2 2.5A1.5 1.5 0 0 1 3.5 1h9A1.5 1.5 0 0 1 14 2.5v11a.5.5 0 0 1-.707.455L8 11.25l-5.293 2.705A.5.5 0 0 1 2 13.5v-11z"/>
          </svg>
          {{ objectName }}
        </span>

        <span v-if="responsibleDisplay" class="meta-item" title="Ответственные">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
            <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H7zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-5.784 6A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
          </svg>
          {{ responsibleDisplay }}
        </span>

        <span v-if="dueDateDisplay" class="meta-item deadline-item" :class="{ overdue: isOverdue }" title="Срок выполнения">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
            <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
          </svg>
          {{ dueDateDisplay }}
        </span>
      </div>
    </div>

    <div class="task-actions" @click.stop>
      <button 
        class="btn-action btn-edit" 
        title="Редактировать задачу" 
        @click="$emit('edit', task)"
      >
        <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
          <path d="M12.146.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1 0 .708l-9.82 9.82a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l9.82-9.82zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
        </svg>
        <span>Редактировать</span>
      </button>

      <button 
        v-if="isAdmin" 
        class="btn-action btn-delete" 
        title="Удалить задачу" 
        @click="$emit('delete', task.id)"
      >
        <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
          <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
          <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
        </svg>
        <span>Удалить</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    task: any
    isAdmin?: boolean
  }>(),
  {
    isAdmin: false
  }
)

const emit = defineEmits<{
  (e: 'toggle', task: any): void
  (e: 'edit', task: any): void
  (e: 'delete', id: number): void
}>()

// Переход на страницу задачи
const goToTask = () => {
  navigateTo(`/tasks/${props.task.id}`)
}

const isCompleted = computed(() => {
  return props.task.completed || props.task.status === 'completed'
})

const isOverdue = computed(() => {
  if (isCompleted.value) return false
  const dateStr = props.task.dueDate || props.task.due_date
  if (!dateStr) return false
  const due = new Date(dateStr)
  return !isNaN(due.getTime()) && due < new Date()
})

const statusClass = computed(() => {
  if (isCompleted.value) return 'done'
  const status = props.task.status || ''
  if (status === 'in_progress') return 'active'
  if (status === 'pending') return 'warn'
  if (isOverdue.value) return 'danger'
  return 'default'
})

const statusLabel = computed(() => {
  if (isCompleted.value) return 'Завершено'
  const map: Record<string, string> = {
    in_progress: 'В работе',
    pending: 'Ожидает',
    new: 'Новая'
  }
  return map[props.task.status] || props.task.status || 'Новая'
})

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    cmr_check: 'Проверка СМР',
    acts_export: 'Выгрузка актов',
    registry_reconciliation: 'Сверка реестров',
    other: 'Другое'
  }
  return map[props.task.type] || props.task.type || ''
})

const objectName = computed(() => {
  return props.task.objectTitle || props.task.object_name || props.task.object_id || ''
})

const responsibleDisplay = computed(() => {
  if (Array.isArray(props.task.responsibleNames) && props.task.responsibleNames.length > 0) {
    return props.task.responsibleNames.join(', ')
  }
  if (Array.isArray(props.task.responsibles)) {
    return props.task.responsibles.map((r: any) => r.name || r.full_name || r.email || r).join(', ')
  }
  return props.task.responsible || ''
})

const dueDateDisplay = computed(() => {
  return props.task.dueDate || props.task.due_date || ''
})
</script>

<style scoped>
.task-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 6px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  position: relative;
}

.task-card:hover {
  border-color: #0078d4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #fafafa;
}

.task-card.is-completed {
  opacity: 0.75;
  background: #fbfbfb;
}

/* Левая секция с чекбоксом */
.task-checkbox-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.fluent-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #0078d4;
}

/* Центральная часть */
.task-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.task-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.task-id {
  font-size: 12px;
  font-weight: 700;
  color: #0078d4;
  flex-shrink: 0;
}

.task-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #242424;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.completed-text {
  text-decoration: line-through;
  color: #707070;
}

.task-badges {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.fluent-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: capitalize;
}

.status-badge.done { background: #dff6dd; color: #107c41; }
.status-badge.active { background: #deecf9; color: #0078d4; }
.status-badge.warn { background: #fff4ce; color: #797775; }
.status-badge.danger { background: #fde7e9; color: #a80000; }
.status-badge.default { background: #f3f2f1; color: #605e5c; }

.type-badge {
  background: #f3f2f1;
  color: #323130;
}

.task-description {
  margin: 0;
  font-size: 12px;
  color: #605e5c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Метаданные: объект, ответственные, дата */
.task-meta-row {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #605e5c;
  margin-top: 2px;
  flex-wrap: wrap;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.meta-item svg {
  color: #8a8886;
}

.deadline-item.overdue {
  color: #a80000;
  font-weight: 600;
}

.deadline-item.overdue svg {
  color: #a80000;
}

/* Правый блок кнопок действий */
.task-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #d1d1d1;
  background: #ffffff;
  color: #242424;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-action:hover {
  background: #f3f3f3;
  border-color: #c8c8c8;
}

.btn-edit:hover {
  color: #0078d4;
  border-color: #0078d4;
}

.btn-delete:hover {
  color: #a80000;
  border-color: #a80000;
  background: #fde7e9;
}
</style>