<template>
  <div class="acts-page">
    <PageToolbar
      title="Работа с актами"
      :countText="`Всего: ${acts.length} (Утверждено: ${approvedCount}, В обработке: ${pendingCount})`"
      :activeTab="statusFilter"
      @update:activeTab="(value: string) => statusFilter = value"
    >
      <template #actions>
        <NuxtLink to="/acts/create" class="fluent-add-button">
          <span class="plus-icon">＋</span> Создать Акт
        </NuxtLink>
      </template>
    </PageToolbar>

    <FilterBar>
      <SearchBar
        v-model="search"
        placeholder="Поиск по наименованию, объекту или подрядчику..."
      />
      <select v-model="typeFilter" class="fluent-select type-select">
        <option value="all">Все типы актов</option>
        <option value="contractor">Подрядный (contractor)</option>
        <option value="supervisory">Технадзор (supervisory)</option>
      </select>
    </FilterBar>

    <!-- Блок круговых диаграмм -->
    <div class="charts-grid">
      <DonutChart
        title="Статусы актов"
        :items="acts"
        key="status"
        :colors="['#6752f5', '#48d6d2', '#ffc247', '#34c978']"
      />
      <DonutChart
        title="Типы актов"
        :items="acts"
        key="type"
        :colors="['#6752f5', '#48d6d2']"
      />
      <DonutChart
        title="Объекты (топ-5)"
        :items="acts"
        key="metadata_fields.objectName"
        :colors="['#6752f5', '#48d6d2', '#34c978', '#ffc247', '#ff5b66']"
      />
      <DonutChart
        title="Месяцы подписания"
        :items="actsWithMonth"
        key="month"
        :colors="['#6752f5', '#48d6d2', '#34c978', '#ffc247', '#ff5b66', '#8a6cff']"
      />
    </div>

    <!-- Список актов -->
    <div v-if="isLoading" class="loading-state">
      Загрузка актов...
    </div>

    <div v-else-if="filteredActs.length > 0" class="acts-grid">
      <ActCard
        v-for="act in filteredActs"
        :key="act.id"
        :act="act"
      />
    </div>

    <EmptyState
      v-else
      title="Записи не найдены"
      description="Ничего не подошло под текущие фильтры. Попробуйте изменить запрос или тип акта."
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useActs } from '~/composables/useActs'
import type { ActStatus } from '~/types/enums'
import ActCard from '~/components/cards/act_card.vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'
import DonutChart from '~/components/donut_chart.vue'

const { acts, isLoading, fetchActs } = useActs()

onMounted(() => {
  fetchActs()
})

const search = ref('')
const statusFilter = ref<string>('all')
const typeFilter = ref<string>('all')

const statusTabs = [
  { id: 'all', label: 'Все акты' },
  { id: 'draft', label: 'Черновики' },
  { id: 'pending', label: 'На рассмотрении' },
  { id: 'approved', label: 'Утверждены' },
  { id: 'completed', label: 'Завершены' }
]

// Вычисляемое поле для группировки по месяцам подписания
const actsWithMonth = computed(() => {
  return acts.value.map(act => {
    let month = 'Не указан'
    if (act.date_signed) {
      try {
        const date = new Date(act.date_signed)
        if (!isNaN(date.getTime())) {
          month = date.toLocaleString('default', { month: 'long', year: 'numeric' })
        }
      } catch {
        // ignore
      }
    }
    return {
      ...act,
      month
    }
  })
})

const filteredActs = computed(() => {
  return acts.value.filter(act => {
    const objectName = act.metadata_fields?.objectName || ''
    const contractor = act.metadata_fields?.contractor || ''
    const actName = act.name || ''

    const searchLower = search.value.toLowerCase()
    const matchesSearch = !search.value ||
      actName.toLowerCase().includes(searchLower) ||
      objectName.toLowerCase().includes(searchLower) ||
      contractor.toLowerCase().includes(searchLower)

    const matchesStatus = statusFilter.value === 'all' || act.status === statusFilter.value
    const matchesType = typeFilter.value === 'all' || act.type === typeFilter.value

    return matchesSearch && matchesStatus && matchesType
  })
})

const approvedCount = computed(() => acts.value.filter(act => act.status === 'approved' || act.status === 'completed').length)
const pendingCount = computed(() => acts.value.filter(act => act.status === 'pending' || act.status === 'draft').length)
</script>


<style scoped>
.acts-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.fluent-add-button {
  background: #0078d4;
  color: #ffffff;
  border: 1px solid #0078d4;
  border-radius: 4px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.1s;
}

.fluent-add-button:hover {
  background: #106ebe;
  border-color: #106ebe;
}

.plus-icon {
  font-size: 12px;
  font-weight: bold;
}

.type-select {
  min-width: 180px;
}

.acts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}

.loading-state {
  padding: 32px;
  text-align: center;
  color: #605e5c;
  font-size: 14px;
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
</style>