<template>
  <div class="edit-object-page">
    <PageToolbar
      title="📝 Редактирование объекта"
      :subtitle="currentObject ? `Изменение параметров: ${currentObject.title}` : 'Загрузка параметров объекта...'"
    >
      <template #actions>
        <button 
          class="fluent-button button-secondary" 
          :disabled="isLoading" 
          @click="goBack"
        >
          Отмена
        </button>
        <button 
          class="fluent-button button-primary" 
          :disabled="isLoading || isCompaniesLoading" 
          @click="handleSubmit"
        >
          {{ isLoading ? 'Сохранение...' : 'Сохранить изменения' }}
        </button>
      </template>
    </PageToolbar>

    <div v-if="isLoadingObject && !currentObject" class="loading-container">
      🌀 Загрузка данных объекта из базы данных...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="form-layout">
      <div v-if="error" class="error-banner">
        ⚠️ Ошибка: {{ error }}
      </div>

      <div class="form-section">
        <h3 class="section-title">Основные параметры</h3>
        <div class="form-grid">
          <div class="form-group full-width">
            <label for="obj-title">Наименование объекта (ОДХ) *</label>
            <input 
              id="obj-title"
              v-model="form.title" 
              type="text" 
              required
              class="fluent-input" 
              placeholder="Введите наименование объекта"
            />
          </div>

          <div class="form-group full-width">
            <label for="obj-address">Адрес объекта</label>
            <input 
              id="obj-address"
              v-model="form.address" 
              type="text" 
              class="fluent-input" 
              placeholder="Адрес, километр, координаты"
            />
          </div>

          <div class="form-group">
            <label for="obj-district">Административный округ (Район)</label>
            <input 
              id="obj-district"
              v-model="form.district" 
              type="text" 
              class="fluent-input" 
              placeholder="Например, ЦАО"
            />
          </div>

          <div class="form-group">
            <label for="obj-status">Текущий статус объекта *</label>
            <select 
              id="obj-status"
              v-model="form.status" 
              required
              class="fluent-select"
            >
              <option v-for="status in availableStatuses" :key="status" :value="status">
                {{ getStatusLabel(status) }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Контрагенты и ответственные лица</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="obj-contractor">Генподрядная организация *</label>
            <select 
              id="obj-contractor"
              v-model.number="form.contractor_id" 
              required
              class="fluent-select"
              :disabled="isCompaniesLoading"
            >
              <option :value="null" disabled>
                {{ isCompaniesLoading ? 'Загрузка списка...' : 'Выберите компанию из реестра' }}
              </option>
              <option v-for="company in companies" :key="company.id" :value="company.id">
                {{ company.name }}
              </option>
            </select>
            <span class="field-hint">Справочник организаций подгружается автоматически</span>
          </div>

          <div class="form-group">
            <label for="obj-supervisor">Куратор (Супервайзер) *</label>
            <select 
              id="obj-supervisor"
              v-model.number="form.supervisor_id" 
              required
              class="fluent-select"
              :disabled="isSupervisorsLoading"
            >
              <option :value="null" disabled>
                {{ isSupervisorsLoading ? 'Загрузка списка...' : 'Выберите куратора' }}
              </option>
              <option v-for="user in supervisors" :key="user.id" :value="user.id">
                {{ user.name || user.username || user.email }}
              </option>
            </select>
            <span class="field-hint">Сотрудники ведомства, контролирующие ОДХ</span>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from '#app'
import { useObject } from '~/composables/useObjects'
import { ObjectStatus } from '~/types/enums'
import type { ObjectUpdate } from '~/types/object'
import PageToolbar from '~/components/common/page_toolbar.vue'

const route = useRoute()
const router = useRouter()
const objectId = computed(() => Number(route.params.id))

const { currentObject, fetchObject, updateObject, isLoading, error, cleanError } = useObject()

// Состояния загрузки справочников
const isCompaniesLoading = ref(false)
const isSupervisorsLoading = ref(false)
const isLoadingObject = ref(false)

// Списки для выпадающих меню
const companies = ref<any[]>([])
const supervisors = ref<any[]>([])

// Форма редактирования
const form = ref<ObjectUpdate>({
  title: '',
  address: '',
  district: '',
  status: ObjectStatus.PENDING,
  supervisor_id: null,
  contractor_id: null,
})

// Список доступных статусов из Enum
const availableStatuses = Object.values(ObjectStatus)

const getStatusLabel = (status: ObjectStatus): string => {
  const labels: Record<ObjectStatus, string> = {
    [ObjectStatus.PENDING]: 'Ожидает',
    [ObjectStatus.ACCEPTED]: 'Принят',
    [ObjectStatus.IN_PROGRESS]: 'В работе',
    [ObjectStatus.COMPLETED]: 'Завершен',
    [ObjectStatus.PAUSED]: 'Приостановлен',
    [ObjectStatus.CANCELLED]: 'Отменен',
    [ObjectStatus.EXPIRED]: 'Просрочен',
    [ObjectStatus.FAILED]: 'Провален'
  }
  return labels[status] || status
}

// Загрузка справочника компаний (исправленный эндпоинт без trailing slash)
const fetchCompaniesList = async () => {
  isCompaniesLoading.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/company', { method: 'GET' })
    companies.value = response.data || []
  } catch (err) {
    console.error('Не удалось загрузить справочник компаний:', err)
  } finally {
    isCompaniesLoading.value = false
  }
}

// Загрузка справочника кураторов
const fetchSupervisorsList = async () => {
  isSupervisorsLoading.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/company', { method: 'GET' })
    supervisors.value = response.data || []
  } catch (err) {
    console.error('Не удалось загрузить кураторов:', err)
  } finally {
    isSupervisorsLoading.value = false
  }
}

// Наполнение формы существующими данными объекта
const loadObjectData = async () => {
  isLoadingObject.value = true
  cleanError()
  try {
    await fetchObject(objectId.value)
    if (currentObject.value) {
      form.value = {
        title: currentObject.value.title,
        address: currentObject.value.address || '',
        district: currentObject.value.district || '',
        status: currentObject.value.status,
        // Забираем ID напрямую
        supervisor_id: currentObject.value.supervisor_id || null,
        contractor_id: currentObject.value.contractor_id || null,
      }
    }
  } catch (err) {
    console.error('Ошибка при инициализации данных объекта:', err)
  } finally {
    isLoadingObject.value = false
  }
}

const goBack = () => {
  router.push(`/monitoring/${objectId.value}`)
}

const handleSubmit = async () => {
  cleanError()

  if (!form.value.title || form.value.title.trim().length < 2) {
    error.value = 'Наименование объекта должно быть не менее 2 символов'
    return
  }

  const payload: Record<string, any> = {}

  if (form.value.title) payload.title = form.value.title.trim()
  
  if (form.value.address && form.value.address.trim().length >= 5) {
    payload.address = form.value.address.trim()
  } else if (!form.value.address) {
    payload.address = null
  }

  if (form.value.district && form.value.district.trim().length >= 2) {
    payload.district = form.value.district.trim()
  } else if (!form.value.district) {
    payload.district = null
  }

  if (form.value.status) {
    payload.status = form.value.status
  }

  payload.contractor_id = form.value.contractor_id && form.value.contractor_id !== null
    ? Number(form.value.contractor_id)
    : null

  payload.supervisor_id = form.value.supervisor_id && form.value.supervisor_id !== null
    ? Number(form.value.supervisor_id)
    : null

  console.log('Отправляем PATCH payload на бэкенд:', payload)

  // Вызываем обновление через composable
  const updated = await updateObject(objectId.value, payload)
  if (updated) {
    console.log('Объект успешно обновлен в БД:', updated)
    goBack()
  }
}

onMounted(() => {
  fetchCompaniesList()
  fetchSupervisorsList()
  loadObjectData()
})
</script>

<style scoped>
.edit-object-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

/* Стили для кнопок действий в тулбаре */
.fluent-button {
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.button-primary {
  background-color: #0078d4;
  color: #ffffff;
}

.button-primary:hover:not(:disabled) {
  background-color: #005a9e;
}

.button-primary:disabled {
  background-color: #f3f2f1;
  color: #a19f9d;
  cursor: not-allowed;
}

.button-secondary {
  background-color: #ffffff;
  color: #323130;
  border-color: #8a8886;
  margin-right: 8px; /* Отступ между Отменой и Сохранением */
}

.button-secondary:hover:not(:disabled) {
  background-color: #f3f2f1;
  border-color: #323130;
}

/* Форма и секции */
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #323130;
}

.full-width {
  grid-column: span 2;
}

.fluent-input,
.fluent-select {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  color: #242424;
  background: #ffffff;
  outline: none;
  transition: all 0.15s ease;
}

.fluent-input:focus,
.fluent-select:focus {
  border-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4;
}

.field-hint {
  font-size: 11px;
  color: #797979;
}

.error-banner {
  background: #fdf2f2;
  border: 1px solid #fde7e9;
  border-radius: 4px;
  color: #a80000;
  padding: 10px 14px;
  font-size: 13px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 48px;
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  color: #616161;
}
</style>