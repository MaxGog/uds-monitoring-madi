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
        <NuxtLink :to="`/monitoring/${objectId}/edit`" class="fluent-button button-secondary" style="margin-right: 8px;">
          ✏️ Редактировать
        </NuxtLink>
        <button class="fluent-button button-danger" @click="handleDelete">
          🗑️ Удалить объект
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      ⚠️ Ошибка: {{ error }}
    </div>

    <div v-if="isLoading" class="loading-container">
      🌀 Загрузка подробной информации об объекте...
    </div>

    <div v-else-if="currentObject" class="detail-content">
      <!-- Красивый статус-баннер на основе Enum -->
      <div class="status-banner" :class="currentObject.status">
        Текущий статус объекта: <strong>{{ formatStatus(currentObject.status) }}</strong>
      </div>

      <!-- Вкладки (Pivot-навигация) -->
      <div class="pivot-nav">
        <button 
          class="pivot-item" 
          :class="{ active: activeTab === 'main' }" 
          @click="activeTab = 'main'"
        >
          📁 Основные сведения
        </button>
        <button 
          class="pivot-item" 
          :class="{ active: activeTab === 'contracts' }" 
          @click="activeTab = 'contracts'"
        >
          📜 Договоры и Контрагенты
        </button>
      </div>

      <!-- Вкладка 1: Основное -->
      <div v-if="activeTab === 'main'" class="tab-card details-grid">
        <div class="detail-field full">
          <label>Полное наименование ОДХ</label>
          <div class="field-value text-wrap">{{ currentObject.title }}</div>
        </div>
        <div class="detail-field full" v-if="currentObject.address">
          <label>Адресные ориентиры (Границы объекта)</label>
          <div class="field-value">📍 {{ currentObject.address }}</div>
        </div>
        <div class="detail-field">
          <label>Административный округ</label>
          <div class="field-value">{{ currentObject.district || 'Не указан' }}</div>
        </div>
        <div class="detail-field">
          <label>Идентификатор в системе (ID)</label>
          <div class="field-value"># {{ currentObject.id }}</div>
        </div>
      </div>

      <!-- Вкладка 2: Договоры и связанные лица из БД -->
      <div v-if="activeTab === 'contracts'" class="tab-card details-grid">
        <div class="detail-field">
          <label>Куратор (Супервайзер)</label>
          <span class="info-value">{{ supervisorName }}</span>
        </div>
        <div class="detail-field">
          <label>Генподрядчик</label>
          <span class="info-value">{{ contractorName }}</span>
        </div>
        <div class="detail-field full bg-info-grid">
          <span class="info-label">Справочная информация:</span>
          <p class="info-desc">
            Все изменения привязок подрядных организаций и контролирующих органов выполняются через редактирование карточки объекта. Данные синхронизированы со справочником контрагентов.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObject } from '~/composables/useObjects'
import { ObjectStatus } from '~/types/enums'

const route = useRoute()
const router = useRouter()
const { currentObject, fetchObject, deleteObject, isLoading, error } = useObject()

const objectId = computed(() => Number(route.params.id))
const activeTab = ref<'main' | 'contracts'>('main')

onMounted(() => {
  if (objectId.value) {
    fetchObject(objectId.value)
  }
})

const formatStatus = (status: ObjectStatus) => {
  const statusMap: Record<ObjectStatus, string> = {
    [ObjectStatus.PENDING]: 'Ожидает рассмотрения',
    [ObjectStatus.ACCEPTED]: 'Принят в работу',
    [ObjectStatus.IN_PROGRESS]: 'В процессе выполнения',
    [ObjectStatus.COMPLETED]: 'Завершен успешно',
    [ObjectStatus.PAUSED]: 'Временно приостановлен',
    [ObjectStatus.CANCELLED]: 'Отменен',
    [ObjectStatus.EXPIRED]: 'Срок действия истек',
    [ObjectStatus.FAILED]: 'Не выполнен / Провален'
  }
  return statusMap[status] || status
}

const companies = ref<any[]>([])
const supervisors = ref<any[]>([])

// Загрузка справочников
const fetchReferences = async () => {
  try {
    // Загружаем компании
    const compRes = await apiFetch<{ data: any[] }>('/company/', { method: 'GET' })
    companies.value = compRes.data || []
    
    // Загружаем кураторов
    const supRes = await apiFetch<{ data: any[] }>('/users/supervisors', { method: 'GET' })
    supervisors.value = supRes.data || []
  } catch (err) {
    console.error('Ошибка при загрузке справочников:', err)
  }
}

// Находим имя компании по ID
const contractorName = computed(() => {
  if (!currentObject.value?.contractor_id) return 'Не назначен'
  const found = companies.value.find(c => c.id === currentObject.value.contractor_id)
  return found ? found.name : `Компания №${currentObject.value.contractor_id}`
})

// Находим имя куратора по ID
const supervisorName = computed(() => {
  if (!currentObject.value?.supervisor_id) return 'Не назначен'
  const found = supervisors.value.find(u => u.id === currentObject.value.supervisor_id)
  return found ? (found.name || found.username || found.email) : `Куратор №${currentObject.value.supervisor_id}`
})

onMounted(() => {
  fetchObject(objectId.value)
  fetchReferences()
})

const handleDelete = async () => {
  if (confirm(`Вы действительно хотите безвозвратно удалить объект № ${objectId.value} из базы данных?`)) {
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

.object-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
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
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid transparent;
}

.button-danger {
  background: #a80000;
  color: #ffffff;
}

.button-danger:hover {
  background: #790000;
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

/* Окрашивание статус-баннеров на основе Enum */
.status-banner {
  padding: 12px 16px;
  font-size: 13px;
  border-left: 4px solid #0078d4;
  border-radius: 4px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.status-banner.in_progress { background: #eff6ff; border-left-color: #0078d4; color: #005a9e; }
.status-banner.completed { background: #dff6dd; border-left-color: #107c41; color: #107c41; }
.status-banner.paused { background: #fff4ce; border-left-color: #d83b01; color: #7a5c00; }
.status-banner.cancelled, .status-banner.failed { background: #fde7e9; border-left-color: #a80000; color: #a80000; }

.pivot-nav {
  display: flex;
  gap: 16px;
  background: #ffffff;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
}

.pivot-item {
  background: none;
  border: none;
  padding: 14px 12px;
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
  padding: 10px 14px;
  border-radius: 4px;
  border: 1px solid #edebe9;
  font-size: 13px;
  color: #242424;
}

.sub-id {
  font-size: 11px;
  color: #797979;
  font-weight: normal;
}

.bg-info-grid {
  background-color: #fafafa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #eaeaea;
  font-size: 13px;
}

.info-label {
  font-weight: 600;
  color: #323130;
}

.info-desc {
  color: #616161;
  margin: 6px 0 0 0;
  line-height: 1.4;
}
</style>