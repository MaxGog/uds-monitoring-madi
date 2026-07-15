<template>
  <div class="task-page">
    <PageToolbar
      :title="isEdit ? 'Редактирование задачи' : 'Создание задачи'"
      subtitle="Заполните информацию о задаче"
    >
      <template #actions>
        <button class="fluent-button button-secondary" @click="goBack">
          Отмена
        </button>
        <button
          class="fluent-button button-primary"
          :disabled="isSubmitting || isLoading"
          @click="handleSubmit"
        >
          {{ isSubmitting ? 'Сохранение...' : isEdit ? 'Сохранить изменения' : 'Создать задачу' }}
        </button>
      </template>
    </PageToolbar>

    <div v-if="isLoading && !isSubmitting" class="loading-card">
      Загрузка данных задачи...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="form-layout">
      <div v-if="error" class="error-banner">
        ⚠️ {{ error }}
      </div>

      <div class="form-section">
        <h3 class="section-title">Основные параметры</h3>
        <FormControls>
          <div class="form-group full-width">
            <label for="task-title">Название задачи *</label>
            <input
              id="task-title"
              v-model="form.title"
              type="text"
              required
              class="fluent-input"
              placeholder="Например: Проверка КС-2 по объекту"
            />
          </div>

          <div class="form-group full-width">
            <label for="task-desc">Описание</label>
            <textarea
              id="task-desc"
              v-model="form.description"
              class="fluent-textarea"
              rows="4"
              placeholder="Подробное описание задачи..."
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="task-status">Статус *</label>
              <select id="task-status" v-model="form.status" class="fluent-select" required>
                <option v-for="(label, value) in statusOptions" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="task-priority">Приоритет *</label>
              <select id="task-priority" v-model="form.priority" class="fluent-select" required>
                <option v-for="(label, value) in priorityOptions" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <label for="task-performers">Исполнители</label>
            <select
              id="task-performers"
              v-model="form.performer_ids"
              class="fluent-select"
              multiple
              style="height: 100px;"
            >
              <option v-for="u in usersList" :key="u.id" :value="u.id">
                {{ u.full_name || u.username || u.email }}
              </option>
            </select>
            <span class="field-hint">Зажмите Ctrl (или Cmd), чтобы выбрать нескольких</span>
          </div>
        </FormControls>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTasks } from '~/composables/useTasks'
import { apiFetch } from '~/composables/useAPI'
import { TaskStatus, TaskPriority } from '~/types/enums'
import type { TaskCreate } from '~/types/task'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FormControls from '~/components/common/form_controls.vue'

const route = useRoute()
const router = useRouter()

const taskId = computed(() => route.params.id as string)
const isEdit = computed(() => taskId.value !== 'new' && !!taskId.value)

const { createTask, updateTask, fetchTask, isLoading, error } = useTasks()

const isSubmitting = ref(false)
const usersList = ref<any[]>([])

const statusOptions = {
  [TaskStatus.PENDING]: 'В ожидании',
  [TaskStatus.IN_PROGRESS]: 'В работе',
  [TaskStatus.COMPLETED]: 'Завершена',
  [TaskStatus.PAUSED]: 'Приостановлена',
  [TaskStatus.CANCELLED]: 'Отменена',
  [TaskStatus.EXPIRED]: 'Просрочена',
  [TaskStatus.FAILED]: 'Провалена'
}

const priorityOptions = {
  [TaskPriority.LOW]: 'Низкий',
  [TaskPriority.MEDIUM]: 'Средний',
  [TaskPriority.HIGH]: 'Высокий',
  [TaskPriority.CRITICAL]: 'Критический'
}

const form = reactive({
  title: '',
  description: '',
  status: TaskStatus.PENDING,
  priority: TaskPriority.MEDIUM,
  performer_ids: [] as string[]
})

const loadUsers = async () => {
  try {
    const res = await apiFetch<any>('/users/')
    if (res?.data) {
      usersList.value = res.data
    }
  } catch (e) {
    console.error('Ошибка загрузки пользователей:', e)
  }
}

const loadTaskData = async () => {
  if (!isEdit.value) return
  const numericId = Number(taskId.value)
  const task = await fetchTask(numericId)
  if (task) {
    form.title = task.title || ''
    form.description = task.description || ''
    form.status = task.status || TaskStatus.PENDING
    form.priority = task.priority || TaskPriority.MEDIUM
    form.performer_ids = task.performer_ids || []
  }
}

const goBack = () => router.push('/tasks')

const handleSubmit = async () => {
  if (!form.title.trim()) {
    alert('Название задачи обязательно')
    return
  }

  isSubmitting.value = true
  const payload: TaskCreate = {
    title: form.title,
    description: form.description || null,
    status: form.status,
    priority: form.priority,
    performer_ids: form.performer_ids
  }

  try {
    let result = null
    if (isEdit.value) {
      result = await updateTask(Number(taskId.value), payload)
    } else {
      result = await createTask(payload)
    }
    if (result) goBack()
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  await loadUsers()
  await loadTaskData()
})
</script>

<style scoped>
.task-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 24px;
}

.loading-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  color: #605e5c;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 15px;
  font-weight: 600;
  color: #242424;
  border-bottom: 1px solid #f3f2f1;
  padding-bottom: 8px;
}

.fluent-button {
  padding: 6px 18px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.1s, border-color 0.1s;
}
.button-secondary {
  background: #ffffff;
  border: 1px solid #d2d0ce;
  color: #323130;
}
.button-secondary:hover {
  background: #f3f2f1;
}
.button-primary {
  background: #0078d4;
  border: 1px solid #0078d4;
  color: #ffffff;
}
.button-primary:hover {
  background: #106ebe;
  border-color: #106ebe;
}
.button-primary:disabled {
  background: #f3f2f1;
  color: #a19f9d;
  border-color: #f3f2f1;
  cursor: not-allowed;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group.full-width {
  grid-column: span 2;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #323130;
}

.fluent-input,
.fluent-select,
.fluent-textarea {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  font-family: inherit;
  background: #ffffff;
  color: #242424;
  transition: border-color 0.15s;
  box-sizing: border-box;
  width: 100%;
}
.fluent-input:focus,
.fluent-select:focus,
.fluent-textarea:focus {
  border-color: #0078d4;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
}

.field-hint {
  font-size: 11px;
  color: #797775;
  margin-top: 2px;
}

.error-banner {
  background: #fde7e9;
  border: 1px solid #fccfd2;
  color: #a80000;
  padding: 10px 14px;
  border-radius: 4px;
  font-size: 13px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>