<template>
  <div class="fluent-object-card" @click="openModal">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="region-tag">{{ obj.region || 'Не указан' }}</span>
          <span 
            v-if="obj.source" 
            class="source-tag" 
            :class="obj.source.toLowerCase().replace(/\s+/g, '-')"
          >
            {{ obj.sourceLabel || obj.source }}
          </span>
        </div>
        <h3 class="object-title" :title="obj.title">{{ obj.title }}</h3>
      </div>
      <span class="status-badge" :class="statusSlug">
        <span class="status-dot"></span>
        {{ getStatusLabel(obj.status) }}
      </span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="fluent-icon">🏢</span>
        <div class="info-content">
          <span class="info-label">Генподрядчик</span>
          <span class="info-value text-ellipsis">
            {{ getField('contractor') }}
          </span>
        </div>
      </div>
      <div class="info-row">
        <span class="fluent-icon">🛡️</span>
        <div class="info-content">
          <span class="info-label">Заказчик / Исполнитель</span>
          <span class="info-value text-ellipsis">
            {{ getField('executor') }}
          </span>
        </div>
      </div>

      <div class="card-divider"></div>

      <div class="progress-section">
        <div class="progress-header">
          <span class="section-subtitle">Освоение объёмов (СМР)</span>
          <span class="progress-percent">{{ obj.progressSMR || 0 }}%</span>
        </div>
        <div class="progress-bar-bg">
          <div 
            class="progress-bar-fill" 
            :style="{ width: (obj.progressSMR || 0) + '%' }"
            :class="{ warning: (obj.progressSMR || 0) < 30, success: (obj.progressSMR || 0) >= 70 }"
          ></div>
        </div>
      </div>

      <div class="dates-row">
        <div class="date-item">
          <span class="date-label">Контракт:</span>
          <span class="date-val">{{ obj.contractNumber || '—' }}</span>
        </div>
        <div class="date-item" v-if="obj.endDate">
          <span class="date-label">Срок до:</span>
          <span class="date-val">{{ obj.endDate }}</span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <div class="finance-brief">
        <div class="fin-item">
          <span class="fin-lbl">Контракт</span>
          <span class="fin-val">{{ getField('contractAmount') }}</span>
        </div>
        <div class="fin-item">
          <span class="fin-lbl">Освоено</span>
          <span class="fin-val success">{{ getField('spentAmount') }}</span>
        </div>
      </div>
      <span v-if="obj.isOverdue" class="overdue-tag">⚠️ Просрочка</span>
    </div>

    <CommonModal
      :is-open="isModalOpen"
      :title="obj.title"
      width="720px"
      @close="closeModal"
    >
      <div class="detail-content">
        <div class="detail-section">
          <h4 class="section-title">Основные реквизиты</h4>
          <div class="detail-grid">
            <div class="detail-field">
              <label>Административный округ</label>
              <div class="field-value">{{ obj.region || 'Не указан' }}</div>
            </div>
            <div class="detail-field">
              <label>Статус</label>
              <div class="field-value">{{ getStatusLabel(obj.status) }}</div>
            </div>
            <div class="detail-field full-width">
              <label>Адрес объекта</label>
              <div class="field-value text-wrap">{{ obj.address || 'Не указан' }}</div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">Участники и контракт</h4>
          <div class="detail-grid">
            <div class="detail-field">
              <label>Генподрядчик</label>
              <div class="field-value">{{ getField('contractor') }}</div>
            </div>
            <div class="detail-field">
              <label>Заказчик / Исполнитель</label>
              <div class="field-value">{{ getField('executor') }}</div>
            </div>
            <div class="detail-field">
              <label>Номер контракта</label>
              <div class="field-value">{{ obj.contractNumber || '—' }}</div>
            </div>
            <div class="detail-field">
              <label>Дата контракта</label>
              <div class="field-value">{{ obj.contractDate || '—' }}</div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">Финансовые показатели</h4>
          <div class="bg-finance-grid">
            <div class="finance-row-item">
              <span class="fin-label">Сумма контракта:</span>
              <span class="fin-val val-total">{{ getField('contractAmount') }}</span>
            </div>
            <div class="finance-row-item">
              <span class="fin-label">Освоено средств:</span>
              <span class="fin-val val-spent">{{ getField('spentAmount') }}</span>
            </div>
            <div class="finance-row-item">
              <span class="fin-label">Остаток средств:</span>
              <span class="fin-val val-rem">{{ getField('remainingAmount') }}</span>
            </div>
          </div>
        </div>
      </div>
    </CommonModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ObjectItem } from '~/types/object'
import CommonModal from '~/components/common/common_modal.vue'

const props = defineProps<{
  obj: ObjectItem
}>()

const isModalOpen = ref(false)

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const statusMap: Record<string, string> = {
  pending: 'Ожидает',
  accepted: 'Принят',
  in_progress: 'В работе',
  completed: 'Завершён',
  paused: 'Приостановлен',
  cancelled: 'Отменён',
  expired: 'Истёк',
  failed: 'Сбой'
}

const getStatusLabel = (status: string) => statusMap[status] || status

const statusSlug = computed(() => {
  const status = props.obj.status || ''
  return `status-${status.toLowerCase().replace(/_/g, '-')}`
})

const getField = (key: keyof ObjectItem | string) => {
  if (props.obj[key as keyof ObjectItem]) {
    return props.obj[key as keyof ObjectItem]
  }
  if (props.obj.metadata_fields && props.obj.metadata_fields[key]) {
    return props.obj.metadata_fields[key]
  }
  return 'Не указано'
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
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.fluent-object-card:hover {
  border-color: #0078d4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

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
}

.badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.region-tag {
  background: #f3f2f1;
  color: #616161;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.source-tag {
  background: #eff6fc;
  color: #0078d4;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.object-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #242424;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Статусы */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  white-space: nowrap;
  background: #f3f2f1;
  color: #616161;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #a19f9d;
}

.status-badge.status-in-progress { background: #eef6ff; color: #0078d4; }
.status-badge.status-in-progress .status-dot { background: #0078d4; }

.status-badge.status-completed { background: #f0fdf4; color: #107c41; }
.status-badge.status-completed .status-dot { background: #107c41; }

.status-badge.status-pending { background: #fffdf5; color: #795e00; }
.status-badge.status-pending .status-dot { background: #ffb900; }

.status-badge.status-paused,
.status-badge.status-cancelled,
.status-badge.status-failed { background: #fdf2f2; color: #a4261d; }
.status-badge.status-paused .status-dot,
.status-badge.status-cancelled .status-dot,
.status-badge.status-failed .status-dot { background: #a4261d; }

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.fluent-icon {
  font-size: 14px;
}

.info-content {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.info-label {
  font-size: 11px;
  color: #797979;
}

.info-value {
  font-size: 13px;
  color: #242424;
  font-weight: 500;
}

.text-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-divider {
  height: 1px;
  background: #f3f2f1;
  margin: 2px 0;
}

/* Прогресс бар */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.section-subtitle {
  color: #616161;
}

.progress-percent {
  font-weight: 600;
  color: #242424;
}

.progress-bar-bg {
  height: 6px;
  background: #f3f2f1;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: #0078d4;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-bar-fill.warning { background: #ffb900; }
.progress-bar-fill.success { background: #107c41; }

.dates-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #616161;
}

.date-item {
  display: flex;
  gap: 4px;
}

.date-label {
  color: #797979;
}

.date-val {
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid #f3f2f1;
  padding-top: 10px;
}

.finance-brief {
  display: flex;
  gap: 16px;
}

.fin-item {
  display: flex;
  flex-direction: column;
}

.fin-lbl {
  font-size: 10px;
  color: #797979;
  text-transform: uppercase;
}

.fin-val {
  font-size: 13px;
  font-weight: 600;
  color: #242424;
}

.fin-val.success {
  color: #107c41;
}

.overdue-tag {
  font-size: 11px;
  color: #a4261d;
  background: #fdf2f2;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

/* Стили модального окна */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #616161;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-field label {
  font-size: 11px;
  font-weight: 600;
  color: #797979;
  display: block;
  margin-bottom: 4px;
}

.detail-field.full-width {
  grid-column: span 2;
}

.field-value {
  background: #f3f2f1;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #edebe9;
  font-size: 13px;
  color: #242424;
}

.field-value.text-wrap {
  white-space: normal;
  line-height: 1.4;
}

.bg-finance-grid {
  background-color: #fafafa;
  padding: 14px 16px;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.finance-row-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.fin-label { color: #616161; }
.val-total { color: #242424; font-weight: 600; }
.val-spent { color: #107c41; font-weight: 600; }
.val-rem { color: #0078d4; font-weight: 600; }
</style>