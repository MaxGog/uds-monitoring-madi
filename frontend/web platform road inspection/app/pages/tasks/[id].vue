<template>
  <div class="page">
    <div class="toolbar">
      <div class="toolbar-left">
        <NuxtLink to="/tasks" class="btn-back" title="Назад к списку задач">
          <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
            <path fill-rule="evenodd" d="M15 8a.75.75 0 0 1-.75.75H4.31l3.72 3.72a.75.75 0 1 1-1.06 1.06l-5-5a.75.75 0 0 1 0-1.06l5-5a.75.75 0 0 1 1.06 1.06L4.31 7.25H14.25A.75.75 0 0 1 15 8z"/>
          </svg>
          <span>К списку задач</span>
        </NuxtLink>
        <h2 class="page-title">
          {{ isEdit ? 'Редактирование задачи' : 'Создание задачи' }}
        </h2>
      </div>
    </div>

    <div v-if="isLoading && !isSubmitting" class="form-card shimmer-loader">
      Загрузка данных задачи...
    </div>

    <div v-else class="form-card">
      <form @submit.prevent="handleSubmit" class="fluent-form">
        
        <div v-if="error" class="error-banner" role="alert">
          {{ error }}
        </div>

        <div class="form-grid">
          <div class="form-group full-width">
            <label class="form-label">Название задачи <span class="required">*</span></label>
            <input
              v-model="form.title"
              type="text"
              class="fluent-input"
              placeholder="Например: Проверка КС-2 по объекту..."
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Тип задачи <span class="required">*</span></label>
            <select v-model="form.type" class="fluent-select" required>
              <option :value="TaskType.CMR_CHECK">Проверка СМР</option>
              <option :value="TaskType.ACTS_EXPORT">Выгрузка актов</option>
              <option :value="TaskType.REGISTRY_RECONCILIATION">Сверка реестров</option>
              <option :value="TaskType.OTHER">Другое</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Статус задачи</label>
            <select v-model="form.status" class="fluent-select">
              <option :value="TaskStatus.NEW">Новая</option>
              <option :value="TaskStatus.IN_PROGRESS">В работе</option>
              <option :value="TaskStatus.PENDING">На проверке</option>
              <option :value="TaskStatus.COMPLETED">Завершена</option>
            </select>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Описание задачи</label>
            <textarea
              v-model="form.description"
              class="fluent-textarea"
              rows="4"
              placeholder="Подробное описание задачи, инструкции или комментарии..."
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">ID объекта (название)</label>
            <input
              v-model="form.objectId"
              type="text"
              class="fluent-input"
              placeholder="Укажите ID или код объекта"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Ответственные пользователи</label>
            <select 
              v-model="form.responsibleUserIds" 
              class="fluent-select" 
              multiple 
              style="height: 96px;"
            >
              <option 
                v-for="u in usersList" 
                :key="u.id" 
                :value="u.id"
              >
                {{ u.full_name || u.email }}
              </option>
            </select>
            <span class="field-hint">Зажмите Ctrl (или Cmd), чтобы выбрать нескольких</span>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="goBack">
            Отмена
          </button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting || isLoading">
            <span v-if="isSubmitting">Сохранение...</span>
            <span v-else>{{ isEdit ? 'Сохранить изменения' : 'Создать задачу' }}</span>
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTasks } from '~/composables/useTasks'
import { apiFetch } from '~/composables/useAPI'
import { TaskType, TaskStatus } from '~/types/task'

const route = useRoute()
const router = useRouter()

const taskId = computed(() => route.params.id as string)
const isEdit = computed(() => taskId.value !== 'new' && !!taskId.value)

const { createTask, updateTask, fetchTask, isLoading, error } = useTasks()

const isSubmitting = ref(false)
const usersList = ref<any[]>([])

const form = reactive({
  title: '',
  type: TaskType.CMR_CHECK,
  status: TaskStatus.NEW,
  description: '',
  objectId: '',
  responsibleUserIds: [] as string[]
})

const loadUsers = async () => {
  try {
    const res = await apiFetch<any>('/users/')
    if (res?.data) {
      usersList.value = res.data
    }
  } catch (e) {
    console.error('Ошибка при загрузке пользователей:', e)
  }
}

const loadTaskData = async () => {
  if (!isEdit.value) return

  const numericId = Number(taskId.value)
  const task = await fetchTask(numericId)

  if (task) {
    form.title = task.title || ''
    form.type = task.type || TaskType.CMR_CHECK
    form.status = task.status || TaskStatus.NEW
    form.description = task.description || ''
    form.objectId = task.objectId || task.object_id || ''
    form.responsibleUserIds = task.responsibleUserIds || task.responsible_user_ids || []
  }
}

const goBack = () => {
  router.push('/tasks')
}

const handleSubmit = async () => {
  isSubmitting.value = true
  let result = null

  try {
    if (isEdit.value) {
      result = await updateTask(Number(taskId.value), form)
    } else {
      result = await createTask(form)
    }

    if (result) {
      goBack()
    }
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
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 12px 20px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #0078d4;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background-color 0.1s ease;
}

.btn-back:hover {
  background-color: #f3f3f3;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #242424;
  margin: 0;
}

.form-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 24px;
}

.shimmer-loader {
  color: #605e5c;
  font-size: 14px;
  text-align: center;
  padding: 40px;
}

.fluent-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.full-width {
  grid-column: 1 / -1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #323130;
}

.required {
  color: #a80000;
}

.fluent-input,
.fluent-select,
.fluent-textarea {
  border: 1px solid #8a8886;
  border-bottom: 2px solid #605e5c;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  font-family: inherit;
  background: #ffffff;
  transition: border-color 0.15s ease;
  box-sizing: border-box;
  width: 100%;
}

.fluent-input:focus,
.fluent-select:focus,
.fluent-textarea:focus {
  outline: none;
  border-color: #0078d4;
  border-bottom-color: #0078d4;
}

.field-hint {
  font-size: 11px;
  color: #605e5c;
}

.error-banner {
  background-color: #fde7e9;
  color: #a80000;
  padding: 10px 14px;
  border-radius: 4px;
  font-size: 13px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  border-top: 1px solid #f3f2f1;
  padding-top: 16px;
}

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  border: none;
  height: 32px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.15s ease;
}

.btn-primary:hover {
  background-color: #106ebe;
}

.btn-primary:disabled {
  background-color: #c8c8c8;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ffffff;
  border: 1px solid #d1d1d1;
  height: 32px;
  padding: 0 20px;
  font-size: 13px;
  font-weight: 400;
  color: #242424;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #f3f3f3;
}
</style>