<template>
  <div class="work-statuses-page">
    <PageToolbar
      title="Статусы работ"
      :countText="`Всего объектов: ${workStatuses.length} (Найдено: ${filteredWorkStatuses.length})`"
      :tabs="[]"
    >
      <template #actions>
        <NuxtLink to="/work-statuses/create" class="fluent-button button-primary">
          ➕ Инициализировать статус
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
import { computed, ref } from 'vue'
import WorkStatusCard from '~/components/cards/work_status_card.vue'
import { useMockData } from '~/composables/useMockData'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'

const { workStatuses } = useMockData()
const search = ref('')
const stageFilter = ref('all')

const stages = computed(() => {
  return [...new Set(workStatuses.value.map(item => item.stage))]
})

const filteredWorkStatuses = computed(() => {
  return workStatuses.value.filter(status => {
    const term = search.value.trim().toLowerCase()
    const matchesText = !term || [status.objectName, status.manager, status.nextAction]
      .some(field => field.toLowerCase().includes(term))

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

.search-box {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  font-size: 14px;
  color: #797979;
}

.search-box .fluent-input {
  padding-left: 32px;
  width: 100%;
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

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 48px;
  background: #ffffff;
  border: 1px dashed #c8c9cc;
  border-radius: 8px;
  color: #616161;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-state h3 {
  margin: 0 0 4px 0;
  color: #242424;
}

.empty-state p {
  margin: 0 0 12px 0;
  font-size: 13px;
}

.fluent-link-btn {
  background: none;
  border: none;
  color: #0078d4;
  font-weight: 600;
  cursor: pointer;
  font-size: 13px;
  text-decoration: underline;
}
</style>