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
        <button v-if="isAdmin" class="btn-primary" @click="openCreateModal">
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

      <EmptyState
        v-else
        icon="📋"
        title="Нет задач"
        description="В выбранном фильтре пока нет задач."
        :button-text="isAdmin ? 'Создать задачу' : undefined"
        @action="openCreateModal"
      />
    </div>

    <TaskModal
      v-if="isModalOpen"
      :is-open="isModalOpen"
      :task="selectedTask"
      @close="closeModal"
      @save="handleSaveTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import TaskCard from '~/components/cards/task_card.vue'
import TaskModal from '~/components/task_modal.vue'
import { useTasks } from '~/composables/useTasks'
import { useAuth } from '~/composables/useAuth'
import { useUserProfile } from '~/composables/useUserProfile'

const { isAdmin } = useUserProfile()
const { tasks, isLoading, error, fetchTasks, updateTask, deleteTask } = useTasks()
const { user } = useAuth()


const currentFilter = ref('all')
const filters = [
  { label: 'Все задачи', value: 'all' },
  { label: 'В работе', value: 'in_progress' },
  { label: 'Завершенные', value: 'completed' }
]

const filteredTasks = computed(() => {
  if (currentFilter.value === 'all') return tasks.value
  return tasks.value.filter(task => task.status === currentFilter.value)
})

const isModalOpen = ref(false)
const selectedTask = ref<any>(null)

const openCreateModal = () => {
  if (!isAdmin.value) return
  selectedTask.value = null
  isModalOpen.value = true
}

const openEditModal = (task: any) => {
  selectedTask.value = task
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedTask.value = null
}

const handleSaveTask = async () => {
  await fetchTasks()
  closeModal()
}

const handleToggleTask = async (task: any) => {
  const newStatus = task.status === 'completed' ? 'in_progress' : 'completed'
  await updateTask(task.id, { status: newStatus })
}

const handleDeleteTask = async (id: number) => {
  if (confirm('Вы действительно хотите удалить эту задачу?')) {
    await deleteTask(id)
  }
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.tasks-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tasks-container {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 16px;
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

.btn-primary:hover {
  background-color: #106ebe;
}
</style>