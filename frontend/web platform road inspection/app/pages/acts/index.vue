<template>
  <div class="acts-page">
    <PageToolbar
      title="Работа с актами"
      :countText="`Всего: ${acts.length} (Утверждено: ${approvedCount}, В обработке: ${pendingCount})`"
      :tabs="statusTabs"
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
import type { ActStatus } from '~/types/act'
import ActCard from '~/components/cards/act_card.vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'


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
</style>