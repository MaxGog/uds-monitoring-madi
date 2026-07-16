<template>
  <div class="fluent-status-card" @click="isModalOpen = true">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="region-tag">{{ status.region || 'Не указан' }}</span>
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
          <span class="info-value text-ellipsis">{{ status.manager || 'Не назначен' }}</span>
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
          <span class="progress-percentage">{{ status.progress || '0%' }}</span>
        </div>
        <div class="fluent-progress-bar">
          <div class="progress-fill" :style="{ width: status.progress || '0%' }"></div>
        </div>
      </div>

      <div class="card-divider"></div>

      <div class="finance-section">
        <span class="section-subtitle">Финансовые показатели</span>
        <div class="finance-grid">
          <div class="finance-item">
            <span class="finance-label">Лимит</span>
            <span class="finance-value limit">{{ Number(status.budgetAllocation?.total || 0).toLocaleString('ru-RU') }} ₽</span>
          </div>
          <div class="finance-item">
            <span class="finance-label">Освоено</span>
            <span class="finance-value spent">{{ Number(status.budgetAllocation?.spent || 0).toLocaleString('ru-RU') }} ₽</span>
          </div>
          <div class="finance-item">
            <span class="finance-label">Остаток</span>
            <span class="finance-value remaining">{{ Number(status.budgetAllocation?.remaining || 0).toLocaleString('ru-RU') }} ₽</span>
          </div>
        </div>
      </div>

      <div class="card-divider"></div>

      <div class="action-section">
        <span class="section-subtitle">Ближайшее действие</span>
        <p class="action-text text-ellipsis-2" :title="status.nextAction">
          {{ status.nextAction || 'Нет запланированных действий' }}
        </p>
      </div>
    </div>

    <div v-if="isModalOpen" class="fluent-modal-overlay" @click.stop="isModalOpen = false">
      <div class="fluent-modal-window" @click.stop>
        
        <div class="modal-header">
          <div class="modal-header-title">
            <div class="modal-badge-row">
              <span class="region-tag">{{ status.region || 'Не указан' }}</span>
              <span v-if="status.hasDeviationAlert" class="deviation-tag">⚠️ Выявлены отклонения</span>
            </div>
            <h2 class="modal-title">{{ status.objectName }}</h2>
          </div>
          <button class="close-button" @click="isModalOpen = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="fluent-tabs">
            <button 
              class="tab-button" 
              :class="{ active: activeTab === 'details' }" 
              @click="activeTab = 'details'"
            >
              📊 Детализация этапа
            </button>
            <button 
              class="tab-button" 
              :class="{ active: activeTab === 'finance' }" 
              @click="activeTab = 'finance'"
            >
              💰 Финансовые показатели
            </button>
            <button 
              class="tab-button" 
              :class="{ active: activeTab === 'history' }" 
              @click="activeTab = 'history'"
            >
              🕒 История изменений
            </button>
          </div>

          <div class="tab-content">
            <div v-if="activeTab === 'details'" class="tab-pane">
              <div class="details-layout">
                <div class="details-main">
                  <div class="details-section">
                    <span class="section-title">Текущее состояние</span>
                    <div class="details-grid">
                      <div class="detail-item">
                        <span class="detail-label">Текущий этап контроля</span>
                        <span class="status-badge" :class="stageSlug" style="align-self: flex-start; margin-top: 4px;">
                          {{ status.stage }}
                        </span>
                      </div>
                      <div class="detail-item">
                        <span class="detail-label">Ответственный менеджер</span>
                        <span class="detail-value">{{ status.manager || 'Не назначен' }}</span>
                      </div>
                      <div class="detail-item">
                        <span class="detail-label">Последнее обновление</span>
                        <span class="detail-value">{{ status.updatedAt }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="details-section" style="margin-top: 20px;">
                    <span class="section-title">Дальнейшие шаги</span>
                    <div class="action-box">
                      <span class="action-box-title">Запланированное действие:</span>
                      <p class="action-box-text">{{ status.nextAction || 'Нет запланированных действий на ближайшее время.' }}</p>
                    </div>
                  </div>
                </div>

                <div class="details-sidebar">
                  <div class="kpi-card">
                    <span class="kpi-title">Прогресс выполнения</span>
                    <span class="kpi-value">{{ status.progress || '0%' }}</span>
                    <div class="fluent-progress-bar" style="margin-top: 12px;">
                      <div class="progress-fill" :style="{ width: status.progress || '0%' }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'finance'" class="tab-pane">
              <div class="finance-tab-layout">
                <div class="finance-kpi-grid">
                  <div class="kpi-mini-card limit">
                    <span class="kpi-mini-label">Общий лимит финансирования</span>
                    <span class="kpi-mini-value">{{ Number(status.budgetAllocation?.total || 0).toLocaleString('ru-RU') }} ₽</span>
                  </div>
                  <div class="kpi-mini-card spent">
                    <span class="kpi-mini-label">Фактически освоено</span>
                    <span class="kpi-mini-value">{{ Number(status.budgetAllocation?.spent || 0).toLocaleString('ru-RU') }} ₽</span>
                  </div>
                  <div class="kpi-mini-card remaining">
                    <span class="kpi-mini-label">Доступный остаток лимита</span>
                    <span class="kpi-mini-value">{{ Number(status.budgetAllocation?.remaining || 0).toLocaleString('ru-RU') }} ₽</span>
                  </div>
                </div>

                <div class="finance-analysis-section" style="margin-top: 24px;">
                  <span class="section-title">Анализ использования бюджета</span>
                  <div class="budget-bar-wrapper">
                    <div class="budget-bar-labels">
                      <span>Освоение бюджета (%)</span>
                      <span>{{ budgetPercent }}%</span>
                    </div>
                    <div class="fluent-progress-bar" style="height: 10px;">
                      <div class="progress-fill budget-fill" :style="{ width: `${budgetPercent}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'history'" class="tab-pane">
              <div class="history-timeline">
                <div v-if="status.historyLog && status.historyLog.length" class="timeline-wrapper">
                  <div v-for="(log, idx) in status.historyLog" :key="idx" class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                      <div class="timeline-header">
                        <span class="timeline-date">{{ log.date }}</span>
                        <span class="timeline-author">👤 {{ log.user || log.author || 'Система' }}</span>
                      </div>
                      <p class="timeline-text">{{ log.action || log.comment || log.title }}</p>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-history-state">
                  <span style="font-size: 24px;">📂</span>
                  <p>История изменений по данному объекту в системе отсутствует.</p>
                </div>
              </div>
            </div>
          </div>

        </div>

        <div class="modal-footer">
          <button class="fluent-button button-secondary" @click="isModalOpen = false">Закрыть окно</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Work } from '~/types/work'

const props = defineProps<{
  status: Work
}>()

const isModalOpen = ref(false)
const activeTab = ref<'details' | 'finance' | 'history'>('details')

const budgetPercent = computed(() => {
  const total = Number(props.status.budgetAllocation?.total || 0)
  const spent = Number(props.status.budgetAllocation?.spent || 0)
  if (!total) return 0
  const percent = Math.round((spent / total) * 100)
  return Math.min(percent, 100)
})

const stageSlug = computed(() => {
  switch (props.status.stage) {
    case 'Проверка объемов': return 'under-review'
    case 'Анализ отклонений': return 'deviation-analysis'
    case 'Приемка работ': return 'acceptance'
    case 'Завершено': return 'completed'
    default: return 'unknown'
  }
})
</script>

<style scoped>
.fluent-status-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.fluent-status-card:hover {
  border-color: #0078d4;
  box-shadow: 0 4px 12px rgba(0, 120, 212, 0.1);
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
  gap: 4px;
}
.badge-row {
  display: flex;
  gap: 6px;
  align-items: center;
}
.region-tag {
  font-size: 10px;
  background: #f3f2f1;
  color: #616161;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}
.deviation-tag {
  font-size: 10px;
  background: #fdf6f6;
  color: #a80000;
  border: 1px solid #fde7e9;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
}
.status-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #242424;
  line-height: 1.3;
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.status-badge.under-review { background: #fff4ce; color: #795b00; }
.status-badge.under-review .status-dot { background: #795b00; }

.status-badge.deviation-analysis { background: #fde7e9; color: #a80000; }
.status-badge.deviation-analysis .status-dot { background: #a80000; }

.status-badge.acceptance { background: #dff6dd; color: #107c41; }
.status-badge.acceptance .status-dot { background: #107c41; }

.status-badge.completed { background: #edebe9; color: #323130; }
.status-badge.completed .status-dot { background: #323130; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.info-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.fluent-icon {
  font-size: 14px;
}
.info-content {
  display: flex;
  flex-direction: column;
}
.info-label {
  font-size: 10px;
  color: #797979;
}
.info-value {
  font-size: 12px;
  color: #242424;
  font-weight: 500;
}

.card-divider {
  height: 1px;
  background: #f3f2f1;
  margin: 4px 0;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}
.section-subtitle {
  font-size: 11px;
  font-weight: 600;
  color: #797979;
}
.progress-percentage {
  font-weight: 600;
  color: #0078d4;
}
.fluent-progress-bar {
  height: 4px;
  background: #f3f2f1;
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #0078d4;
  border-radius: 2px;
}

.finance-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.finance-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.finance-item {
  display: flex;
  flex-direction: column;
  background: #fafafa;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}
.finance-label {
  font-size: 9px;
  color: #797979;
}
.finance-value {
  font-size: 11px;
  font-weight: 600;
}
.finance-value.limit { color: #242424; }
.finance-value.spent { color: #a80000; }
.finance-value.remaining { color: #107c41; }

.action-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.action-text {
  font-size: 11px;
  color: #616161;
  margin: 0;
}

.text-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fluent-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.fluent-modal-window {
  background: #ffffff;
  border-radius: 8px;
  width: 800px;
  max-width: 90%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.modal-badge-row {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}
.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #242424;
}
.close-button {
  background: transparent;
  border: none;
  font-size: 18px;
  color: #797979;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}
.close-button:hover {
  color: #242424;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.fluent-tabs {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #eaeaea;
  margin-bottom: 20px;
}
.tab-button {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #616161;
  cursor: pointer;
  transition: all 0.1s ease;
}
.tab-button:hover {
  color: #0078d4;
  border-bottom-color: #c7e0f4;
}
.tab-button.active {
  color: #0078d4;
  border-bottom-color: #0078d4;
}

.details-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}
.section-title {
  font-size: 12px;
  font-weight: 600;
  color: #797979;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  display: block;
  margin-bottom: 12px;
}
.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.detail-label {
  font-size: 11px;
  color: #797979;
}
.detail-value {
  font-size: 13px;
  font-weight: 600;
  color: #242424;
  background: #f3f2f1;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #edebe9;
}

.action-box {
  background: #fafafa;
  border: 1px dashed #d2d0ce;
  padding: 12px;
  border-radius: 6px;
}
.action-box-title {
  font-size: 12px;
  font-weight: 600;
  color: #0078d4;
  display: block;
  margin-bottom: 4px;
}
.action-box-text {
  font-size: 13px;
  color: #242424;
  margin: 0;
}

.kpi-card {
  background: #fcfcfc;
  border: 1px solid #eaeaea;
  border-radius: 6px;
  padding: 16px;
}
.kpi-title {
  font-size: 11px;
  font-weight: 600;
  color: #797979;
  display: block;
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #0078d4;
}

.finance-kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.kpi-mini-card {
  padding: 14px;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi-mini-card.limit { border-left: 4px solid #0078d4; background: #f9fbfd; }
.kpi-mini-card.spent { border-left: 4px solid #a80000; background: #fdf6f6; }
.kpi-mini-card.remaining { border-left: 4px solid #107c41; background: #f4faf6; }

.kpi-mini-label {
  font-size: 11px;
  color: #797979;
}
.kpi-mini-value {
  font-size: 18px;
  font-weight: 700;
  color: #242424;
}

.budget-bar-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #616161;
  margin-bottom: 6px;
}
.budget-fill {
  background: #107c41;
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.timeline-wrapper {
  position: relative;
  padding-left: 16px;
}
.timeline-wrapper::before {
  content: '';
  position: absolute;
  left: 4px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #eaeaea;
}
.timeline-item {
  position: relative;
  padding-bottom: 16px;
}
.timeline-item:last-child {
  padding-bottom: 0;
}
.timeline-dot {
  position: absolute;
  left: -16px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #0078d4;
  border: 2px solid #ffffff;
}
.timeline-content {
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  padding: 10px 12px;
}
.timeline-header {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #797979;
  margin-bottom: 4px;
}
.timeline-date {
  font-weight: 600;
}
.timeline-text {
  font-size: 13px;
  color: #242424;
  margin: 0;
}
.empty-history-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #797979;
  padding: 40px 0;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.fluent-button {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
}
.button-secondary {
  background: #ffffff;
  border: 1px solid #d6d9dc;
  color: #242424;
}
.button-secondary:hover {
  background: #f3f2f1;
}
</style>