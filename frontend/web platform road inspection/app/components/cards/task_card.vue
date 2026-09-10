<template>
  <div class="task-card" @click="goToTask">
    <div class="task-checkbox" @click.stop>
      <input
        type="checkbox"
        :checked="isCompleted"
        :disabled="!isAdmin"
        @change="$emit('toggle', task)"
      />
    </div>

    <div class="task-content">
      <div class="task-header">
        <span class="task-id">#{{ task.id }}</span>
        <h3 class="task-title" :class="{ completed: isCompleted }">{{ task.title }}</h3>
        <div class="task-badges">
          <span class="badge status" :class="statusClass">{{ statusLabel }}</span>
          <span class="badge priority" :class="priorityClass">{{ priorityLabel }}</span>
        </div>
      </div>
      <p v-if="task.description" class="task-description">{{ task.description }}</p>
      <div class="task-meta">
        <span v-if="performerCount" class="meta-item">
          👤 {{ performerCount }} исполнитель{{ performerCount > 1 ? 'я' : '' }}
        </span>
        <span v-if="task.created_at" class="meta-item">
          🗓️ {{ formatDate(task.created_at) }}
        </span>
      </div>
    </div>

    <div class="task-actions" @click.stop>
      <button class="btn-action" @click="$emit('edit', task)">✎</button>
      <button v-if="isAdmin" class="btn-action danger" @click="$emit('delete', task.id)">✕</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TaskStatus, TaskPriority } from '~/types/enums'

const props = defineProps<{
  task: any
  isAdmin?: boolean
}>()

const emit = defineEmits(['toggle', 'edit', 'delete'])

const goToTask = () => navigateTo(`/tasks/${props.task.id}`)

const isCompleted = computed(() => props.task.status === TaskStatus.COMPLETED)
const performerCount = computed(() => (props.task.performer_ids || []).length)

const statusClass = computed(() => {
  const status = props.task.status as TaskStatus
  switch (status) {
    case TaskStatus.COMPLETED: return 'done'
    case TaskStatus.IN_PROGRESS: return 'active'
    case TaskStatus.PENDING: return 'warn'
    case TaskStatus.PAUSED: return 'paused'
    case TaskStatus.CANCELLED:
    case TaskStatus.EXPIRED:
    case TaskStatus.FAILED: return 'danger'
    default: return 'default'
  }
})

const statusLabel = computed(() => {
  const map: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: 'Ожидает',
    [TaskStatus.IN_PROGRESS]: 'В работе',
    [TaskStatus.COMPLETED]: 'Завершена',
    [TaskStatus.PAUSED]: 'Приостановлена',
    [TaskStatus.CANCELLED]: 'Отменена',
    [TaskStatus.EXPIRED]: 'Просрочена',
    [TaskStatus.FAILED]: 'Провалена',
    [TaskStatus.ACCEPTED]: 'Принято'
  }
  return map[props.task.status as TaskStatus] || props.task.status
})

const priorityClass = computed(() => {
  const priority = props.task.priority as TaskPriority
  switch (priority) {
    case TaskPriority.LOW: return 'low'
    case TaskPriority.MEDIUM: return 'medium'
    case TaskPriority.HIGH: return 'high'
    case TaskPriority.CRITICAL: return 'critical'
    default: return ''
  }
})

const priorityLabel = computed(() => {
  const map: Record<TaskPriority, string> = {
    [TaskPriority.LOW]: 'Низкий',
    [TaskPriority.MEDIUM]: 'Средний',
    [TaskPriority.HIGH]: 'Высокий',
    [TaskPriority.CRITICAL]: 'Критический'
  }
  return map[props.task.priority as TaskPriority] || props.task.priority
})

const formatDate = (date: string) => new Date(date).toLocaleDateString('ru-RU')
</script>

<style scoped>
.task-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #e1e3e8;
  border-radius: 6px;
  background: #fff;
  transition: 0.15s;
  cursor: pointer;
}
.task-card:hover {
  border-color: #0078d4;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.task-checkbox {
  flex-shrink: 0;
}
.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.task-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.task-id {
  font-weight: 700;
  color: #0078d4;
  font-size: 12px;
}
.task-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #242424;
}
.task-title.completed {
  text-decoration: line-through;
  color: #888;
}
.task-badges {
  display: flex;
  gap: 6px;
  margin-left: auto;
}
.badge {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
}
.badge.status.done { background: #dff6dd; color: #107c41; }
.badge.status.active { background: #deecf9; color: #0078d4; }
.badge.status.warn { background: #fff4ce; color: #797775; }
.badge.status.paused { background: #fef6e6; color: #b25a00; }
.badge.status.danger { background: #fde7e9; color: #a80000; }
.badge.status.default { background: #f3f2f1; color: #605e5c; }

.badge.priority.low { background: #e1e3e8; color: #605e5c; }
.badge.priority.medium { background: #f3f2f1; color: #323130; }
.badge.priority.high { background: #fedfce; color: #b25a00; }
.badge.priority.critical { background: #fde7e9; color: #a80000; }

.task-description {
  margin: 0;
  font-size: 12px;
  color: #605e5c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.task-meta {
  font-size: 12px;
  color: #797775;
  display: flex;
  gap: 16px;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.task-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.btn-action {
  background: transparent;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #605e5c;
  transition: 0.15s;
}
.btn-action:hover {
  background: #f3f2f1;
}
.btn-action.danger:hover {
  background: #fde7e9;
  color: #a80000;
}
</style>