<template>
  <div class="create-object-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Новый объект мониторинга</h2>
        <span class="page-subtitle">Регистрация ОДХ и привязка к контрактной системе</span>
      </div>
      <div class="toolbar-actions">
        <NuxtLink to="/monitoring" class="fluent-button button-secondary">
          Отмена
        </NuxtLink>
        <button class="fluent-button button-primary" @click="handleSubmit">
          Сохранить объект
        </button>
      </div>
    </div>

    <div class="form-layout">
      <div class="form-section">
        <h3 class="section-title">Основные параметры</h3>
        <div class="form-grid">
          <div class="form-field full-width">
            <label>Наименование объекта дорожного хозяйства (ОДХ)</label>
            <input 
              v-model="form.title" 
              type="text" 
              class="fluent-input" 
              placeholder="Введите точное наименование объекта"
            />
          </div>

          <div class="form-field">
            <label>Административный округ (Регион)</label>
            <select v-model="form.region" class="fluent-select">
              <option disabled value="">Выберите округ</option>
              <option v-for="region in regions" :key="region" :value="region">
                {{ region }}
              </option>
            </select>
          </div>

          <div class="form-field">
            <label>Текущий статус объекта</label>
            <select v-model="form.status" class="fluent-select">
              <option value="В планировании">В планировании</option>
              <option value="Активен / В работе">Активен / В работе</option>
              <option value="Приемка объемов">Приемка объемов</option>
              <option value="Приостановлен">Приостановлен</option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Контрагенты и Исполнители</h3>
        <div class="form-grid">
          <div class="form-field">
            <label>Генеральный подрядчик</label>
            <input 
              v-model="form.contractor" 
              type="text" 
              class="fluent-input" 
              placeholder="Наименование организации"
            />
          </div>

          <div class="form-field">
            <label>Контролирующий орган / Эксплуатирующая организация</label>
            <input 
              v-model="form.executor" 
              type="text" 
              class="fluent-input" 
              placeholder="Ответственный орган"
            />
          </div>
        </div>
      </div>

      <div class="form-section connection-alert">
        <div class="alert-icon">📄</div>
        <div class="alert-content">
          <h4>Интеграция с актами выполненных работ</h4>
          <p>После сохранения объекта, акты с совпадающим наименованием строительного объекта будут автоматически консолидированы в карточке мониторинга.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useObject } from '~/composables/useObjects'
import type { ObjectCreate } from '~/types/object'

const router = useRouter()
const { createObject, isLoading, error } = useObject()

const regions = ['ЦАО', 'САО', 'ЮАО', 'ЗАО', 'ВАО'] as const

const form = ref<ObjectCreate>({
  title: '',
  region: 'ЦАО',
  status: 'Планирование',
  contractor: '',
  executor: '',
  progressSMR: 0,
  source: 'Ручной ввод',
  sourceLabel: 'Локальный ввод',
  contractNumber: '—',
  contractDate: new Date().toISOString().split('T')[0] || '',
  contractAmount: '0 ₽',
  spentAmount: '0 ₽',
  remainingAmount: '0 ₽',
  address: '',
  startDate: '',
  endDate: '',
  isOverdue: false,
  actsList: []
})

const handleSubmit = async () => {
  if (!form.value.title || !form.value.region) {
    alert('Пожалуйста, заполните обязательные поля: Наименование и Регион.')
    return
  }

  const result = await createObject(form.value)
  if (result) {
    router.push('/monitoring')
  }
}
</script>

<style scoped>
.create-object-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #242424;
}

.page-subtitle {
  font-size: 12px;
  color: #616161;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.fluent-button {
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 18px;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
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
  font-weight: 500;
  color: #242424;
}

.fluent-input,
.fluent-select {
  font-family: inherit;
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  background: #ffffff;
  color: #242424;
  width: 100%;
}

.fluent-input:focus,
.fluent-select:focus {
  border-color: #0078d4;
  outline: none;
}

.connection-alert {
  display: flex;
  gap: 16px;
  background: #f3f9f4;
  border: 1px solid #dff0d8;
  padding: 16px 20px;
}

.alert-icon {
  font-size: 20px;
}

.alert-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #107c41;
}

.alert-content p {
  margin: 0;
  font-size: 13px;
  color: #616161;
  line-height: 1.4;
}
</style>