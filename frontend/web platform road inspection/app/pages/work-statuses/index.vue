<template>
  <div class="work-statuses-page">
    <PageToolbar
      title="Статусы работ"
      :countText="`Всего объектов: ${works.length} (Найдено: ${filteredWorkStatuses.length})`"
      :tabs="[]"
    >
      <template #actions>
        <NuxtLink to="/work-statuses/create" class="fluent-button button-primary">
          <span class="plus-icon">＋</span> Инициализировать статус
        </NuxtLink>
      </template>
    </PageToolbar>

    <FilterBar>
      <SearchBar
        v-model="search"
        placeholder="Поиск по объекту или менеджеру..."
      />
      <select v-model="stageFilter" class="fluent-select">
        <option value="all">Все этапы</option>
        <option v-for="stage in stages" :key="stage" :value="stage">
          {{ stage }}
        </option>
      </select>
    </FilterBar>

    <!-- Блок круговых диаграмм -->
    <div class="charts-grid">
      <DonutChart
        title="Этапы работ"
        :items="works"
        key="stage"
        :colors="['#6752f5', '#48d6d2', '#ffc247', '#34c978', '#ff5b66']"
      />
      <DonutChart
        title="Менеджеры (топ-5)"
        :items="works"
        key="manager"
        :colors="['#6752f5', '#48d6d2', '#34c978', '#ffc247', '#ff5b66']"
      />
      <DonutChart
        title="Округа"
        :items="works"
        key="region"
        :colors="['#6752f5', '#48d6d2', '#34c978', '#ffc247', '#ff5b66', '#8a6cff']"
      />
      <DonutChart
        title="Наличие отклонений"
        :items="works"
        key="hasDeviationAlert"
        :colors="['#6752f5', '#ff5b66']"
      />
    </div>

    <div v-if="filteredWorkStatuses.length" class="status-grid">
      <WorkStatusCard
        v-for="status in filteredWorkStatuses"
        :key="status.id"
        :status="status"
      />
    </div>

    <EmptyState
      v-else
      icon="📂"
      title="Записи не найдены"
      description="Попробуйте изменить параметры поиска или сбросить фильтры."
      buttonText="Сбросить фильтры"
      @action="resetFilters"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import WorkStatusCard from '~/components/cards/work_status_card.vue'
import { useWork } from '~/composables/useWork'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'
import DonutChart from '~/components/donut_chart.vue'

const { works, isLoading, error, fetchWorks } = useWork()
const search = ref('')
const stageFilter = ref('all')

const stages = computed(() => {
  return [...new Set(works.value.map(item => item.stage))]
})

onMounted(async () => {
  await fetchWorks()
})

const filteredWorkStatuses = computed(() => {
  return works.value.filter(status => {
    const term = search.value.trim().toLowerCase()
    const matchesText = !term || [status.objectName, status.manager, status.nextAction]
      .some(field => field && field.toLowerCase().includes(term))

    const matchesStage = stageFilter.value === 'all' || status.stage === stageFilter.value
    return matchesText && matchesStage
  })
})

const resetFilters = () => {
  search.value = ''
  stageFilter.value = 'all'
}
</script>

<style scoped>
.work-statuses-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #242424;
}

.fluent-button {
  padding: 6px 18px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.1s, border-color 0.1s;
}

.button-primary {
  background: #0078d4;
  border: 1px solid #0078d4;
  color: #ffffff;
}

.button-primary:hover {
  background: #106ebe;
  border-color: #106ebe;
}

.filter-bar {
  display: flex;
  gap: 16px;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.fluent-input,
.fluent-select {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  color: #242424;
  background: #ffffff;
  outline: none;
}

.fluent-input:focus,
.fluent-select:focus {
  border-color: #0078d4;
}

.fluent-select {
  width: 260px;
  cursor: pointer;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 4px;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

/* стили для EmptyState уже есть в компоненте */
</style>