<template>
  <div class="create-act-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Первичный ввод объёмов / Создание Акта</h2>
        <span class="page-subtitle">Двухэтапная валидация данных ИС (Интеграция со скриптом Code.gs)</span>
      </div>
      <div class="toolbar-actions">
        <NuxtLink to="/acts" class="fluent-button button-secondary">
          Отмена
        </NuxtLink>
        <button 
          class="fluent-button button-primary" 
          :disabled="isLoading" 
          @click="handleSubmit"
        >
          {{ isLoading ? 'Сохранение...' : 'Сформировать акт' }}
        </button>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="form-layout">
      <div class="form-section">
        <h3 class="section-title">Основные реквизиты объекта и контракта</h3>
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
            <label>Государственный контракт / Основание</label>
            <input 
              v-model="form.contractNumber" 
              type="text" 
              required 
              placeholder="ГК-2024/05" 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Округ (Регион)</label>
            <select v-model="form.region" class="fluent-select">
              <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <div class="form-field">
            <label>Подрядчик</label>
            <input 
              v-model="form.contractor" 
              type="text" 
              required 
              placeholder="ООО 'ДорСтрой'" 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Тип документа</label>
            <select v-model="form.type" class="fluent-select">
              <option value="acceptance">Приёмка работ</option>
              <option value="control">Технический контроль</option>
              <option value="inspection">Инспекция объемов</option>
            </select>
          </div>
        </div>
      </div>

      </form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useActs } from '~/composables/useActs'
import type { ActCreate } from '~/types/act'
import type { ActType } from '~/types/enums'

const router = useRouter()
const { createAct, isLoading } = useActs()

const regions = ['ЦАО', 'САО', 'ЮАО', 'ЗАО', 'ВАО'] as const

const form = reactive({
  objectName: '',
  contractNumber: '',
  region: 'ЦАО' as typeof regions[number],
  contractor: '',
  type: 'acceptance' as ActType,
  planAmount: '0.00',
  notes: '',
  volumes: [
    { name: '1. Фрезерование асфальтобетонного покрытия', plan: 1200, fact: 1200, unit: 'м³' },
    { name: '2. Укладка нижнего слоя покрытия', plan: 450, fact: 450, unit: 'т' }
  ]
})

const handleSubmit = async () => {
  const todayDate = new Date().toISOString().split('T')[0]
  
  const mappedType = form.type === 'contractor' || 'supervisory'

  const items = form.volumes
    .filter(v => v.plan > 0 || v.fact > 0)
    .map((v, index) => ({
      contract_item_id: index + 1,
      completed_quantity: Number(v.fact) || 0,
      price: 0
    }))

  const payload = {
    name: form.objectName ? `Акт: ${form.objectName}` : "Новый Акт",
    status: "draft",
    type: mappedType,
    date_signed: todayDate,
    object_id: null,
    contract_id: null,
    work_id: null,
    items: items,
    metadata_fields: {
      objectName: form.objectName,
      contractNumber: form.contractNumber,
      region: form.region,
      contractor: form.contractor,
      planAmount: form.planAmount,
      notes: form.notes,
      volumes: form.volumes
    }
  }

  const result = await createAct(payload as any)
  if (result) {
    router.push('/acts')
  }
}

</script>

<style scoped>
.create-act-page {
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
  color: var(--fluent-gray-100);
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
  color: var(--fluent-gray-100);
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
  color: var(--fluent-gray-100);
}

.fluent-input:focus,
.fluent-select:focus,
.fluent-textarea:focus {
  border-color: #0078d4;
  outline: none;
}

.volumes-table-wrapper {
  border: 1px solid #e1e3e8;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.volumes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.volumes-table th {
  background: #f3f4f6;
  padding: 10px 12px;
  font-weight: 600;
  color: #242424;
  border-bottom: 1px solid #e1e3e8;
}

.volumes-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.vol-name {
  color: var(--fluent-gray-100);
  font-weight: 500;
}

.vol-unit {
  color: #616161;
  font-size: 12px;
}

.fluent-table-input {
  width: 100%;
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 13px;
  box-sizing: border-box;
}

.fluent-table-input:focus {
  border-color: #0078d4;
  outline: none;
}
</style>