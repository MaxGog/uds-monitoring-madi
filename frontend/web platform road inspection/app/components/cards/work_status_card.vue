<template>
  <div class="fluent-status-card" @click="isModalOpen = true">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="region-tag">{{ status.region }}</span>
          <span v-if="status.hasDeviationAlert" class="deviation-tag">⚠️ Отклонение</span>
        </div>
        <h3 class="status-title" :title="status.objectName">{{ status.objectName }}</h3>
      </div>
      <span class="status-badge" :class="stageSlug">
        <span class="status-dot"></span>
        {{ status.stage }}
      </span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="fluent-icon">👤</span>
        <div class="info-content">
          <span class="info-label">Ответственный менеджер</span>
          <span class="info-value text-ellipsis">{{ status.manager }}</span>
        </div>
      </div>
      <div class="info-row">
        <span class="fluent-icon">📅</span>
        <div class="info-content">
          <span class="info-label">Последнее обновление</span>
          <span class="info-value text-ellipsis">{{ status.updatedAt }}</span>
        </div>
      </div>

      <div class="card-divider"></div>

      <div class="progress-section">
        <div class="progress-header">
          <span class="section-subtitle">Прогресс выполнения этапа</span>
          <span class="progress-percentage">{{ status.progress }}</span>
        </div>
        <div class="fluent-progress-bar">
          <div class="progress-track" :style="{ width: progressValue + '%' }" :class="stageSlug"></div>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <span class="next-action-text text-ellipsis">
        🔮 <strong>Далее:</strong> {{ status.nextAction }}
      </span>
      <span class="view-details-lnk">Подробнее →</span>
    </div>

    <!-- Модальное окно деталей (Интеграция с CommonModal) -->
    <CommonModal :isOpen="isModalOpen" width="750px" @close="isModalOpen = false">
      <template #header>
        <div class="modal-header-layout">
          <span class="act-type">Этап: {{ status.stage }} | {{ status.region }} округ</span>
          <h3 class="modal-main-title">Контроль этапов и прогресса объекта № {{ status.id }}</h3>
        </div>
      </template>

      <div class="modal-status-extended">
        <div class="modal-status-banner" :class="stageSlug">
          <strong>Текущий статус:</strong> {{ status.stage }} (Прогресс: {{ status.progress }})
        </div>

        <h4 class="block-title">Основная информация</h4>
        <div class="details-grid">
          <div class="detail-field full">
            <label>Наименование объекта дорожного хозяйства</label>
            <div class="field-value font-semibold">{{ status.objectName }}</div>
          </div>
          <div class="detail-field">
            <label>Ответственный менеджер</label>
            <div class="field-value">👤 {{ status.manager }}</div>
          </div>
          <div class="detail-field">
            <label>Запланированное действие</label>
            <div class="field-value">🔮 {{ status.nextAction }}</div>
          </div>
        </div>

        <div class="modal-divider"></div>

        <h4 class="block-title">Распределение бюджета по объекту</h4>
        <div class="details-grid bg-finance-grid">
          <div class="detail-field">
            <label>Выделенный лимит бюджета</label>
            <div class="field-value-light">{{ status.budgetAllocation.total }}</div>
          </div>
          <div class="detail-field">
            <label>Освоено (Выплачено)</label>
            <div class="field-value-light">{{ status.budgetAllocation.spent }}</div>
          </div>
          <div class="detail-field full">
            <label>Свободный остаток лимита</label>
            <div class="total-highlight-value">{{ status.budgetAllocation.remaining }}</div>
          </div>
        </div>

        <div v-if="status.historyLog && status.historyLog.length" class="modal-divider"></div>

        <h4 v-if="status.historyLog && status.historyLog.length" class="block-title">История изменения статусов</h4>
        <div v-if="status.historyLog && status.historyLog.length" class="history-timeline">
          <div v-for="(log, idx) in status.historyLog" :key="idx" class="history-item">
            <div class="history-meta">
              <span class="history-date">{{ log.date }}</span>
              <span class="history-user">👤 {{ log.user }}</span>
            </div>
            <div class="history-action">{{ log.action }}</div>
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
import type { MockWorkStatus } from '~/composables/useMockData'
import CommonModal from '~/components/common/common_modal.vue'

const props = defineProps<{ status: MockWorkStatus }>()
const isModalOpen = ref(false)

const progressValue = computed(() => {
  const parsed = Number(props.status.progress.replace('%', ''))
  return Number.isFinite(parsed) ? parsed : 0
})

const stageSlug = computed(() => {
  switch (props.status.stage) {
    case 'Проверка объемов': return 'review'
    case 'Анализ отклонений': return 'deviation'
    case 'Приемка работ': return 'pending'
    case 'Завершено': return 'completed'
    default: return 'neutral'
  }
})
</script>

<style scoped>
.fluent-status-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 4px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.fluent-status-card:hover {
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

.deviation-tag {
  background: #fdf2f2;
  color: #b13512;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 2px;
}

.status-title {
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

.status-review { background: #eff6ff; color: #0078d4; }
.status-review .status-dot { background: #0078d4; }

.status-deviation { background: #fdf2f2; color: #b13512; }
.status-deviation .status-dot { background: #b13512; }

.status-pending { background: #fff4ce; color: #7a5c00; }
.status-pending .status-dot { background: #d83b01; }

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
.progress-track.deviation { background-color: #b13512; }
.progress-track.pending { background-color: #d83b01; }
.progress-track.completed { background-color: #107c41; }

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  border-top: 1px solid #f3f2f1;
  padding-top: 10px;
}

.next-action-text {
  color: #323130;
  max-width: 200px;
}

.view-details-lnk {
  color: #0078d4;
  font-weight: 600;
}

.modal-header-layout { display: flex; flex-direction: column; }
.modal-main-title { margin: 2px 0 0 0; font-size: 18px; font-weight: 600; color: #242424; }
.act-type { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #616161; }

.modal-status-extended { display: flex; flex-direction: column; gap: 14px; }
.modal-status-banner { padding: 10px 14px; border-radius: 4px; font-size: 13px; border-left: 4px solid #a1a1a1; }
.modal-status-banner.review { background: #eff6ff; color: #0078d4; border-left-color: #0078d4; }
.modal-status-banner.deviation { background: #fdf2f2; color: #b13512; border-left-color: #b13512; }
.modal-status-banner.pending { background: #fff4ce; color: #7a5c00; border-left-color: #d83b01; }
.modal-status-banner.completed { background: #dff6dd; color: #107c41; border-left-color: #107c41; }

.block-title { margin: 8px 0 2px 0; font-size: 12px; font-weight: 600; color: #616161; text-transform: uppercase; letter-spacing: 0.3px; }
.details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.detail-field { display: flex; flex-direction: column; gap: 4px; }
.detail-field.full { grid-column: span 2; }
.detail-field label { font-size: 11px; font-weight: 600; color: #797979; }

.field-value { background: #f3f2f1; padding: 8px 12px; border-radius: 4px; border: 1px solid #edebe9; font-size: 13px; color: #242424; }
.field-value-light { background: #fafafa; padding: 6px 10px; border-radius: 4px; border: 1px dashed #d2d0ce; font-size: 13px; }
.font-semibold { font-weight: 600; }

.bg-finance-grid { background-color: #fcfcfc; padding: 14px; border-radius: 6px; border: 1px solid #f0f0f0; }
.total-highlight-value { font-size: 22px; font-weight: 700; color: #107c41; margin-top: 2px; }
.modal-divider { height: 1px; background-color: #eaeaea; margin: 4px 0; }

.history-timeline { display: flex; flex-direction: column; gap: 12px; padding: 4px 0; }
.history-item { border-left: 2px solid #edebe9; padding-left: 12px; font-size: 13px; }
.history-meta { display: flex; gap: 12px; font-size: 11px; color: #797979; margin-bottom: 2px; }
.history-action { color: #242424; font-weight: 500; }

.fluent-button { font-size: 12px; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: 500; }
.button-secondary { background: #ffffff; border: 1px solid #d2d0ce; color: #323130; }
.button-secondary:hover { background: #f3f2f1; }
</style>