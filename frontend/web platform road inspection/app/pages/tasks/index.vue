<template>
  <div class="tasks-page">
    <PageToolbar
      title="Управление задачами"
      :countText="`Активных: ${activeTasksCount}`"
      :tabs="filters"
      :activeTab="currentFilter"
      @update:activeTab="value => currentFilter = value"
    >
      <template #actions>
        <button
          v-if="isAdmin"
          class="btn-primary"
          @click="isModalOpen = true"
        >
          <span class="btn-icon">＋</span> Создать задачу
        </button>
      </template>
    </PageToolbar>

    <div v-if="!isAdmin" class="admin-note">
      Создание задач доступно только пользователям с ролью администратора.
    </div>

    <div class="tasks-container">
      <div v-if="filteredTasks.length > 0" class="tasks-list">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          :is-admin="isAdmin"
          @toggle="handleToggleTask"
          @delete="handleDeleteTask"
        />
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">🎉</div>
        <h3>Нет задач</h3>
        <p>На текущий момент в данном фильтре нет подходящих задач.</p>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Новая задача</h3>
          <button class="close-modal-btn" @click="isModalOpen = false">✕</button>
        </div>

        <form @submit.prevent="createTask" class="modal-form">
          <div class="form-group">
            <label>Название задачи *</label>
            <input
              v-model="newTask.title"
              type="text"
              class="fluent-input"
              placeholder="Что нужно сделать..."
              required
            />
          </div>

          <div class="form-group">
            <label>Описание</label>
            <textarea
              v-model="newTask.description"
              class="fluent-textarea"
              placeholder="Детали задачи..."
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Объект УДС</label>
              <select
                v-model="newTask.objectTitle"
                class="fluent-select"
              >
                <option
                  v-for="obj in mockObjects"
                  :key="obj"
                  :value="obj"
                >
                  {{ obj }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Приоритет</label>
              <select v-model="newTask.priority" class="fluent-select">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Тип задачи</label>
              <select v-model="newTask.type" class="fluent-select">
                <option v-for="type in taskTypes" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Ответственный</label>
              <select v-model="newTask.responsibleName" class="fluent-select">
                <option
                  v-for="name in responsibleUsers"
                  :key="name"
                  :value="name"
                >
                  {{ name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Срок выполнения</label>
              <input
                v-model="newTask.dueDate"
                type="date"
                class="fluent-input"
              />
            </div>

            <div class="form-group">
              <label>Тип видимости</label>
              <select v-model="newTask.scope" class="fluent-select">
                <option value="own">Только мои</option>
                <option value="all">Общая задача</option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn-secondary"
              @click="isModalOpen = false"
            >
              Отмена
            </button>
            <button type="submit" class="btn-primary">Создать</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TaskCard from '~/components/cards/task_card.vue'
import { useAuth } from '~/composables/useAuth'
import PageToolbar from '~/components/common/page_toolbar.vue'

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

const { user } = useAuth()
const isAdmin = computed(() => user.value?.role === 'Администратор')

const filters = [
  { label: 'Мои задачи', value: 'own' },
  { label: 'Все задачи УДС', value: 'all' },
  { label: 'Выполненные', value: 'completed' }
]
const currentFilter = ref('own')
const isModalOpen = ref(false)

const mockObjects = [
  'ул. Тверская (Капитальный ремонт)',
  'Путепровод Ленинградского шоссе',
  'Парк Нагатинская Пойма',
  'Дублер Кутузовского проспекта'
]

const taskTypes = ['Согласование', 'Контроль', 'Документы', 'Мониторинг']
const responsibleUsers = [
  'Иванов И.',
  'Петров С.',
  'Назарова Е.',
  'Морозов А.',
  'АО Мосинжпроект'
]

const mockTasks = ref<Task[]>([
  {
    id: 1,
    title: 'Проверить ордер на земляные работы и фрезерование покрытия',
    description: 'Необходимо сверить сроки действия ордера ОАТИ с текущим графиком подрядчика на Тверской.',
    priority: 'high',
    priorityLabel: 'Высокий',
    objectTitle: 'ул. Тверская (Капитальный ремонт)',
    dueDate: '2026-07-02',
    assignee: 'Иванов И.',
    responsibleNames: ['Иванов И.'],
    type: 'Контроль',
    status: 'Активна',
    scope: 'own',
    completed: false,
    createdAt: '2026-06-28',
    authorName: 'Петров С.'
  },
  {
    id: 2,
    title: 'Согласовать технологическое окно с ОАО «РЖД»',
    description: 'Для монтажа пролетных строений путепровода требуется ночное окно 4 часа.',
    priority: 'high',
    priorityLabel: 'Высокий',
    objectTitle: 'Путепровод Ленинградского шоссе',
    dueDate: '2026-07-10',
    assignee: 'Назарова Е.',
    responsibleNames: ['Назарова Е.'],
    type: 'Согласование',
    status: 'Скоро дедлайн',
    scope: 'all',
    completed: false,
    createdAt: '2026-06-27',
    authorName: 'Иванова А.'
  },
  {
    id: 3,
    title: 'Запросить исполнительную документацию по нижнему слою асфальта',
    description: 'Взять акты скрытых работ и результаты лабораторных испытаний кернов.',
    priority: 'medium',
    priorityLabel: 'Средний',
    objectTitle: 'Парк Нагатинская Пойма',
    dueDate: '2026-07-05',
    assignee: 'Морозов А.',
    responsibleNames: ['Морозов А.'],
    type: 'Документы',
    status: 'Выполнена',
    scope: 'own',
    completed: true,
    createdAt: '2026-06-24',
    authorName: 'Иванов И.'
  }
])

const filteredTasks = computed(() => {
  if (currentFilter.value === 'completed') {
    return mockTasks.value.filter(t => t.completed)
  }
  if (currentFilter.value === 'own') {
    return mockTasks.value.filter(t => t.scope === 'own' && !t.completed)
  }
  return mockTasks.value.filter(t => !t.completed)
})

const activeTasksCount = computed(() => {
  return mockTasks.value.filter(t => !t.completed).length
})

const handleToggleTask = (id: number) => {
  if (!isAdmin.value) {
    return
  }
  const task = mockTasks.value.find(t => t.id === id)
  if (task) {
    task.completed = !task.completed
    task.status = task.completed ? 'Выполнена' : 'Активна'
  }
}

const handleDeleteTask = (id: number) => {
  if (!isAdmin.value) {
    return
  }
  mockTasks.value = mockTasks.value.filter(t => t.id !== id)
}

const newTask = ref({
  title: '',
  description: '',
  priority: 'medium',
  objectTitle: mockObjects[0],
  dueDate: '',
  scope: 'own',
  type: taskTypes[0],
  responsibleName: responsibleUsers[0]
})

const createTask = () => {
  const priorityLabels: Record<string, string> = { low: 'Низкий', medium: 'Средний', high: 'Высокий' }

  mockTasks.value.unshift({
    id: Date.now(),
    title: newTask.value.title,
    description: newTask.value.description,
    priority: newTask.value.priority,
    priorityLabel: priorityLabels[newTask.value.priority] || '',
    objectTitle: newTask.value.objectTitle || '',
    dueDate: newTask.value.dueDate || '',
    assignee: newTask.value.responsibleName || '',
    responsibleNames: String(newTask.value.responsibleName).split(',').map(s => s.trim()) || [''],
    type: newTask.value.type || '',
    status: 'Активна',
    scope: newTask.value.scope,
    completed: false,
    createdAt: new Date().toISOString().slice(0, 10),
    authorName: user.value?.name || 'Система'
  })

  newTask.value = {
    title: '',
    description: '',
    priority: 'medium',
    objectTitle: mockObjects[0],
    dueDate: '',
    scope: 'own',
    type: taskTypes[0],
    responsibleName: responsibleUsers[0]
  }
  isModalOpen.value = false
}
</script>

<style scoped>
.tasks-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: var(--fluent-font, sans-serif);
}

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  border: 1px solid transparent;
  height: 32px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-primary:hover {
  background-color: #106ebe;
}

.btn-secondary {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  height: 32px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f3f4f6;
}

.admin-note {
  padding: 14px 18px;
  border-radius: 10px;
  background: #fff7e6;
  border: 1px solid #ffe5b4;
  color: #8a5600;
  font-size: 13px;
}

.tasks-container {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tasks-list {
  display: flex;
  flex-direction: column;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #616161;
}

.empty-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  display: grid;
  place-items: center;
  padding: 24px;
  z-index: 50;
}

.modal-card {
  background: #ffffff;
  border-radius: 18px;
  width: min(100%, 640px);
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.16);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-modal-btn {
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.modal-form {
  display: grid;
  gap: 16px;
}

.form-group {
  display: grid;
  gap: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

label {
  font-size: 13px;
  font-weight: 700;
  color: #242424;
}

.fluent-input,
.fluent-textarea,
.fluent-select {
  width: 100%;
  border: 1px solid #d6d9dc;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  color: #242424;
  background: #ffffff;
}

.fluent-textarea {
  min-height: 100px;
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 720px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
