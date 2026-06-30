<template>
  <div class="object-card">
    <div class="card-header">
      <h2 class="object-title">{{ title }}</h2>
      
      <div class="badge-group">
        <span class="badge badge-blue">{{ region }}</span>
        <span class="badge badge-orange">
          <span class="dot"></span> {{ status }}
        </span>
        <span class="badge badge-green-outline">{{ contractor }}</span>
        <span class="badge badge-green-outline">{{ executor }}</span>
      </div>
    </div>

    <div class="card-section">
      <h3 class="section-title">
        <span class="section-icon">ℹ️</span> Статус объекта
      </h3>
      
      <table class="property-table">
        <tbody>
          <tr v-for="(val, key) in statusProperties" :key="key">
            <td class="prop-label">{{ key }}</td>
            <td class="prop-value" :class="{ 'value-highlight': val !== 'Нет' }">
              {{ val }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <hr class="divider" />

    <div class="card-section">
      <h3 class="section-title">
        <span class="section-icon">🔳</span> Объём работ
      </h3>
      </div>

    <hr class="fluent-divider" />

    <div class="card-section">
      <h3 class="section-title">
        <span class="section-icon">📄</span> Контракт
      </h3>
      
      <table class="property-table">
        <tbody>
          <tr v-for="(val, key) in contractProperties" :key="key">
            <td class="prop-label">{{ key }}</td>
            <td class="prop-value">{{ val }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  region: string
  status: string
  contractor: string
  executor: string
  
  geometry?: string
  loadingSok?: string
  cardSok?: string
  updatingAis?: string
  contractorName?: string
  executorName?: string
  
  contractNumber?: string
  contractDate?: string
  contractSubject?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'НАИМЕНОВАНИЕ УЛИЦЫ',
  region: 'ОКРУГ',
  status: 'В РАБОТЕ',
  contractor: 'Contractor',
  executor: 'Executor',
  geometry: 'Нет',
  loadingSok: 'Нет',
  cardSok: 'Нет',
  updatingAis: 'Нет',
  contractorName: 'ООО "МосГорТранс"',
  executorName: 'МАДИ',
  contractNumber: '0000000',
  contractDate: '12.03.2012',
  contractSubject: 'Капремонт'
})

const statusProperties = computed(() => ({
  'Геометрия': props.geometry,
  'Акт': 'Нет',
  'Загрузка в СОК': props.loadingSok,
  'Карточка в СОК': props.cardSok,
  'Обновление АИС': props.updatingAis,
  'Подрядчик': props.contractorName,
  'Исполнитель': props.executorName,
}))

const contractProperties = computed(() => ({
  'Подрядчик': props.contractorName,
  'Номер договора': props.contractNumber,
  'Дата заключения': props.contractDate,
  'Предмет': props.contractSubject,
}))
</script>

<style scoped>
.object-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04), 0 1px 4px rgba(0, 0, 0, 0.02);
    border: 1px solid var(--fluent-gray-40);
    font-family: var(--fluent-font);
    max-width: 550px;
    width: 100%;
    box-sizing: border-box;
}

.card-header {
    margin-bottom: 20px;
}

.object-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--fluent-gray-100);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 12px 0;
    line-height: 1.3;
}

.badge-group {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.badge {
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 12px;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.badge-blue {
    background-color: var(--fluent-blue-light);
    color: var(--fluent-blue);
}

.badge-orange {
    background-color: #fff4ce;
    color: #a4261d;
}

.badge-orange .dot {
    width: 6px;
    height: 6px;
    background-color: #e81123;
    border-radius: 50%;
    display: inline-block;
}

.badge-green-outline {
    background-color: #f3f9f4;
    color: #107c41;
    border: 1px solid #dff0d8;
}

.card-section {
    margin: 16px 0;
}

.section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--fluent-gray-100);
    margin: 0 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-icon {
    font-size: 14px;
    color: var(--fluent-gray-80);
}

.property-table {
    width: 100%;
    border-collapse: collapse;
}

.property-table tr {
    height: 24px;
}

.prop-label {
    font-size: 12px;
    color: var(--fluent-gray-60);
    width: 40%;
    padding-right: 8px;
    vertical-align: middle;
}

.prop-value {
    font-size: 12px;
    font-weight: 500;
    color: var(--fluent-gray-100);
    width: 60%;
    vertical-align: middle;
}

.value-highlight {
    font-weight: 600;
}

.divider {
    border: none;
    height: 1px;
    background-color: var(--fluent-gray-20);
    margin: 16px 0;
}
</style>