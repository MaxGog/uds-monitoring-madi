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
@import './object_card.css';
</style>