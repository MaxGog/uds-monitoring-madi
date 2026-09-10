<template>
  <div class="create-act-page">
    <PageToolbar
      title="Первичный ввод объёмов / Создание Акта"
      subtitle="Двухэтапная валидация данных ИС (Интеграция со скриптом Code.gs)"
    >
      <template #actions>
        <NuxtLink to="/acts" class="fluent-button button-secondary">
          Отмена
        </NuxtLink>
        <button 
          class="fluent-button button-primary" 
          :disabled="isSubmitting || isLoadingContracts || isLoadingCompanies || isLoadingWorks || isLoadingObjects"
          @click="handleSubmit"
        >
          {{ isSubmitting ? 'Сохранение...' : 'Сформировать акт' }}
        </button>
      </template>
    </PageToolbar>

    <form @submit.prevent="handleSubmit" class="form-layout">
      <div v-if="error" class="error-banner">
        ⚠️ {{ error }}
      </div>

      <div class="form-section">
        <h3 class="section-title">Основные реквизиты объекта и контракта</h3>
        <FormControls>
          <div class="form-group full-width">
            <label for="act-name">Наименование акта / Номер *</label>
            <input 
              id="act-name"
              v-model="form.name" 
              type="text" 
              required 
              placeholder="Например: Акт скрытых работ №12" 
              class="fluent-input"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="act-contract">Государственный контракт *</label>
              <select 
                id="act-contract"
                v-model="form.contractId" 
                class="fluent-select"
                required
                @change="onContractChange"
              >
                <option :value="null" disabled>Выберите контракт из списка...</option>
                <option 
                  v-for="contract in contracts" 
                  :key="contract.id" 
                  :value="contract.id"
                >
                  {{ `Контракт №${contract.id}` }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="act-company">Подрядчик (Организация) *</label>
              <select 
                id="act-company"
                v-model="form.companyId" 
                class="fluent-select"
                required
              >
                <option :value="null" disabled>Выберите подрядчика...</option>
                <option 
                  v-for="company in companies" 
                  :key="company.id" 
                  :value="company.id"
                >
                  {{ company.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="act-type">Тип акта</label>
              <select id="act-type" v-model="form.type" class="fluent-select">
                <option :value="ActType.CONTRACTOR">Подрядный (Contractor)</option>
                <option :value="ActType.SUPERVISORY">Технадзор (Supervisory)</option>
              </select>
            </div>

            <div class="form-group">
              <label for="act-region">Округ (Регион)</label>
              <select id="act-region" v-model="form.region" class="fluent-select">
                <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
          </div>

          <!-- Дополнительный выбор объекта, если у контракта нет object_id -->
          <div v-if="!contractObjectId" class="form-row">
            <div class="form-group full-width">
              <label for="act-object">Объект (выберите, если контракт не привязан к объекту)</label>
              <select 
                id="act-object"
                v-model="form.selectedObjectId" 
                class="fluent-select"
                @change="onObjectChange"
              >
                <option :value="null" disabled>Выберите объект...</option>
                <option 
                  v-for="obj in objects" 
                  :key="obj.id" 
                  :value="obj.id"
                >
                  {{ obj.title }} ({{ obj.address }})
                </option>
              </select>
              <span class="field-hint">Выберите объект, чтобы загрузить связанные с ним работы</span>
            </div>
          </div>
        </FormControls>
      </div>

      <div class="form-section">
        <h3 class="section-title">Табличная часть (Позиции акта)</h3>
        <p class="section-desc">
          Введите фактически выполненные объемы. 
          Нулевые или пустые строки не будут отправлены в систему.
        </p>

        <div v-if="!effectiveObjectId" class="info-message">
          ⚠️ Выберите контракт с привязанным объектом или выберите объект вручную.
        </div>
        <div v-else-if="isLoadingWorks" class="info-message">
          ⏳ Загрузка позиций контракта...
        </div>
        <div v-else-if="form.volumes.length === 0" class="info-message">
          ❌ У выбранного объекта нет связанных работ.
        </div>

        <div v-else class="volumes-table-wrapper">
          <table class="volumes-table">
            <thead>
              <tr>
                <th>Наименование работы</th>
                <th style="width: 120px;">План (стоимость)</th>
                <th style="width: 140px;">Факт (Выполнено)</th>
                <th style="width: 80px;">Ед. изм.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(vol, index) in form.volumes" :key="index">
                <td class="vol-name">{{ vol.name }}</td>
                <td>{{ vol.plan }}</td>
                <td>
                  <input 
                    v-model.number="vol.fact" 
                    type="number" 
                    step="0.01" 
                    min="0"
                    placeholder="0.00" 
                    class="fluent-table-input"
                  />
                </td>
                <td class="vol-unit">{{ vol.unit }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Блок добавления работы -->
        <div class="add-work-section">
          <template v-if="canAddWork">
            <button type="button" class="fluent-button button-secondary" @click="showAddWork = !showAddWork">
              {{ showAddWork ? 'Скрыть форму' : '+ Добавить работу' }}
            </button>
            <div v-if="showAddWork" class="add-work-form">
              <div class="form-row">
                <div class="form-group">
                  <label>Наименование работы *</label>
                  <input v-model="newWork.title" type="text" class="fluent-input" placeholder="Например: Укладка асфальта" />
                </div>
                <div class="form-group">
                  <label>Стоимость (план)</label>
                  <input v-model.number="newWork.cost" type="number" step="0.01" class="fluent-input" placeholder="0.00" />
                </div>
                <div class="form-group">
                  <label>Ед. изм.</label>
                  <input v-model="newWork.unit" type="text" class="fluent-input" placeholder="м³, т, шт" />
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="fluent-button button-primary" :disabled="isAddingWork" @click="addWork">
                  {{ isAddingWork ? 'Добавление...' : 'Добавить работу' }}
                </button>
                <button type="button" class="fluent-button button-secondary" @click="cancelAddWork">Отмена</button>
              </div>
            </div>
          </template>
          <div v-else class="info-message">
            ⚠️ Для добавления работы необходимо выбрать объект и подрядчика.
            <br>
            <span v-if="!effectiveObjectId">Сначала выберите контракт с объектом или выберите объект вручную.</span>
            <span v-else-if="!form.companyId">Выберите подрядчика.</span>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useActs } from '~/composables/useActs'
import { useObject } from '~/composables/useObjects'
import { ActType, ActStatus } from '~/types/enums'
import type { ActCreate } from '~/types/act'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FormControls from '~/components/common/form_controls.vue'

const router = useRouter()
const { createAct, isLoading: isActCreating } = useActs()
const { objects, fetchObjects, isLoading: isLoadingObjects } = useObject()

const contracts = ref<any[]>([])
const companies = ref<any[]>([])
const works = ref<any[]>([])

const isLoadingContracts = ref(false)
const isLoadingCompanies = ref(false)
const isLoadingWorks = ref(false)
const error = ref<string | null>(null)

const regions = ['ЦАО', 'САО', 'ЮАО', 'ЗАО', 'ВАО'] as const

const form = ref({
  name: '',
  contractId: null as number | null,
  companyId: null as number | null,
  selectedObjectId: null as number | null,
  region: 'ЦАО',
  type: ActType.CONTRACTOR,
  volumes: [] as {
    contract_item_id: number
    name: string
    plan: number
    unit: string
    fact: number
  }[]
})

const showAddWork = ref(false)
const isAddingWork = ref(false)
const newWork = ref({
  title: '',
  cost: 0,
  unit: 'шт'
})

const contractObjectId = computed(() => {
  const contract = contracts.value.find(c => c.id === form.value.contractId)
  return contract?.object_id || null
})

const effectiveObjectId = computed(() => {
  return contractObjectId.value || form.value.selectedObjectId || null
})

const canAddWork = computed(() => {
  return !!effectiveObjectId.value && !!form.value.companyId
})

const fetchContracts = async () => {
  isLoadingContracts.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/contract/', { method: 'GET' })
    contracts.value = response.data || []
  } catch (err) {
    error.value = 'Ошибка загрузки контрактов'
    console.error(err)
  } finally {
    isLoadingContracts.value = false
  }
}

const fetchCompanies = async () => {
  isLoadingCompanies.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/company/', { method: 'GET' })
    companies.value = response.data || []
  } catch (err) {
    error.value = 'Ошибка загрузки компаний'
    console.error(err)
  } finally {
    isLoadingCompanies.value = false
  }
}

const fetchWorks = async () => {
  isLoadingWorks.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/work/', { method: 'GET' })
    works.value = response.data || []
  } catch (err) {
    error.value = 'Ошибка загрузки списка работ'
    console.error(err)
  } finally {
    isLoadingWorks.value = false
  }
}

const updateVolumes = () => {
  const objId = effectiveObjectId.value
  if (!objId) {
    form.value.volumes = []
    return
  }

  const filteredWorks = works.value.filter(w => w.object?.id === objId)
  if (filteredWorks.length === 0) {
    form.value.volumes = []
    return
  }

  form.value.volumes = filteredWorks.map(w => ({
    contract_item_id: w.id,
    name: w.title,
    plan: w.cost || 0,
    unit: 'шт',
    fact: 0
  }))

  error.value = null
}

const onContractChange = () => {
  if (contractObjectId.value) {
    form.value.selectedObjectId = null
  }
  updateVolumes()
  showAddWork.value = false
  newWork.value = { title: '', cost: 0, unit: 'шт' }
}

const onObjectChange = () => {
  updateVolumes()
  showAddWork.value = false
  newWork.value = { title: '', cost: 0, unit: 'шт' }
}

const addWork = async () => {
  if (!newWork.value.title.trim()) {
    alert('Введите наименование работы')
    return
  }
  const objId = effectiveObjectId.value
  const companyId = form.value.companyId
  if (!objId || !companyId) {
    alert('Не выбран объект или подрядчик')
    return
  }

  isAddingWork.value = true
  try {
    const payload = {
      title: newWork.value.title,
      cost: newWork.value.cost || 0,
      object_id: objId,
      contractor_id: companyId,
      status: 'pending'
    }
    const response = await apiFetch<{ data: any }>('/work/', {
      method: 'POST',
      body: { data: payload }
    })
    const createdWork = response.data
    works.value.push(createdWork)
    updateVolumes()
    newWork.value = { title: '', cost: 0, unit: 'шт' }
    showAddWork.value = false
    error.value = null
  } catch (err: any) {
    error.value = err.data?.detail || 'Ошибка при создании работы'
    console.error(err)
  } finally {
    isAddingWork.value = false
  }
}

const cancelAddWork = () => {
  showAddWork.value = false
  newWork.value = { title: '', cost: 0, unit: 'шт' }
}

onMounted(async () => {
  await Promise.all([
    fetchContracts(),
    fetchCompanies(),
    fetchWorks(),
    fetchObjects()
  ])
  if (form.value.contractId) {
    updateVolumes()
  }
})

const isSubmitting = ref(false)

const handleSubmit = async () => {
  if (!form.value.name || !form.value.contractId || !form.value.companyId) {
    alert('Пожалуйста, заполните обязательные поля: Название акта, Контракт и Подрядчик')
    return
  }

  const objId = effectiveObjectId.value
  if (!objId) {
    alert('Не выбран объект (контракт не привязан к объекту, и объект не выбран вручную)')
    return
  }

  if (form.value.volumes.length === 0) {
    alert('У выбранного объекта нет позиций работ. Невозможно создать акт.')
    return
  }

  const items = form.value.volumes
    .filter(v => v.fact > 0)
    .map(v => ({
      contract_item_id: v.contract_item_id,
      completed_quantity: Number(v.fact)
    }))

  if (items.length === 0) {
    alert('Необходимо заполнить хотя бы одну позицию с объёмом выполнения > 0')
    return
  }

  isSubmitting.value = true
  const todayDate = new Date().toISOString().split('T')[0]

  const payload: ActCreate = {
    name: form.value.name,
    status: ActStatus.DRAFT,
    type: form.value.type,
    date_signed: todayDate || '',
    contract_id: form.value.contractId,
    object_id: objId,
    work_id: items[0]?.contract_item_id || null,
    items: items,
    metadata_fields: {
      region: form.value.region,
      companyId: form.value.companyId
    }
  }

  const result = await createAct(payload)
  isSubmitting.value = false

  if (result) {
    router.push('/acts')
  }
}
</script>

<style scoped>
.create-act-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', sans-serif;
  background-color: #f5f6f8;
  min-height: 100vh;
}

.toolbar,
.form-section {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1.6px 3.6px rgba(0, 0, 0, 0.06), 0 0.6px 1.6px rgba(0, 0, 0, 0.04);
  padding: 20px 24px;
  transition: box-shadow 0.2s;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e1e1e;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 13px;
  color: #605e5c;
  font-weight: 400;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.fluent-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  border-radius: 4px;
  border: 1px solid transparent;
  background: transparent;
  color: #323130;
  cursor: pointer;
  transition: background 0.1s, border-color 0.1s, box-shadow 0.1s;
  text-decoration: none;
  white-space: nowrap;
  min-height: 36px;
}

.button-secondary {
  background: #ffffff;
  border-color: #d2d0ce;
  color: #323130;
}
.button-secondary:hover {
  background: #f3f2f1;
  border-color: #b3b0ad;
}
.button-secondary:active {
  background: #e1dfdd;
}

.button-primary {
  background: #0078d4;
  border-color: #0078d4;
  color: #ffffff;
}
.button-primary:hover {
  background: #106ebe;
  border-color: #106ebe;
}
.button-primary:active {
  background: #005a9e;
}
.button-primary:disabled,
.fluent-button:disabled {
  background: #f3f2f1;
  color: #a19f9d;
  border-color: #f3f2f1;
  cursor: not-allowed;
  pointer-events: none;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e1e1e;
  border-bottom: 1px solid #edebe9;
  padding-bottom: 10px;
}

.section-desc {
  font-size: 13px;
  color: #605e5c;
  margin-top: -10px;
  margin-bottom: 18px;
  line-height: 1.4;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px 24px;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-field.full-width {
  grid-column: span 2;
}
.form-field label {
  font-size: 13px;
  font-weight: 500;
  color: #323130;
}

.fluent-input,
.fluent-select {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  font-family: inherit;
  background: #ffffff;
  color: #242424;
  width: 100%;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}
.fluent-input:focus,
.fluent-select:focus {
  border-color: #0078d4;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
}
.fluent-input::placeholder {
  color: #a19f9d;
}
.fluent-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23605e5c' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.volumes-table-wrapper {
  border: 1px solid #edebe9;
  border-radius: 4px;
  overflow: auto;
  margin-top: 4px;
}
.volumes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  text-align: left;
}
.volumes-table th {
  background: #faf9f8;
  padding: 10px 14px;
  font-weight: 600;
  color: #323130;
  border-bottom: 1px solid #edebe9;
  white-space: nowrap;
}
.volumes-table td {
  padding: 8px 14px;
  border-bottom: 1px solid #f3f2f1;
  vertical-align: middle;
}
.volumes-table tbody tr:hover {
  background-color: #f3f2f1;
}
.vol-name {
  font-weight: 500;
  color: #1e1e1e;
}
.vol-unit {
  color: #605e5c;
  font-size: 13px;
}
.fluent-table-input {
  width: 100%;
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.fluent-table-input:focus {
  border-color: #0078d4;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
}

.info-message,
.error-banner {
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
  border: 1px solid transparent;
}
.error-banner {
  background: #fde7e9;
  border-color: #fccfd2;
  color: #a80000;
}
.info-message {
  background: #f3f4f6;
  border-color: #e1e3e8;
  color: #323130;
}
.info-message:before {
  content: 'ℹ️ ';
}
.error-banner:before {
  content: '⚠️ ';
}

.add-work-section {
  margin-top: 24px;
  border-top: 1px solid #edebe9;
  padding-top: 18px;
}
.add-work-form {
  margin-top: 14px;
  padding: 18px 20px;
  background: #f9f8f7;
  border-radius: 6px;
  border: 1px solid #edebe9;
}
.add-work-form .form-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
.add-work-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.add-work-form .form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #323130;
}
.add-work-form .form-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.field-hint {
  font-size: 12px;
  color: #797775;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .create-act-page {
    padding: 16px;
  }
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .toolbar-actions {
    justify-content: flex-end;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-field.full-width {
    grid-column: 1;
  }
  .add-work-form .form-row {
    grid-template-columns: 1fr;
  }
  .form-row {
    flex-direction: column;
  }
}
</style>