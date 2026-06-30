<template>
  <div class="monitoring-page"> <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Управление задачами</h2>
        <span class="objects-count">Активных: {{ activeTasksCount }}</span>
      </div>
      
      <div class="toolbar-actions">
        <div class="fluent-pivot">
          <button 
            v-for="filter in filters" 
            :key="filter.value"
            class="pivot-item"
            :class="{ active: currentFilter === filter.value }"
            @click="currentFilter = filter.value"
          >
            {{ filter.label }}
          </button>
        </div>
        
        <button class="btn-primary" @click="isModalOpen = true">
          <span class="btn-icon">＋</span> Создать задачу
        </button>
      </div>
    </div>

    <div class="tasks-container">
      <div v-if="filteredTasks.length > 0" class="tasks-list">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
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
            <input v-model="newTask.title" type="text" class="fluent-input" placeholder="Что нужно сделать..." required />
          </div>

          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="newTask.description" class="fluent-textarea" placeholder="Детали задачи..."></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Объект УДС</label>
              <select v-model="newTask.objectTitle" class="fluent-select">
                <option v-for="obj in mockObjects" :key="obj" :value="obj">{{ obj }}</option>
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
              <label>Срок выполнения</label>
              <input v-model="newTask.dueDate" type="date" class="fluent-input" />
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
            <button type="button" class="btn-secondary" @click="isModalOpen = false">Отмена</button>
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

const mockTasks = ref<Task[]>([
  {
    id: 1,
    title: 'Проверить ордер на земляные работы и фрезерование покрытия',
    description: 'Необходимо сверить сроки действия ордера ОАТИ с текущим графиком подрядчика на Тверской.',
    priority: 'high',
    priorityLabel: 'Высокий',
    objectTitle: 'ул. Тверская (Капитальный ремонт)',
    dueDate: '2026-07-02',
    assignee: 'Иванов И. (Разработчик)',
    scope: 'own',
    completed: false
  },
  {
    id: 2,
    title: 'Согласовать технологическое окно с ОАО «РЖД»',
    description: 'Для монтажа пролетных строений путепровода требуется ночное окно 4 часа.',
    priority: 'high',
    priorityLabel: 'Высокий',
    objectTitle: 'Путепровод Ленинградского шоссе',
    dueDate: '2026-07-10',
    assignee: 'АО Мосинжпроект',
    scope: 'all',
    completed: false
  },
  {
    id: 3,
    title: 'Запросить исполнительную документацию по нижнему слою асфальта',
    description: 'Взять акты скрытых работ и результаты лабораторных испытаний кернов.',
    priority: 'medium',
    priorityLabel: 'Средний',
    objectTitle: 'Парк Нагатинская Пойма',
    dueDate: '2026-07-05',
    assignee: 'Иванов И. (Разработчик)',
    scope: 'own',
    completed: true
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
  const task = mockTasks.value.find(t => t.id === id)
  if (task) {
    task.completed = !task.completed
  }
}

const handleDeleteTask = (id: number) => {
  mockTasks.value = mockTasks.value.filter(t => t.id !== id)
}

const newTask = ref({
  title: '',
  description: '',
  priority: 'medium',
  objectTitle: mockObjects[0],
  dueDate: '',
  scope: 'own'
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
    assignee: 'Иванов И. (Разработчик)',
    scope: newTask.value.scope,
    completed: false
  })

  newTask.value = {
    title: '',
    description: '',
    priority: 'medium',
    objectTitle: mockObjects[0],
    dueDate: '',
    scope: 'own'
  }
  isModalOpen.value = false
}
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: var(--fluent-font, sans-serif);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #242424;
  margin: 0;
}

.objects-count {
  font-size: 13px;
  color: #616161;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.fluent-pivot {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 4px;
}

.pivot-item {
  background: transparent;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  color: #616161;
  cursor: pointer;
  border-radius: 4px;
  position: relative;
  transition: all 0.15s ease;
}

.pivot-item:hover {
  background: #f3f3f3;
  color: #242424;
}

.pivot-item.active {
  color: #0078d4;
  font-weight: 600;
}

.pivot-item.active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #0078d4;
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
.btn-primary:hover { background-color: #106ebe; }

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
.btn-secondary:hover { background: #f3f4f6; }

.tasks-container {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #616161;
}
.empty-icon { font-size: 28px; margin-bottom: 6px; }
.empty-state h3 { margin: 0 0 4px 0; color: #242424; }
.empty-state p { margin: 0; font-size: 12px; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card {
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.close-modal-btn {
  background: transparent;
  border: none;
  font-size: 14px;
  cursor: pointer;
  color: #616161;
}

.modal-form {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: #242424;
}

.form-row {
  display: flex;
  gap: 16px;
}

.fluent-input, .fluent-select, .fluent-textarea {
  border: 1px solid #a1a1a1;
  border-radius: 4px;
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  box-sizing: border-box;
  font-family: inherit;
}

.fluent-textarea {
  height: 64px;
  padding: 6px 10px;
  resize: none;
}

.fluent-input:focus, .fluent-select:focus, .fluent-textarea:focus {
  outline: none;
  border-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4 inset;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}
</style>