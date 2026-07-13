<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h3 class="modal-title">{{ isEdit ? 'Редактирование задачи' : 'Новая задача' }}</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="handleSubmit" class="fluent-form">
        <div class="form-group">
          <label>Название задачи *</label>
          <input
            v-model="form.title"
            type="text"
            class="fluent-input"
            placeholder="Например: Проверка КС-2 по объекту..."
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Тип задачи *</label>
            <select v-model="form.type" class="fluent-select" required>
              <option :value="TaskType.CMR_CHECK">Проверка СМР</option>
              <option :value="TaskType.ACTS_EXPORT">Выгрузка актов</option>
              <option :value="TaskType.REGISTRY_RECONCILIATION">Сверка реестров</option>
              <option :value="TaskType.OTHER">Другое</option>
            </select>
          </div>

          <div class="form-group">
            <label>Статус</label>
            <select v-model="form.status" class="fluent-select">
              <option :value="TaskStatus.PENDING">В ожидании</option>
              <option :value="TaskStatus.STARTED">Запущена</option>
              <option :value="TaskStatus.IN_PROGRESS">В работе</option>
              <option :value="TaskStatus.COMPLETED">Завершена</option>
              <option :value="TaskStatus.PAUSED">Приостановлена</option>
              <option :value="TaskStatus.CANCELLED">Отменена</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Объект / Проект</label>
            <input
              v-model="form.objectTitle"
              type="text"
              class="fluent-input"
              placeholder="Объект строительства..."
            />
          </div>

          <div class="form-group">
            <label>Срок выполнения (Due Date)</label>
            <input
              v-model="form.dueDate"
              type="date"
              class="fluent-input"
            />
          </div>
        </div>

        <div class="form-group">
          <label>Описание</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="fluent-textarea"
            placeholder="Подробная информация о задаче..."
          ></textarea>
        </div>

        <div class="form-group">
          <label>Ответственные (через запятую)</label>
          <input
            v-model="responsibleInput"
            type="text"
            class="fluent-input"
            placeholder="Петров И.И., Сидоров А.В."
          />
        </div>

        <div class="checkbox-group">
          <label class="fluent-checkbox">
            <input type="checkbox" v-model="form.hasReminderTrigger" />
            <span class="checkmark"></span>
            <span>Включить напоминание</span>
          </label>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="$emit('close')">Отмена</button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner"></span>
            <span>{{ isSubmitting ? 'Сохранение...' : (isEdit ? 'Сохранить' : 'Создать') }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { TaskStatus, TaskType, type Task, type TaskCreate, type TaskUpdate } from '~/types/task'

const props = defineProps<{
  taskToEdit?: Task | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', payload: TaskCreate | TaskUpdate): void
}>()

const isEdit = computed(() => !!props.taskToEdit)
const isSubmitting = ref(false)
const responsibleInput = ref('')

const form = ref({
  title: '',
  description: '',
  type: TaskType.CMR_CHECK,
  status: TaskStatus.PENDING,
  objectTitle: '',
  dueDate: '',
  hasReminderTrigger: false,
})

onMounted(() => {
  if (props.taskToEdit) {
    form.value = {
      title: props.taskToEdit.title || '',
      description: props.taskToEdit.description || '',
      type: props.taskToEdit.type || TaskType.CMR_CHECK,
      status: props.taskToEdit.status || TaskStatus.PENDING,
      objectTitle: props.taskToEdit.objectTitle || '',
      dueDate: props.taskToEdit.dueDate ? props.taskToEdit.dueDate.split('T')[0] : '',
      hasReminderTrigger: props.taskToEdit.hasReminderTrigger || false,
    }
    responsibleInput.value = props.taskToEdit.responsibleNames?.join(', ') || ''
  }
})

const handleSubmit = () => {
  isSubmitting.value = true
  const responsibleNames = responsibleInput.value
    ? responsibleInput.value.split(',').map(s => s.trim()).filter(Boolean)
    : []

  const payload = {
    ...form.value,
    responsibleNames
  }

  emit('save', payload)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  display: grid;
  place-items: center;
  padding: 20px;
  z-index: 100;
}

.modal-card {
  background: #ffffff;
  border-radius: 8px;
  width: min(100%, 560px);
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #242424;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #605e5c;
  padding: 4px 8px;
  border-radius: 4px;
}
.close-btn:hover { background: #f3f3f3; color: #242424; }

.fluent-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
}

@media (max-width: 600px) {
  .form-row { flex-direction: column; }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #605e5c;
}

.fluent-input, .fluent-select, .fluent-textarea {
  border: 1px solid #8a8886;
  border-bottom: 2px solid #605e5c;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 13px;
  font-family: inherit;
  background: #ffffff;
  transition: border-color 0.15s ease;
}

.fluent-input:focus, .fluent-select:focus, .fluent-textarea:focus {
  outline: none;
  border-color: #0078d4;
  border-bottom-color: #0078d4;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.fluent-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
  user-select: none;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
  padding-top: 16px;
  border-top: 1px solid #f3f2f1;
}

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  border: none;
  height: 32px;
  padding: 0 18px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary:hover { background-color: #106ebe; }

.btn-secondary {
  background: #ffffff;
  border: 1px solid #d1d1d1;
  height: 32px;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
}
.btn-secondary:hover { background: #f5f5f5; }

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.8s linear infinite;
  margin-right: 6px;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>