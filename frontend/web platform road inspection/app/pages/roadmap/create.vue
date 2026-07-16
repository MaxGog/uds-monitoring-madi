<template>
  <div class="roadmap-create-page">
    <div class="fluent-page-header">
      <div class="header-nav">
        <NuxtLink to="/roadmap" class="back-link">← Назад к списку ДК</NuxtLink>
      </div>
      <h1 class="page-title">Создание новой дорожной карты</h1>
      <p class="page-subtitle">Заполните параметры объекта, бюджетные лимиты и ключевые вехи реализации проекта.</p>
    </div>

    <form @submit.prevent="handleSubmit" class="fluent-form-container">
      
      <div class="form-section">
        <h3 class="section-title">📊 Основные параметры</h3>
        <div class="form-grid-2">
          <div class="fluent-field">
            <label for="title">Название проекта / Объекта *</label>
            <input 
              id="title" 
              v-model="form.title" 
              type="text" 
              placeholder="Например: Капитальный ремонт ОДХ по ул. Ленина" 
              required
              class="fluent-input"
            />
          </div>

          <div class="fluent-field">
            <label for="region">Территориальный округ *</label>
            <select id="region" v-model="form.region" required class="fluent-select">
              <option value="" disabled selected>Выберите округ</option>
              <option value="ЦАО">ЦАО</option>
              <option value="САО">САО</option>
              <option value="ЮАО">ЮАО</option>
              <option value="ЗАО">ЗАО</option>
              <option value="ВАО">ВАО</option>
            </select>
          </div>
        </div>

        <div class="form-grid-3" style="margin-top: 16px;">
          <div class="fluent-field">
            <label for="phase">Текущая фаза *</label>
            <select id="phase" v-model="form.phase" required class="fluent-select">
              <option value="Разработка проекта">Разработка проекта</option>
              <option value="Подготовка ИД">Подготовка ИД</option>
              <option value="Проверка согласований">Проверка согласований</option>
              <option value="Утверждено">Утверждено</option>
            </select>
          </div>

          <div class="fluent-field">
            <label for="risk">Уровень риска *</label>
            <select id="risk" v-model="form.risk" required class="fluent-select">
              <option value="Низкий">Низкий риск</option>
              <option value="Средний">Средний риск</option>
              <option value="Высокий">Высокий риск</option>
            </select>
          </div>

          <div class="fluent-field">
            <label for="progress">Прогресс выполнения (%)</label>
            <input 
              id="progress" 
              v-model.number="form.progressPercentage" 
              type="number" 
              min="0" 
              max="100" 
              placeholder="0"
              class="fluent-input"
            />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">📅 Сроки, Финансы и Ответственные</h3>
        <div class="form-grid-2">
          <div class="fluent-field">
            <label for="startDate">Дата начала *</label>
            <input 
              id="startDate" 
              v-model="form.startDate" 
              type="date" 
              required
              class="fluent-input"
            />
          </div>

          <div class="fluent-field">
            <label for="endDate">Дата окончания *</label>
            <input 
              id="endDate" 
              v-model="form.endDate" 
              type="date" 
              required
              class="fluent-input"
            />
          </div>
        </div>

        <div class="form-grid-3" style="margin-top: 16px;">
          <div class="fluent-field">
            <label for="cost">Плановый бюджет (руб.) *</label>
            <input 
              id="cost" 
              v-model.number="form.cost" 
              type="number" 
              placeholder="15000000" 
              required
              class="fluent-input"
            />
          </div>

          <div class="fluent-field">
            <label for="area">Площадь объекта (кв. м)</label>
            <input 
              id="area" 
              v-model.number="form.area" 
              type="number" 
              placeholder="5400" 
              class="fluent-input"
            />
          </div>

          <div class="fluent-field">
            <label for="manager">Куратор ОДХ *</label>
            <input 
              id="manager" 
              v-model="form.manager" 
              type="text" 
              placeholder="Иванов И. И." 
              required
              class="fluent-input"
            />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">⚠️ Риски и Ограничения</h3>
        <div class="fluent-field">
          <label for="riskDescription">Описание факторов риска (если применимо)</label>
          <textarea 
            id="riskDescription" 
            v-model="form.riskDescription" 
            rows="3" 
            placeholder="Опишите возможные сдвиги сроков, проблемы с подрядчиком или иные риски..."
            class="fluent-textarea"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <div class="section-header-row">
          <h3 class="section-title">📌 Ключевые вехи (Milestones)</h3>
          <button type="button" class="fluent-button-secondary" @click="addMilestone">
            ＋ Добавить веху
          </button>
        </div>

        <div v-if="form.milestones.length === 0" class="empty-milestones-alert">
          Вехи не добавлены. Вы можете добавить ключевые контрольные точки для отслеживания графика.
        </div>

        <div v-else class="milestones-list">
          <div v-for="(milestone, index) in form.milestones" :key="index" class="milestone-row">
            <div class="milestone-fields">
              <input 
                v-model="milestone.name" 
                type="text" 
                placeholder="Название контрольной точки (например, Проектирование)" 
                required 
                class="fluent-input"
              />
              <div class="date-group">
                <label>План:</label>
                <input v-model="milestone.planDate" type="date" required class="fluent-input" />
              </div>
              <div class="date-group">
                <label>Факт:</label>
                <input v-model="milestone.factDate" type="date" class="fluent-input" />
              </div>
              <select v-model="milestone.status" class="fluent-select compact">
                <option value="В графике">В графике</option>
                <option value="Внимание">Внимание</option>
                <option value="Критический сдвиг">Критический сдвиг</option>
                <option value="Выполнено">Выполнено</option>
              </select>
            </div>
            <button type="button" class="delete-milestone-btn" @click="removeMilestone(index)">✕</button>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-banner">
        <strong>Ошибка сохранения:</strong> {{ error }}
      </div>

      <div class="form-actions">
        <NuxtLink to="/roadmap" class="fluent-button button-secondary">Отмена</NuxtLink>
        <button 
          type="submit" 
          class="fluent-button button-primary" 
          :disabled="isLoading"
        >
          <span v-if="isLoading">Сохранение...</span>
          <span v-else>Создать карту</span>
        </button>
      </div>

    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRoadmap } from '~/composables/useRoadmap'

const router = useRouter()
const { createRoadmap, isLoading, error } = useRoadmap()

const form = ref({
  title: '',
  objectId: Math.floor(Math.random() * 10000) + 1,
  region: '' as 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО' | '',
  startDate: '',
  endDate: '',
  phase: 'Разработка проекта' as 'Разработка проекта' | 'Подготовка ИД' | 'Проверка согласований' | 'Утверждено',
  risk: 'Низкий' as 'Низкий' | 'Средний' | 'Высокий',
  riskDescription: '',
  manager: '',
  cost: null as number | null,
  area: null as number | null,
  progressPercentage: 0,
  lastSource: 'Ручной ввод' as 'Ручной ввод',
  milestones: [] as Array<{
    id: number
    name: string
    planDate: string
    factDate: string | null
    status: 'В графике' | 'Внимание' | 'Критический сдвиг' | 'Выполнено'
  }>
})

const addMilestone = () => {
  form.value.milestones.push({
    id: Date.now(),
    name: '',
    planDate: '',
    factDate: null,
    status: 'В графике'
  })
}

const removeMilestone = (index: number) => {
  form.value.milestones.splice(index, 1)
}

const handleSubmit = async () => {
  if (new Date(form.value.startDate) > new Date(form.value.endDate)) {
    alert('Дата окончания не может быть раньше даты начала!')
    return
  }

  const payload = {
    ...form.value,
    budget: form.value.cost ? `${form.value.cost.toLocaleString('ru-RU')} ₽` : '0 ₽',
    responsibleManager: form.value.manager,
    hasRiskAlert: form.value.risk === 'Высокий'
  }

  const result = await createRoadmap(payload as any)
  
  if (result) {
    router.push('/roadmap')
  }
}
</script>

<style scoped>
.roadmap-create-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 16px;
  font-family: var(--fluent-font, "Segoe UI", -apple-system, sans-serif);
}

.fluent-page-header {
  margin-bottom: 28px;
}
.header-nav {
  margin-bottom: 8px;
}
.back-link {
  font-size: 13px;
  color: #0078d4;
  text-decoration: none;
  font-weight: 600;
}
.back-link:hover {
  text-decoration: underline;
}
.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #242424;
  margin: 0 0 6px 0;
}
.page-subtitle {
  font-size: 13px;
  color: #616161;
  margin: 0;
}

.fluent-form-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #242424;
  border-bottom: 1px solid #f3f2f1;
  padding-bottom: 8px;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid #f3f2f1;
  padding-bottom: 8px;
}
.section-header-row .section-title {
  margin: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.form-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.fluent-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.fluent-field label {
  font-size: 12px;
  font-weight: 600;
  color: #323130;
}

.fluent-input, .fluent-select, .fluent-textarea {
  border: 1px solid #d2d0ce;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  background: #ffffff;
  color: #242424;
  outline: none;
  transition: border-color 0.15s ease;
}
.fluent-input:focus, .fluent-select:focus, .fluent-textarea:focus {
  border-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4;
}

.fluent-textarea {
  resize: vertical;
}

.empty-milestones-alert {
  background: #fafafa;
  border: 1px dashed #d2d0ce;
  border-radius: 6px;
  padding: 16px;
  text-align: center;
  font-size: 13px;
  color: #616161;
}

.milestones-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.milestone-row {
  display: flex;
  gap: 12px;
  align-items: center;
  background: #fafafa;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #edebe9;
}

.milestone-fields {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 12px;
  width: 100%;
  align-items: center;
}

.date-group {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #616161;
}
.date-group label {
  white-space: nowrap;
}

.fluent-select.compact {
  padding: 6px;
}

.delete-milestone-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  color: #a80000;
  cursor: pointer;
  padding: 4px;
}
.delete-milestone-btn:hover {
  color: #e81123;
}

.error-banner {
  background: #fdf2f2;
  border: 1px solid #fde7e9;
  border-radius: 4px;
  color: #b13512;
  padding: 12px 16px;
  font-size: 13px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
}

.fluent-button {
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.1s ease;
}
.button-primary {
  background: #0078d4;
  border: 1px solid #0078d4;
  color: #ffffff;
}
.button-primary:hover:not(:disabled) {
  background: #106ebe;
}
.button-primary:disabled {
  background: #c8c6c4;
  border-color: #f3f2f1;
  color: #a19f9d;
  cursor: not-allowed;
}

.button-secondary {
  background: #ffffff;
  border: 1px solid #d2d0ce;
  color: #323130;
}
.button-secondary:hover {
  background: #f3f2f1;
}

.fluent-button-secondary {
  background: #ffffff;
  border: 1px solid #0078d4;
  color: #0078d4;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
}
.fluent-button-secondary:hover {
  background: #f4f9fd;
}
</style>