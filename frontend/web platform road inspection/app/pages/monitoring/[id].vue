<template>
  <div class="object-detail-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <NuxtLink to="/monitoring" class="back-link">← Назад к списку</NuxtLink>
        <h2 class="page-title" v-if="currentObject">
          {{ currentObject.title }}
        </h2>
        <h2 class="page-title" v-else-if="isLoading">Загрузка объекта №{{ objectId }}...</h2>
        <h2 class="page-title" v-else>Объект не найден</h2>
      </div>
      <div class="toolbar-actions" v-if="currentObject">
        <button class="fluent-button button-danger" @click="handleDelete">
          Удалить объект
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-container">
      Загрузка подробной информации...
    </div>

    <div v-else-if="currentObject" class="detail-content">
      <div class="status-banner" :class="statusSlug">
        Текущий статус: <strong>{{ currentObject.status }}</strong> | Источник: {{ currentObject.sourceLabel || currentObject.source }}
      </div>

      <div class="pivot-nav">
        <button 
          class="pivot-item" 
          :class="{ active: activeTab === 'main' }" 
          @click="activeTab = 'main'"
        >
          Основное
        </button>
        <button 
          class="pivot-item" 
          :class="{ active: activeTab === 'finance' }" 
          @click="activeTab = 'finance'"
        >
          Финансы и Контракт
        </button>
        <button 
          class="pivot-item" 
          :class="{ active: activeTab === 'acts' }" 
          @click="activeTab = 'acts'"
        >
          Акты ({{ currentObject.connectedActsCount || (currentObject.actsList ? currentObject.actsList.length : 0) }})
        </button>
        <button 
          class="pivot-item" 
          :class="{ active: activeTab === 'history' }" 
          @click="activeTab = 'history'"
        >
          История изменений
        </button>
      </div>

      <div v-if="activeTab === 'main'" class="tab-card details-grid">
        <div class="detail-field full">
          <label>Полное наименование ОДХ</label>
          <div class="field-value text-wrap">{{ currentObject.title }}</div>
        </div>
        <div class="detail-field full" v-if="currentObject.address">
          <label>Адрес / Границы объекта</label>
          <div class="field-value">📍 {{ currentObject.address }}</div>
        </div>
        <div class="detail-field">
          <label>Административный округ</label>
          <div class="field-value">{{ currentObject.region }}</div>
        </div>
        <div class="detail-field">
          <label>Прогресс СМР</label>
          <div class="field-value font-semibold">{{ currentObject.progressSMR }} %</div>
        </div>
        <div class="detail-field">
          <label>Сроки проведения работ</label>
          <div class="field-value">
            📅 {{ currentObject.startDate || '—' }} — {{ currentObject.endDate || '—' }}
            <span v-if="currentObject.isOverdue" class="badge-danger">Просрочка</span>
          </div>
        </div>
        <div class="detail-field">
          <label>Генеральный подрядчик</label>
          <div class="field-value">{{ currentObject.contractor }}</div>
        </div>
        <div class="detail-field">
          <label>Контролирующий орган</label>
          <div class="field-value">{{ currentObject.executor }}</div>
        </div>
      </div>

      <div v-if="activeTab === 'finance'" class="tab-card details-grid">
        <div class="detail-field">
          <label>Номер контракта</label>
          <div class="field-value">{{ currentObject.contractNumber }}</div>
        </div>
        <div class="detail-field">
          <label>Дата регистрации</label>
          <div class="field-value">{{ currentObject.contractDate }}</div>
        </div>
        <div class="detail-field full bg-finance-grid">
          <div class="finance-row-item">
            <span class="fin-label">Сумма контракта:</span>
            <span class="fin-val val-total">{{ currentObject.contractAmount }}</span>
          </div>
          <div class="finance-row-item">
            <span class="fin-label">Освоено (Принято актами):</span>
            <span class="fin-val val-spent">{{ currentObject.spentAmount }}</span>
          </div>
          <div class="finance-row-item">
            <span class="fin-label">Остаток к освоению:</span>
            <span class="fin-val val-rem">{{ currentObject.remainingAmount }}</span>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'acts'" class="tab-card">
        <div v-if="currentObject.actsList && currentObject.actsList.length" class="acts-list">
          <div v-for="act in currentObject.actsList" :key="act.id" class="act-item-row">
            <div class="act-info">
              <span class="act-number">Акт № {{ act.number }}</span>
              <span class="act-date">от {{ act.date }}</span>
            </div>
            <div class="act-meta">
              <span class="act-amount">{{ act.amount }}</span>
              <span class="act-status-tag">{{ act.status }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          К данному объекту пока не привязано ни одного закрывающего акта СМР.
        </div>
      </div>

      <div v-if="activeTab === 'history'" class="tab-card">
        <div v-if="currentObject.historyLog && currentObject.historyLog.length" class="history-timeline">
          <div v-for="(log, idx) in currentObject.historyLog" :key="idx" class="history-item">
            <div class="history-meta">
              <span class="history-date">{{ log.date }}</span>
              <span class="history-user">👤 {{ log.user }}</span>
            </div>
            <div class="history-action">{{ log.action }}</div>
          </div>
        </div>
        <div v-else class="empty-state">
          История изменений пуста.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObject } from '~/composables/useObjects'

const route = useRoute()
const router = useRouter()
const { currentObject, fetchObject, deleteObject, isLoading, error } = useObject()

const objectId = computed(() => Number(route.params.id))
const activeTab = ref<'main' | 'finance' | 'acts' | 'history'>('main')

onMounted(() => {
  if (objectId.value) {
    fetchObject(objectId.value)
  }
})

const statusSlug = computed(() => {
  if (!currentObject.value) return 'neutral'
  switch (currentObject.value.status) {
    case 'Активный': return 'active'
    case 'На проверке': return 'review'
    case 'Планирование': return 'planning'
    case 'Завершено': return 'completed'
    default: return 'neutral'
  }
})

const handleDelete = async () => {
  if (confirm(`Вы действительно хотите удалить объект № ${objectId.value}?`)) {
    const success = await deleteObject(objectId.value)
    if (success) {
      router.push('/monitoring')
    }
  }
}
</script>

<style scoped>
.object-detail-page {
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
  gap: 6px;
}

.back-link {
  font-size: 12px;
  color: #0078d4;
  text-decoration: none;
  font-weight: 500;
}

.back-link:hover {
  text-decoration: underline;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #242424;
}

.fluent-button {
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.button-danger {
  background: #a80000;
  border: 1px solid #a80000;
  color: #ffffff;
}

.button-danger:hover {
  background: #790000;
  border-color: #790000;
}

.error-banner {
  padding: 12px 16px;
  background: #fdf2f2;
  border: 1px solid #fde7e9;
  color: #a80000;
  border-radius: 4px;
}

.loading-container {
  padding: 40px;
  background: #ffffff;
  border-radius: 8px;
  text-align: center;
  color: #616161;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-banner {
  padding: 10px 16px;
  font-size: 13px;
  border-left: 4px solid #0078d4;
  border-radius: 4px;
  background: #ffffff;
}
.status-banner.active { background: #fff4ce; border-left-color: #d83b01; color: #7a5c00; }
.status-banner.review { background: #eff6ff; border-left-color: #0078d4; color: #005a9e; }
.status-banner.planning { background: #f3f2f1; border-left-color: #616161; color: #323130; }
.status-banner.completed { background: #dff6dd; border-left-color: #107c41; color: #107c41; }

.pivot-nav {
  display: flex;
  gap: 16px;
  background: #ffffff;
  padding: 0 16px;
  border-radius: 4px;
  border: 1px solid #e1e3e8;
}

.pivot-item {
  background: none;
  border: none;
  padding: 12px 8px;
  font-size: 13px;
  color: #616161;
  cursor: pointer;
  position: relative;
  font-weight: 500;
}

.pivot-item.active {
  color: #0078d4;
  font-weight: 600;
}

.pivot-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #0078d4;
}

.tab-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-field.full {
  grid-column: span 2;
}

.detail-field label {
  font-size: 11px;
  font-weight: 600;
  color: #797979;
  display: block;
  margin-bottom: 4px;
}

.field-value {
  background: #f3f2f1;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #edebe9;
  font-size: 13px;
  color: #242424;
}

.bg-finance-grid {
  background-color: #fafafa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #eaeaea;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.finance-row-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.fin-label { color: #616161; }
.fin-val { font-weight: 600; }
.val-total { color: #242424; }
.val-spent { color: #107c41; }
.val-rem { color: #0078d4; }

.acts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.act-item-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  background: #f9f9f9;
  border: 1px solid #e1e1e1;
  border-radius: 4px;
}

.act-number { font-weight: 600; margin-right: 8px; }
.act-date { color: #616161; font-size: 12px; }
.act-amount { font-weight: 600; margin-right: 12px; }
.act-status-tag { font-size: 11px; background: #e1dfdd; padding: 2px 6px; border-radius: 2px; }

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  border-left: 2px solid #0078d4;
  padding-left: 12px;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #797979;
}

.history-action {
  font-size: 13px;
  color: #242424;
  margin-top: 2px;
}

.empty-state {
  color: #616161;
  font-size: 13px;
  text-align: center;
  padding: 24px;
}

.badge-danger {
  background: #fde7e9;
  color: #a80000;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 2px;
  margin-left: 6px;
}
</style>