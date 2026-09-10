<template>
  <div class="fluent-act-card" :class="`status-${act.status}`">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="act-type">{{ displayType }}</span>
          <span v-if="region" class="region-tag">{{ region }}</span>
        </div>
        <h3 class="act-title">{{ act.name || `Акт № ${act.id}` }}</h3>
      </div>
      <span class="status-badge" :class="act.status">
        <span class="status-dot"></span>
        {{ displayStatus }}
      </span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="fluent-icon">🏢</span>
        <div class="info-content">
          <span class="info-label">Объект (ОДХ)</span>
          <span class="info-value text-ellipsis" :title="objectName">{{ objectName }}</span>
        </div>
      </div>

      <div class="info-row">
        <span class="fluent-icon">🤝</span>
        <div class="info-content">
          <span class="info-label">Подрядчик / Контракт</span>
          <span class="info-value text-ellipsis" :title="contractor">
            {{ contractor }} <template v-if="contractNumber">({{ contractNumber }})</template>
          </span>
        </div>
      </div>

      <div class="info-row" v-if="act.date_signed">
        <span class="fluent-icon">📅</span>
        <div class="info-content">
          <span class="info-label">Дата подписания</span>
          <span class="info-value">{{ act.date_signed }}</span>
        </div>
      </div>

      <div class="divider"></div>

      <div class="total-row">
        <span class="total-label">Плановая сумма:</span>
        <span class="total-amount">{{ planAmount }} ₽</span>
      </div>
    </div>

    <div class="card-expandable">
      <button class="expand-toggle" @click="isExpanded = !isExpanded">
        <span>{{ isExpanded ? 'Скрыть объёмы работ' : 'Показать объёмы работ' }}</span>
        <span class="chevron" :class="{ open: isExpanded }">❯</span>
      </button>

      <div v-if="isExpanded" class="expand-content">
        <div v-if="notes" class="notes-box">
          <strong>Примечание:</strong> {{ notes }}
        </div>

        <div v-if="volumes.length > 0" class="volumes-table-wrapper">
          <table class="volumes-table">
            <thead>
              <tr>
                <th>Наименование</th>
                <th class="text-right">План</th>
                <th class="text-right">Факт</th>
                <th>Ед.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(v, i) in volumes" :key="i">
                <td>{{ v.name }}</td>
                <td class="text-right">{{ v.plan }}</td>
                <td class="text-right font-bold">{{ v.fact }}</td>
                <td>{{ v.unit }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-volumes">
          Объёмы работ не указаны
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Act } from '~/types/act'

const props = defineProps<{
  act: Act
}>()

const isExpanded = ref(false)

const metadata = computed(() => props.act.metadata_fields || {})
const objectName = computed(() => metadata.value.objectName || 'Не указан')
const contractor = computed(() => metadata.value.contractor || 'Не указан')
const contractNumber = computed(() => metadata.value.contractNumber || '')
const region = computed(() => metadata.value.region || '')
const planAmount = computed(() => metadata.value.planAmount || '0.00')
const notes = computed(() => metadata.value.notes || '')
const volumes = computed(() => metadata.value.volumes || [])

const displayType = computed(() => {
  switch (props.act.type) {
    case 'contractor': return 'Подрядный'
    case 'supervisory': return 'Технадзор'
    default: return props.act.type || 'Акт'
  }
})

const displayStatus = computed(() => {
  switch (props.act.status) {
    case 'draft': return 'Черновик'
    case 'pending': return 'На рассмотрении'
    case 'approved': return 'Утверждён'
    case 'completed': return 'Завершён'
    default: return props.act.status
  }
})
</script>

<style scoped>
.fluent-act-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s, border-color 0.2s;
  overflow: hidden;
}

.fluent-act-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #c8cacc;
}

.card-header {
  padding: 16px;
  background: #faf9f8;
  border-bottom: 1px solid #edebe9;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.badge-row {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
}

.act-type {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: #eff6fc;
  color: #005a9e;
  padding: 2px 6px;
  border-radius: 3px;
}

.region-tag {
  font-size: 11px;
  font-weight: 600;
  background: #f3f2f1;
  color: #605e5c;
  padding: 2px 6px;
  border-radius: 3px;
}

.act-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #323130;
}

/* Статусы */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 12px;
  white-space: nowrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.draft { background: #f3f2f1; color: #605e5c; }
.status-badge.draft .status-dot { background: #8a8886; }

.status-badge.pending { background: #fff4ce; color: #797673; }
.status-badge.pending .status-dot { background: #797673; }

.status-badge.approved { background: #dff6dd; color: #107c41; }
.status-badge.approved .status-dot { background: #107c41; }

.status-badge.completed { background: #e1dfdd; color: #323130; }
.status-badge.completed .status-dot { background: #323130; }

.card-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-grow: 1;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.fluent-icon {
  font-size: 14px;
  line-height: 1.4;
}

.info-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.info-label {
  font-size: 11px;
  color: #8a8886;
}

.info-value {
  font-size: 13px;
  color: #323130;
  font-weight: 500;
}

.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.divider {
  height: 1px;
  background: #edebe9;
  margin: 4px 0;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-label {
  font-size: 12px;
  color: #605e5c;
}

.total-amount {
  font-size: 15px;
  font-weight: 700;
  color: #0078d4;
}

/* Разворачиваемая секция */
.card-expandable {
  border-top: 1px solid #edebe9;
  background: #faf9f8;
}

.expand-toggle {
  width: 100%;
  padding: 10px 16px;
  background: none;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #0078d4;
  font-weight: 500;
  cursor: pointer;
}

.expand-toggle:hover {
  background: #f3f2f1;
}

.chevron {
  transition: transform 0.2s;
  font-size: 10px;
}

.chevron.open {
  transform: rotate(90deg);
}

.expand-content {
  padding: 0 16px 16px 16px;
}

.notes-box {
  background: #fffdf5;
  border: 1px solid #ffeab2;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  color: #5d461a;
  margin-bottom: 10px;
}

.volumes-table-wrapper {
  border: 1px solid #edebe9;
  border-radius: 4px;
  background: #ffffff;
  overflow: hidden;
}

.volumes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.volumes-table th {
  background: #f3f2f1;
  padding: 6px 8px;
  text-align: left;
  font-weight: 600;
  color: #605e5c;
}

.volumes-table td {
  padding: 6px 8px;
  border-top: 1px solid #edebe9;
  color: #323130;
}

.text-right { text-align: right; }
.font-bold { font-weight: 600; }

.no-volumes {
  font-size: 12px;
  color: #8a8886;
  text-align: center;
  padding: 8px;
}
</style>