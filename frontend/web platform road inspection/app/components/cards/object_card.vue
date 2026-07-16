<template>
  <div class="fluent-object-card" @click="navigateToDetail">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="district-tag" :class="{ 'not-specified': !obj.district }">
            📍 {{ obj.district || 'Округ не указан' }}
          </span>
        </div>
        <h3 class="object-title" :title="obj.title">{{ obj.title }}</h3>
      </div>
      <span class="status-badge" :class="obj.status">
        <span class="status-dot"></span>
        {{ getStatusLabel(obj.status) }}
      </span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="fluent-icon">🗺️</span>
        <div class="info-content">
          <span class="info-label">Адрес объекта</span>
          <span class="info-value text-ellipsis" :title="obj.address || 'Не указан'">
            {{ obj.address || 'Адрес не указан' }}
          </span>
        </div>
      </div>

      <div class="info-row">
        <span class="fluent-icon">🏢</span>
        <div class="info-content">
          <span class="info-label">Генподрядчик</span>
          <span class="info-value text-ellipsis">
            {{ obj.contractor_name || (obj.contractor_id ? `Организация ID: ${obj.contractor_id}` : 'Не назначен') }}
          </span>
        </div>
      </div>

      <div class="info-row">
        <span class="fluent-icon">🛡️</span>
        <div class="info-content">
          <span class="info-label">Куратор</span>
          <span class="info-value text-ellipsis">
            {{ obj.supervisor_name || (obj.supervisor_id ? `Сотрудник ID: ${obj.supervisor_id}` : 'Не назначен') }}
          </span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <span class="object-id">ID: {{ obj.id }}</span>
      <span class="details-link">Подробнее →</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from '#app'
import { ObjectStatus } from '~/types/enums'
import type { ObjectItem } from '~/types/object'

const props = defineProps<{
  obj: ObjectItem
}>()

const router = useRouter()

// Переход на страницу детального просмотра
const navigateToDetail = () => {
  router.push(`/monitoring/${props.obj.id}`)
}

// Понятные лейблы для статусов
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
</script>

<style scoped>
.fluent-object-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  position: relative;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.fluent-object-card:hover {
  border-color: #0078d4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

/* Шапка */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-grow: 1;
  min-width: 0;
}

.badge-row {
  display: flex;
  gap: 6px;
}

.district-tag {
  font-size: 11px;
  font-weight: 600;
  background: #f3f2f1;
  color: #323130;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.district-tag.not-specified {
  background: #f3f2f1;
  color: #a19f9d;
}

.object-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #242424;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Статусы (Fluent Design палитра) */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

/* Цвета статусов */
.status-badge.pending { background: #fff4ce; color: #795300; }
.status-badge.pending .status-dot { background: #795300; }

.status-badge.accepted { background: #dff6dd; color: #107c41; }
.status-badge.accepted .status-dot { background: #107c41; }

.status-badge.in_progress { background: #deecf9; color: #0078d4; }
.status-badge.in_progress .status-dot { background: #0078d4; }

.status-badge.completed { background: #dff6dd; color: #107c41; }
.status-badge.completed .status-dot { background: #107c41; }

.status-badge.paused { background: #f3f2f1; color: #323130; }
.status-badge.paused .status-dot { background: #323130; }

.status-badge.cancelled, .status-badge.failed { background: #fde7e9; color: #a80000; }
.status-badge.cancelled .status-dot, .status-badge.failed .status-dot { background: #a80000; }

.status-badge.expired { background: #fde7e9; color: #d83b01; }
.status-badge.expired .status-dot { background: #d83b01; }

/* Тело */
.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.fluent-icon {
  font-size: 14px;
  margin-top: 1px;
  opacity: 0.8;
}

.info-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex-grow: 1;
}

.info-label {
  font-size: 10px;
  color: #797979;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.info-value {
  font-size: 12px;
  color: #242424;
  font-weight: 500;
}

.text-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Футер */
.card-footer {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #f3f2f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.object-id {
  font-size: 11px;
  color: #797979;
  font-family: monospace;
}

.details-link {
  font-size: 11px;
  font-weight: 600;
  color: #0078d4;
  transition: color 0.1s ease;
}

.fluent-object-card:hover .details-link {
  color: #005a9e;
}
</style>