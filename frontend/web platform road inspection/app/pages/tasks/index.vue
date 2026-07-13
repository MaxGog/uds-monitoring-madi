<template>
  <div class="tasks-page">
    <PageToolbar
      title="Управление задачами"
      :countText="`Задач: ${tasks.length}`"
      :tabs="filters"
      :activeTab="currentFilter"
      @update:activeTab="(value: string) => currentFilter = value"
    >
      <template #actions>
        <button class="btn-primary" @click="openCreateModal">
          <span class="btn-icon">＋</span> Создать задачу
        </button>
      </template>
    </PageToolbar>

    <div v-if="isLoading && tasks.length === 0" class="loading-card">
      Загрузка списка задач...
    </div>

    <div v-else-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="fetchTasks" class="btn-retry">Повторить</button>
    </div>

    <div v-else class="tasks-container">
      <div v-if="filteredTasks.length > 0" class="tasks-list">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          :is-admin="isAdmin"
          @toggle="handleToggleTask"
          @edit="openEditModal(task)"
          @delete="handleDeleteTask"
        />
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>Нет задач</h3>
        <p>В этом фильтре сейчас нет подходящих задач.</p>
      </div>
    </div>

    <TaskModal
      v-if="isModalOpen"
      :task-to-edit="selectedTask"
      @close="closeModal"
      @save="handleSaveTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTasks } from '~/composables/useTasks'
import { TaskStatus, type Task, type TaskCreate, type TaskUpdate } from '~/types/task'
import TaskModal from '~/components/task_modal.vue'

const { tasks, isLoading, error, fetchTasks, createTask, updateTask, deleteTask } = useTasks()

const isAdmin = ref(true)
const currentFilter = ref('all')
const isModalOpen = ref(false)
const selectedTask = ref<Task | null>(null)

const filters = [
  { id: 'all', label: 'Все' },
  { id: 'pending', label: 'В ожидании' },
  { id: 'in_progress', label: 'В работе' },
  { id: 'completed', label: 'Завершенные' },
]

onMounted(() => {
  fetchTasks()
})

const filteredTasks = computed(() => {
  if (currentFilter.value === 'all') return tasks.value
  return tasks.value.filter(t => t.status === currentFilter.value)
})

const openCreateModal = () => {
  selectedTask.value = null
  isModalOpen.value = true
}

const openEditModal = (task: Task) => {
  selectedTask.value = task
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedTask.value = null
}

const handleSaveTask = async (payload: TaskCreate | TaskUpdate) => {
  if (selectedTask.value) {
    await updateTask(selectedTask.value.id, payload as TaskUpdate)
  } else {
    await createTask(payload as TaskCreate)
  }
  closeModal()
}

const handleToggleTask = async (task: Task) => {
  const newStatus = task.status === TaskStatus.COMPLETED 
    ? TaskStatus.IN_PROGRESS 
    : TaskStatus.COMPLETED

  await updateTask(task.id, { status: newStatus })
}

const handleDeleteTask = async (id: number) => {
  if (confirm('Вы действительно хотите удалить эту задачу?')) {
    await deleteTask(id)
  }
}
</script>

<style scoped>
.tasks-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.btn-primary {
  background-color: #0078d4;
  color: white;
  border: none;
  height: 32px;
  padding: 0 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-primary:hover { background-color: #106ebe; }

.tasks-container {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.loading-card, .empty-state {
  text-align: center;
  padding: 40px;
  color: #605e5c;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.error-banner {
  background: #fde7e9;
  color: #a80000;
  padding: 12px 16px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-retry {
  background: #ffffff;
  border: 1px solid #a80000;
  color: #a80000;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
}
</style>