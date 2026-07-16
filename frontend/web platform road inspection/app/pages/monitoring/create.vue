<template>
  <div class="create-object-page">
    <!-- Использование системного PageToolbar -->
    <PageToolbar
      title="🏢 Новый объект мониторинга"
      subtitle="Регистрация ОДХ и связывание с контрагентами из БД"
    >
      <template #actions>
        <NuxtLink to="/monitoring" class="fluent-button button-secondary">
          Отмена
        </NuxtLink>
        <button class="fluent-button button-primary" :disabled="isLoading || isCompaniesLoading" @click="handleSubmit">
          {{ isLoading ? 'Сохранение...' : 'Сохранить объект' }}
        </button>
      </template>
    </PageToolbar>

    <form @submit.prevent="handleSubmit" class="form-layout">
      <!-- Блок ошибок бэкенда -->
      <div v-if="error" class="error-banner">
        ⚠️ Ошибка при создании объекта: {{ error }}
      </div>

      <!-- Основные параметры -->
      <div class="form-section">
        <h3 class="section-title">Основные параметры</h3>
        <FormControls>
          <div class="form-group full-width">
            <label for="obj-title">Наименование объекта (ОДХ) *</label>
            <input 
              id="obj-title"
              v-model="form.title" 
              type="text" 
              required
              class="fluent-input" 
              placeholder="Например, Ремонт автомобильной дороги по ул. Ленина"
            />
          </div>

          <div class="form-group full-width">
            <label for="obj-address">Адрес объекта * (минимум 5 символов)</label>
            <input 
              id="obj-address"
              v-model="form.address" 
              type="text" 
              required
              minlength="5"
              class="fluent-input" 
              placeholder="г. Москва, ул. Тверская, д. 1"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="obj-district">Административный округ (Регион) *</label>
              <select id="obj-district" v-model="form.district" required class="fluent-select">
                <option disabled value="">Выберите округ</option>
                <option v-for="district in districts" :key="district" :value="district">
                  {{ district }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="obj-status">Статус объекта *</label>
              <select id="obj-status" v-model="form.status" required class="fluent-select">
                <option v-for="(label, value) in statusLabels" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </div>
          </div>
        </FormControls>
      </div>

      <!-- Связи с БД: Генеральный подрядчик и Заказчик (Supervisor) -->
      <div class="form-section">
        <h3 class="section-title">Ответственные организации (из справочника компаний)</h3>
        <FormControls>
          <div class="form-row">
            <!-- Выпадающий список Заказчиков -->
            <div class="form-group">
              <label for="obj-supervisor">Заказчик (Supervisor) *</label>
              <select 
                id="obj-supervisor"
                v-model.number="form.supervisor_id" 
                required
                class="fluent-select"
              >
                <option :value="null" disabled>Выберите куратора</option>
                <option v-for="company in companies" :key="company.id" :value="company.id">
                  {{ company.name }}
                </option>
              </select>
              <span class="field-hint">Организация, осуществляющая технадзор</span>
            </div>

            <!-- Выпадающий список Подрядчиков -->
            <div class="form-group">
              <label for="obj-contractor">Генеральный подрядчик *</label>
              <select 
                id="obj-contractor"
                v-model.number="form.contractor_id" 
                required
                class="fluent-select"
              >
                <option :value="null" disabled>Выберите генподрядную организацию</option>
                <option v-for="company in companies" :key="company.id" :value="company.id">
                  {{ company.name }}
                </option>
              </select>
              <span class="field-hint">Организация, выполняющая работы</span>
            </div>
          </div>
        </FormControls>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useObject } from '~/composables/useObjects'
import { ObjectStatus } from '~/types/enums'
import type { ObjectCreate } from '~/types/object'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FormControls from '~/components/common/form_controls.vue'

const { createObject, isLoading, error } = useObject()

const districts = ['ЦАО', 'САО', 'ЮАО', 'ЗАО', 'ВАО', 'СЗАО', 'СВАО', 'ЮВАО', 'ЮЗАО']

const statusLabels: Record<ObjectStatus, string> = {
  [ObjectStatus.PENDING]: '⏳ Ожидает рассмотрения (Pending)',
  [ObjectStatus.ACCEPTED]: '✅ Принят в работу (Accepted)',
  [ObjectStatus.IN_PROGRESS]: '⚡ В процессе исполнения (In Progress)',
  [ObjectStatus.COMPLETED]: '🏁 Завершен успешно (Completed)',
  [ObjectStatus.PAUSED]: '⏸️ Временно приостановлен (Paused)',
  [ObjectStatus.CANCELLED]: '❌ Отменен (Cancelled)',
  [ObjectStatus.EXPIRED]: '⚠️ Срок действия истек (Expired)',
  [ObjectStatus.FAILED]: '🛑 Провален (Failed)'
}

const companies = ref<any[]>([])
const isCompaniesLoading = ref(false)

const fetchCompaniesList = async () => {
  isCompaniesLoading.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/company/', { method: 'GET' })
    companies.value = response.data || []
  } catch (err) {
    console.error('Не удалось загрузить справочник компаний:', err)
  } finally {
    isCompaniesLoading.value = false
  }
}

const form = ref<ObjectCreate>({
  title: '',
  address: '',
  district: '',
  status: ObjectStatus.PENDING,
  supervisor_id: null,
  contractor_id: null,
})

onMounted(() => {
  fetchCompaniesList()
})

const handleSubmit = async () => {
  if (!form.value.address || form.value.address.trim().length < 5) {
    alert('Адрес объекта должен содержать не менее 5 символов.')
    return
  }

  if (!form.value.supervisor_id || !form.value.contractor_id) {
    alert('Необходимо выбрать Заказчика и Генерального подрядчика из списков.')
    return
  }

  const payload: ObjectCreate = {
    title: form.value.title,
    address: form.value.address,
    district: form.value.district,
    status: form.value.status,
    supervisor_id: form.value.supervisor_id,
    contractor_id: form.value.contractor_id
  }

  const created = await createObject(payload)
  if (created) {
    await navigateTo('/monitoring')
  }
}
</script>

<style scoped>

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

.create-object-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.full-width {
  grid-column: span 2;
}

.error-banner {
  background: #fdf2f2;
  border: 1px solid #fde7e9;
  border-radius: 4px;
  color: #a80000;
  padding: 10px 14px;
  font-size: 13px;
}

.field-hint {
  font-size: 11px;
  color: #797979;
  margin-top: 2px;
}

.fluent-button {
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 20px;
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

.button-primary:disabled {
  background: #f3f2f1;
  color: #a19f9d;
  border-color: #f3f2f1;
  cursor: not-allowed;
}
</style>