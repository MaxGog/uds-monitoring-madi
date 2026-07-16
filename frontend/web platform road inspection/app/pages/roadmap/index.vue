<template>
  <div class="roadmap-page-layout">
    <PageToolbar
      title="Формирование Дорожных Карт (ДК)"
      :countText="countText"
    >
      <template #actions>
        <button class="fluent-add-button" @click="openCreateModal">
          <span class="plus-icon">＋</span> Создать Дорожную Карту
        </button>
      </template>
    </PageToolbar>

    <FilterBar>
      <SearchBar
        v-model="search"
        placeholder="Поиск по проекту или куратору..."
      />

      <select v-model="regionFilter" class="fluent-select">
        <option value="all">Все округа</option>
        <option v-for="reg in uniqueRegions" :key="reg" :value="reg">{{ reg }}</option>
      </select>

      <select v-model="riskFilter" class="fluent-select">
        <option value="all">Все уровни риска</option>
        <option value="Низкий">Низкий риск</option>
        <option value="Средний">Средний риск</option>
        <option value="Высокий">Высокий риск</option>
      </select>
    </FilterBar>

    <div v-if="filteredRoadmapItems.length" class="roadmap-grid">
      <div
        v-for="item in filteredRoadmapItems"
        :key="item.id"
        class="fluent-roadmap-card"
        :class="`risk-${getRiskSlug(item.risk)}`"
      >
        <div class="card-header">
          <div class="header-meta">
            <span class="region-tag">{{ item.region }}</span>
            <span class="phase-tag">{{ item.phase }}</span>
          </div>
          <span class="risk-badge" :class="getRiskSlug(item.risk)">
            <span class="status-dot"></span> {{ item.risk }} риск
          </span>
        </div>

        <h3 class="project-title">{{ item.title }}</h3>

        <div class="project-details">
          <div class="detail-item">
            <span class="detail-label">Период реализации</span>
            <span class="detail-value">📅 {{ item.startDate }} – {{ item.endDate }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Плановый бюджет</span>
            <span class="detail-value">💰 {{ item.budget }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Куратор ОДХ</span>
            <span class="detail-value">👤 {{ item.manager }}</span>
          </div>
        </div>

        <div class="progress-section">
          <div class="progress-header">
            <span class="progress-label">Выполнение графика работ</span>
            <span class="progress-percent">{{ item.progressPercentage }}%</span>
          </div>
          <div class="fluent-progress-bar">
            <div class="progress-track" :style="{ width: item.progressPercentage + '%' }"></div>
          </div>
        </div>

        <div v-if="item.riskDescription" class="risk-description-box" :class="getRiskSlug(item.risk)">
          <strong>Факторы риска:</strong> {{ item.riskDescription }}
        </div>
      </div>
    </div>

    <EmptyState
      v-else
      icon="🗺️"
      title="Дорожные карты не найдены"
      description="Попробуйте скорректировать поисковый запрос или фильтры по округам."
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, type Ref } from 'vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'

const { roadmaps, isLoading, fetchRoadmaps } = useRoadmap()

const search = ref('')
const regionFilter = ref('all')
const riskFilter = ref('all')

onMounted(async () => {
  await fetchRoadmaps()
})

const uniqueRegions = computed(() => {
  const regions = roadmaps.value.map(item => item.region).filter(Boolean)
  return [...new Set(regions)]
})

const countText = computed(() => {
  return `Всего дорожных карт: ${roadmaps.value.length} (Найдено: ${filteredRoadmapItems.value.length})`
})

const filteredRoadmapItems = computed(() => {
  return roadmaps.value.filter(item => {
    const matchesSearch = 
      item.title.toLowerCase().includes(search.value.toLowerCase()) ||
      (item.responsibleManager && item.responsibleManager.toLowerCase().includes(search.value.toLowerCase())) ||
      (item.manager && item.manager.toLowerCase().includes(search.value.toLowerCase()))

    const matchesRegion = regionFilter.value === 'all' || item.region === regionFilter.value
    const matchesRisk = riskFilter.value === 'all' || item.risk === riskFilter.value

    return matchesSearch && matchesRegion && matchesRisk
  })
})

const getRiskSlug = (risk: string) => {
  if (risk === 'Высокий') return 'high'
  if (risk === 'Средний') return 'medium'
  return 'low'
}

const openCreateModal = () => {
  console.log('Открытие модального окна создания ДК')
}
</script>

<style scoped>
.roadmap-page-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
  font-family: var(--fluent-font, Segoe UI, -apple-system, sans-serif);
}

.fluent-add-button {
  background: #0078d4;
  color: #ffffff;
  border: 1px solid #0078d4;
  border-radius: 4px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.1s;
}

.fluent-add-button:hover {
  background: #106ebe;
}

.fluent-select {
  min-width: 220px;
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  background: #ffffff;
  outline: none;
  cursor: pointer;
}

.fluent-select:focus {
  border-color: #0078d4;
}

.roadmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
}

.fluent-roadmap-card {
  background: #ffffff;
  border: 1px solid #edebe9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 14px;
  border-left: 4px solid #edebe9;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.fluent-roadmap-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.fluent-roadmap-card.risk-high { border-left-color: #d83b01; }
.fluent-roadmap-card.risk-medium { border-left-color: #ffaa44; }
.fluent-roadmap-card.risk-low { border-left-color: #107c41; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-meta {
  display: flex;
  gap: 6px;
}

.region-tag {
  background: #f3f2f1;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
  color: #323130;
}

.phase-tag {
  background: #e1dfdd;
  padding: 3px 8px;
  font-size: 11px;
  border-radius: 4px;
  color: #201f1e;
}

.project-title {
  font-size: 18px;
  margin: 0;
}

.project-details {
  display: grid;
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}

.detail-label {
  color: #616161;
}

.detail-value {
  font-weight: 600;
}

.progress-section {
  display: grid;
  gap: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #242424;
  font-size: 13px;
}

.fluent-progress-bar {
  height: 10px;
  background: #e6f0fb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-track {
  height: 100%;
  background: linear-gradient(90deg, #107c41 0%, #2563eb 100%);
}

.risk-description-box {
  padding: 14px 16px;
  border-radius: 10px;
  background: #f8faf8;
  color: #1f2937;
  font-size: 13px;
}

.risk-high.risk-description-box {
  background: #fff1f0;
}

.risk-medium.risk-description-box {
  background: #fff7ed;
}

.risk-low.risk-description-box {
  background: #ecfdf5;
}

/* Бейджи Рисков */
.risk-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.risk-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.risk-badge.high { background: #fde7e9; color: #a80000; }
.risk-badge.high .status-dot { background: #d83b01; }
.risk-badge.medium { background: #fff4ce; color: #7a5c00; }
.risk-badge.medium .status-dot { background: #ffaa44; }
.risk-badge.low { background: #dff6dd; color: #107c41; }
.risk-badge.low .status-dot { background: #107c41; }

.project-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: #242424;
  line-height: 1.4;
}

/* Детали */
.project-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  background: #fafafa;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #f3f2f1;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.detail-item:style {
  grid-column: span 2;
}
.detail-label {
  font-size: 11px;
  color: #797979;
}
.detail-value {
  font-size: 13px;
  font-weight: 500;
  color: #242424;
}

/* Шкала Прогресса */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.progress-label { color: #616161; }
.progress-percent { font-weight: 600; color: #0078d4; }
.fluent-progress-bar {
  height: 6px;
  background: #f3f2f1;
  border-radius: 3px;
  overflow: hidden;
}
.progress-track {
  height: 100%;
  background-color: #0078d4;
  border-radius: 3px;
}

/* Блок описания проблемных рисков */
.risk-description-box {
  font-size: 12px;
  padding: 10px;
  border-radius: 4px;
  line-height: 1.4;
}
.risk-description-box.high { background: #fdf3f4; border-left: 3px solid #d83b01; color: #a80000; }
.risk-description-box.medium { background: #fffdf5; border-left: 3px solid #ffaa44; color: #5f4500; }
.risk-description-box.low { background: #f9fef9; border-left: 3px solid #107c41; color: #0b532b; }

/* Пустые состояния */
.empty-state {
  text-align: center;
  padding: 50px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px dashed #c5c9d1;
  color: #616161;
}
.empty-icon { font-size: 32px; margin-bottom: 8px; }
</style>