<template>
  <div class="fluent-object-card" @click="isModalOpen = true">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="region-tag">{{ obj.region }}</span>
          <span class="source-tag" :class="obj.source.toLowerCase().replace(' ', '-')">{{ obj.source }}</span>
        </div>
        <h3 class="object-title" :title="obj.title">{{ obj.title }}</h3>
      </div>
      <span class="status-badge" :class="statusSlug">
        <span class="status-dot"></span>
        {{ obj.status }}
      </span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="fluent-icon">🏢</span>
        <div class="info-content">
          <span class="info-label">Генподрядчик</span>
          <span class="info-value text-ellipsis">{{ obj.contractor }}</span>
        </div>
      </div>
      <div class="info-row">
        <span class="fluent-icon">🛡️</span>
        <div class="info-content">
          <span class="info-label">Контролирующий орган</span>
          <span class="info-value text-ellipsis">{{ obj.executor }}</span>
        </div>
      </div>

      <div class="card-divider"></div>

      <div class="progress-section">
        <div class="progress-header">
          <span class="section-subtitle">Освоение объёмов (СМР)</span>
          <span class="progress-percentage" :class="{ 'completed': obj.progressSMR === 100 }">
            {{ obj.progressSMR }}%
          </span>
        </div>
        <div class="fluent-progress-bar">
          <div class="progress-track" :style="{ width: obj.progressSMR + '%' }" :class="statusSlug"></div>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <span class="acts-counter" v-if="obj.hasActs">
        📎 Связанных актов: <strong>{{ obj.connectedActsCount }}</strong>
      </span>
      <span class="acts-counter empty" v-else>
        ✕ Акты отсутствуют
      </span>
      <span class="view-details-lnk">Подробнее →</span>
    </div>

    <CommonModal :is-open="isModalOpen" :title="`Карточка мониторинга ОДХ № ${obj.id}`" width="750px" @close="isModalOpen = false">
      <div class="modal-object-details">
        <div class="modal-status-banner" :class="statusSlug">
          Текущий статус: <strong>{{ obj.status }}</strong> | {{ obj.sourceLabel }}
        </div>

        <div class="modal-pivot">
          <button class="pivot-item" :class="{ active: activeTab === 'main' }" @click="activeTab = 'main'">Основное</button>
          <button class="pivot-item" :class="{ active: activeTab === 'finance' }" @click="activeTab = 'finance'">Финансы и Контракт</button>
          <button class="pivot-item" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">История изменений</button>
        </div>

        <div v-if="activeTab === 'main'" class="tab-content details-grid">
          <div class="detail-field full">
            <label>Полное наименование ОДХ</label>
            <div class="field-value text-wrap">{{ obj.title }}</div>
          </div>
          <div class="detail-field">
            <label>Административный округ</label>
            <div class="field-value">{{ obj.region }}</div>
          </div>
          <div class="detail-field">
            <label>Прогресс строительно-монтажных работ</label>
            <div class="field-value">{{ obj.progressSMR }} %</div>
          </div>
          <div class="detail-field">
            <label>Генеральный подрядчик</label>
            <div class="field-value">{{ obj.contractor }}</div>
          </div>
          <div class="detail-field">
            <label>Орган исполнительной власти / Технадзор</label>
            <div class="field-value">{{ obj.executor }}</div>
          </div>
        </div>

        <div v-if="activeTab === 'finance'" class="tab-content details-grid">
          <div class="detail-field">
            <label>Номер контракта</label>
            <div class="field-value">{{ obj.contractNumber }}</div>
          </div>
          <div class="detail-field">
            <label>Дата регистрации</label>
            <div class="field-value">{{ obj.contractDate }}</div>
          </div>
          <div class="detail-field full bg-finance-grid">
            <div class="finance-row-item">
              <span class="fin-label">Сумма контракта:</span>
              <span class="fin-val val-total">{{ obj.contractAmount }}</span>
            </div>
            <div class="finance-row-item">
              <span class="fin-label">Освоено (Принято актами):</span>
              <span class="fin-val val-spent">{{ obj.spentAmount }}</span>
            </div>
            <div class="finance-row-item">
              <span class="fin-label">Остаток к освоению:</span>
              <span class="fin-val val-rem">{{ obj.remainingAmount }}</span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'history'" class="tab-content">
          <div class="history-timeline">
            <div v-for="(log, idx) in obj.historyLog" :key="idx" class="history-item">
              <div class="history-meta">
                <span class="history-date">{{ log.date }}</span>
                <span class="history-user">👤 {{ log.user }}</span>
              </div>
              <div class="history-action">{{ log.action }}</div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <button class="fluent-button button-secondary" @click="isModalOpen = false">Закрыть</button>
      </template>
    </CommonModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { MockObject } from '~/composables/useMockData'
import CommonModal from '~/components/common/common_modal.vue'

const props = defineProps<{ obj: MockObject }>()

const isModalOpen = ref(false)
const activeTab = ref<'main' | 'finance' | 'history'>('main')

const statusSlug = computed(() => {
  switch (props.obj.status) {
    case 'Активный': return 'active'
    case 'На проверке': return 'review'
    case 'Планирование': return 'planning'
    case 'Завершено': return 'completed'
    default: return 'neutral'
  }
})
</script>

<style scoped>
.fluent-object-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 4px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 240px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.fluent-object-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #0078d4;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.header-main {
  flex: 1;
  min-width: 0;
}

.badge-row {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.region-tag {
  background: #f3f2f1;
  color: #323130;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 2px;
}

.source-tag {
  background: #eff6ff;
  color: #0078d4;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 2px;
}
.source-tag.ручной-ввод {
  background: #f5f5f5;
  color: #616161;
}

.object-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #242424;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.status-badge {
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 2px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.status-active { background: #fff4ce; color: #7a5c00; }
.status-active .status-dot { background: #e81123; }

.status-review { background: #eff6ff; color: #0078d4; }
.status-review .status-dot { background: #0078d4; }

.status-planning { background: #f3f2f1; color: #323130; }
.status-planning .status-dot { background: #616161; }

.status-completed { background: #dff6dd; color: #107c41; }
.status-completed .status-dot { background: #107c41; }

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}

.info-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.fluent-icon {
  font-size: 14px;
  margin-top: 1px;
}

.info-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.info-label {
  font-size: 11px;
  color: #616161;
}

.info-value {
  font-size: 12px;
  color: #242424;
  font-weight: 500;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-divider {
  height: 1px;
  background-color: #f3f2f1;
  margin: 6px 0;
}

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

.progress-percentage {
  font-weight: 600;
  color: #0078d4;
}
.progress-percentage.completed {
  color: #107c41;
}

.fluent-progress-bar {
  height: 4px;
  background-color: #edebe9;
  border-radius: 2px;
  overflow: hidden;
}

.progress-track {
  height: 100%;
  background-color: #0078d4;
  transition: width 0.3s cubic-bezier(0.1, 0.9, 0.2, 1);
}
.progress-track.completed { background-color: #107c41; }
.progress-track.active { background-color: #d83b01; }
.progress-track.planning { background-color: #a1a1a1; }

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  border-top: 1px solid #f3f2f1;
  padding-top: 10px;
}

.acts-counter {
  color: #323130;
}
.acts-counter.empty {
  color: #a1a1a1;
}

.view-details-lnk {
  color: #0078d4;
  font-weight: 600;
}

.modal-object-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-status-banner {
  padding: 8px 12px;
  font-size: 13px;
  border-left: 3px solid #0078d4;
  border-radius: 2px;
}
.modal-status-banner.active { background: #fff4ce; border-left-color: #d83b01; color: #7a5c00; }
.modal-status-banner.review { background: #eff6ff; border-left-color: #0078d4; color: #005a9e; }
.modal-status-banner.planning { background: #f3f2f1; border-left-color: #616161; color: #323130; }
.modal-status-banner.completed { background: #dff6dd; border-left-color: #107c41; color: #107c41; }

.modal-pivot {
  display: flex;
  gap: 16px;
  border-bottom: 1px solid #eaeaea;
}

.modal-pivot .pivot-item {
  background: none;
  border: none;
  padding: 8px 4px;
  font-size: 13px;
  color: #616161;
  cursor: pointer;
  position: relative;
}

.modal-pivot .pivot-item.active {
  color: #0078d4;
  font-weight: 600;
}

.modal-pivot .pivot-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #0078d4;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
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

.field-value.text-wrap {
  white-space: normal;
  line-height: 1.4;
}

.bg-finance-grid {
  background-color: #fafafa;
  padding: 12px 16px;
  border-radius: 4px;
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

.fin-label {
  color: #616161;
}

.fin-val {
  font-weight: 600;
}
.val-total { color: #242424; }
.val-spent { color: #107c41; }
.val-rem { color: #0078d4; }

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px 0;
}

.history-item {
  border-left: 2px solid #edebe9;
  padding-left: 12px;
  font-size: 13px;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #797979;
  margin-bottom: 2px;
}

.history-action {
  color: #242424;
  font-weight: 500;
}

.fluent-button {
  font-family: inherit;
  font-size: 13px;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.button-secondary {
  background: #ffffff;
  border: 1px solid #d2d0ce;
  color: #323130;
}
.button-secondary:hover {
  background: #f3f2f1;
}
</style>