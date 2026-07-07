<template>
  <div class="acts-page">
    <PageToolbar
      title="Работа с актами"
      :countText="`Всего: ${acts.length} (Подписано: ${signedCount}, Ожидает: ${pendingCount})`"
      :tabs="statusTabs"
      :activeTab="statusFilter"
      @update:activeTab="value => statusFilter = value"
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
        placeholder="Поиск по объекту, номеру или подрядчику..."
      />
      
      <select v-model="typeFilter" class="fluent-select type-select">
        <option value="all">Все типы актов</option>
        <option v-for="type in types" :key="type" :value="type">
          {{ type }}
        </option>
      </select>
    </FilterBar>

    <div v-if="filteredActs.length > 0" class="acts-grid">
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
import { ref, computed } from 'vue'
import { useMockData } from '~/composables/useMockData'
import ActCard from '~/components/cards/act_card.vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'

const { acts, types } = useMockData()

const search = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')

const statusTabs = [
  { label: 'Все', value: 'all' },
  { label: 'На утверждении', value: 'На утверждении' },
  { label: 'Ожидает подписи', value: 'Ожидает подписи' },
  { label: 'Подписан', value: 'Подписан' }
]

const filteredActs = computed(() => {
  return acts.value.filter(act => {
    const text = search.value.toLowerCase().trim()
    const matchesText = !text || 
      act.objectName.toLowerCase().includes(text) ||
      act.number.toLowerCase().includes(text) ||
      act.contractor.toLowerCase().includes(text)

    const matchesStatus = statusFilter.value === 'all' || act.status === statusFilter.value
    const matchesType = typeFilter.value === 'all' || act.type === typeFilter.value

    return matchesText && matchesStatus && matchesType
  })
})

const signedCount = computed(() => acts.value.filter(act => act.status === 'Подписан').length)
const pendingCount = computed(() => acts.value.filter(act => act.status !== 'Подписан').length)
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

.filter-bar {
  display: flex;
  gap: 12px;
  background: #ffffff;
  padding: 12px 24px;
  border: 1px solid #e1e3e8;
  border-radius: 4px;
}


.search-input {
  flex: 1;
  min-width: 200px;
}

.type-select {
  width: 260px;
}

.fluent-input,
.fluent-select {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  background: #ffffff;
}

.fluent-input:focus,
.fluent-select:focus {
  border-color: #0078d4;
  outline: none;
}

.acts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  background: #ffffff;
  border: 1px dashed #d2d0ce;
  border-radius: 8px;
  color: #616161;
}
</style>