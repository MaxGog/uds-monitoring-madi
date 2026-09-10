<template>
  <div class="create-status-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Инициализация мониторинга / Добавление статуса ОДХ</h2>
        <span class="page-subtitle">Ввод базовых параметров объекта, финансовых лимитов и этапа контроля работ</span>
      </div>
      <div class="toolbar-actions">
        <NuxtLink to="/statuses" class="fluent-button button-secondary">
          Отмена
        </NuxtLink>
        <button class="fluent-button button-primary" @click="handleSubmit">
          Инициализировать мониторинг
        </button>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="form-layout">
      
      <div class="form-section">
        <h3 class="section-title">Основные реквизиты ОДХ и управление этапом</h3>
        <div class="form-grid">
          <div class="form-field full-width">
            <label>Наименование объекта (ОДХ)</label>
            <input 
              v-model="form.objectName" 
              type="text" 
              required 
              placeholder="Например: Капитальный ремонт ул. Тверская" 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Территориальное управление (Округ)</label>
            <select v-model="form.region" required class="fluent-select">
              <option value="" disabled>Выберите округ</option>
              <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <div class="form-field">
            <label>Ответственный менеджер / Инспектор</label>
            <input 
              v-model="form.manager" 
              type="text" 
              required 
              placeholder="Фамилия И. О." 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Текущий этап контроля</label>
            <select v-model="form.stage" required class="fluent-select">
              <option value="Проверка объемов">Проверка объемов</option>
              <option value="Анализ отклонений">Анализ отклонений</option>
              <option value="Приемка работ">Приемка работ</option>
              <option value="Завершено">Завершено</option>
            </select>
          </div>

          <div class="form-field">
            <label>Прогресс выполнения (%)</label>
            <input 
              v-model.number="form.progress" 
              type="number" 
              min="0" 
              max="100" 
              required 
              placeholder="Например: 45" 
              class="fluent-input"
            />
          </div>

          <div class="form-field full-width alert-toggle-field">
            <label class="checkbox-label">
              <input v-model="form.hasDeviationAlert" type="checkbox" class="fluent-checkbox" />
              <span>⚠️ Активировать маркер критического отклонения (Триггер аномалии)</span>
            </label>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Распределение бюджета и финансовых лимитов</h3>
        <p class="section-desc">Значения будут сконвертированы в текстовый формат отображения на карточках мониторинга.</p>
        
        <div class="form-grid">
          <div class="form-field">
            <label>Общий лимит финансирования (млн ₽)</label>
            <input 
              v-model.number="form.budgetTotal" 
              type="number" 
              step="any" 
              required 
              placeholder="Например: 12.5" 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Фактически освоено (млн ₽)</label>
            <input 
              v-model.number="form.budgetSpent" 
              type="number" 
              step="any" 
              required 
              placeholder="Например: 5.2" 
              class="fluent-input"
            />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Прогнозное планирование</h3>
        <div class="form-grid">
          <div class="form-field full-width">
            <label>Следующее запланированное действие системы</label>
            <input 
              v-model="form.nextAction" 
              type="text" 
              placeholder="Например: Формирование финального акта или Выездная проверка верификации" 
              class="fluent-input"
            />
          </div>
          <div class="form-field full-width">
            <label>Вводная запись для журнала изменений (History Log)</label>
            <textarea 
              v-model="form.initialComment" 
              rows="3" 
              placeholder="Опишите текущее состояние объекта для первой записи в таймлайне..." 
              class="fluent-textarea"
            ></textarea>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useWork } from '~/composables/useWork'

const router = useRouter()
const { createWork, error, isLoading } = useWork()

const regions = ['ЦАО', 'САО', 'СВАО', 'ВАО', 'ЮВАО', 'ЮАО', 'ЮЗАО', 'ЗАО', 'СЗАО', 'Новая Москва']

const form = reactive({
  objectName: '',
  region: 'ЦАО',
  manager: '',
  stage: 'Проверка объемов' as 'Проверка объемов' | 'Анализ отклонений' | 'Приемка работ' | 'Завершено',
  progress: 0,
  hasDeviationAlert: false,
  budgetTotal: null as number | null,
  budgetSpent: null as number | null,
  nextAction: '',
  initialComment: ''
})

const handleSubmit = async () => {
  const payload = {
    objectName: form.objectName,
    region: form.region,
    manager: form.manager,
    stage: form.stage,
    progress: form.progress,
    hasDeviationAlert: form.hasDeviationAlert,
    budgetTotal: form.budgetTotal || 0,
    budgetSpent: form.budgetSpent || 0,
    nextAction: form.nextAction,
    initialComment: form.initialComment
  }

  const result = await createWork(payload)
  
  if (result) {
    router.push('/work-statuses')
  } else {
    console.error("Ошибка при создании:", error.value)
  }
}
</script>

<style scoped>
.create-status-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 4px;
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
  flex-direction: column;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #242424;
}

.page-subtitle {
  font-size: 12px;
  color: #616161;
  margin-top: 4px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
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

.section-desc {
  font-size: 12px;
  color: #616161;
  margin: -12px 0 16px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.full-width {
  grid-column: span 2;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: #616161;
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
}

.fluent-input:focus,
.fluent-select:focus,
.fluent-textarea:focus {
  border-color: #0078d4;
  outline: none;
}

.alert-toggle-field {
  padding: 8px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.fluent-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #0078d4;
}
</style>