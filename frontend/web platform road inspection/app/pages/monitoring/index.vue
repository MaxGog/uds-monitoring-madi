<template>
  <div class="admin-page-layout">
    <!-- Системный PageToolbar с табами на основе TypeScript Enum -->
    <PageToolbar
      title="🛣️ Мониторинг объектов УДС"
      :countText="`Найдено ОДХ: ${filteredObjects.length} из ${objects.length}`"
      :tabs="statusTabs"
      :activeTab="currentStatusFilter"
      @update:activeTab="value => currentStatusFilter = value"
    >
      <template #actions>
        <NuxtLink to="/monitoring/create" class="fluent-button button-primary">
          <span class="plus-icon">＋</span> Регистрация ОДХ
        </NuxtLink>
      </template>
    </PageToolbar>

    <!-- Системный FilterBar -->
    <FilterBar>
      <SearchBar
        v-model="searchQuery"
        placeholder="Поиск по наименованию или адресу..."
      />

      <!-- Фильтр по округам -->
      <select v-model="regionFilter" class="fluent-select">
        <option value="all">Все административные округа</option>
        <option v-for="district in districts" :key="district" :value="district">
          {{ district }}
        </option>
      </select>

      <!-- Фильтр по генподрядчикам из БД -->
      <select v-model="contractorFilter" class="fluent-select" :disabled="isCompaniesLoading">
        <option value="all">Все подрядчики</option>
        <option v-for="company in companies" :key="company.id" :value="company.id">
          {{ company.name }}
        </option>
      </select>
    </FilterBar>

    <!-- Сетка объектов -->
    <div v-if="filteredObjects.length > 0" class="objects-grid">
      <ObjectCard
        v-for="obj in filteredObjects"
        :key="obj.id"
        :obj="obj"
      />
    </div>

    <!-- Системный EmptyState -->
    <EmptyState
      v-else
      icon="📂"
      title="Объекты не найдены"
      description="Попробуйте изменить параметры поиска или сбросить фильтры."
      buttonText="Сбросить фильтры"
      @action="resetFilters"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useObject } from '~/composables/useObjects'
import { ObjectStatus } from '~/types/enums'
import ObjectCard from '~/components/cards/object_card.vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import SearchBar from '~/components/search_bar.vue'

const { objects, fetchObjects } = useObject()

const searchQuery = ref('')
const currentStatusFilter = ref('all')
const regionFilter = ref('all')
const contractorFilter = ref('all')

const districts = ['ЦАО', 'САО', 'ЮАО', 'ЗАО', 'ВАО', 'СЗАО', 'СВАО', 'ЮВАО', 'ЮЗАО']

// Список статусов на основе системного Enum
const statusTabs = [
  { label: 'Все ОДХ', value: 'all' },
  { label: 'В процессе', value: ObjectStatus.IN_PROGRESS },
  { label: 'Приняты', value: ObjectStatus.ACCEPTED },
  { label: 'Ожидают', value: ObjectStatus.PENDING },
  { label: 'Приостановлены', value: ObjectStatus.PAUSED },
  { label: 'Завершены', value: ObjectStatus.COMPLETED }
]

// Подгружаем компании для фильтрации
const companies = ref<any[]>([])
const isCompaniesLoading = ref(false)

const fetchCompanies = async () => {
  isCompaniesLoading.value = true
  try {
    const response = await apiFetch<{ data: any[] }>('/company/', { method: 'GET' })
    companies.value = response.data || []
  } catch (err) {
    console.error('Ошибка загрузки компаний для фильтра:', err)
  } finally {
    isCompaniesLoading.value = false
  }
}

onMounted(() => {
  fetchObjects()
  fetchCompanies()
})

const filteredObjects = computed(() => {
  return objects.value.filter(obj => {
    const text = searchQuery.value.trim().toLowerCase()
    const matchesText = !text || 
      (obj.title && obj.title.toLowerCase().includes(text)) ||
      (obj.address && obj.address.toLowerCase().includes(text))

    const matchesStatus = currentStatusFilter.value === 'all' || obj.status === currentStatusFilter.value
    const matchesRegion = regionFilter.value === 'all' || obj.district === regionFilter.value
    const matchesContractor = contractorFilter.value === 'all' || obj.contractor_id === Number(contractorFilter.value)

    return matchesText && matchesStatus && matchesRegion && matchesContractor
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  currentStatusFilter.value = 'all'
  regionFilter.value = 'all'
  contractorFilter.value = 'all'
}
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.fluent-btn-primary {
  background: #0078d4;
  border: 1px solid #0078d4;
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 4px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.fluent-btn-primary:hover {
  background: #106ebe;
  border-color: #106ebe;
}

.filter-bar {
  display: flex;
  gap: 12px;
  background: #ffffff;
  padding: 12px 24px;
  border: 1px solid #e1e3e8;
  border-radius: 4px;
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
  padding: 6px 12px;
  font-size: 13px;
  color: #242424;
  background: #ffffff;
  outline: none;
}

.fluent-input:focus,
.fluent-select:focus {
  border-color: #0078d4;
  box-shadow: 0 0 0 1px #0078d4;
}

.fluent-select {
  min-width: 220px;
  cursor: pointer;
}

.objects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 48px;
  background: #ffffff;
  border: 1px dashed #c8c9cc;
  border-radius: 4px;
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

.admin-page-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.objects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.fluent-button {
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.button-primary {
  background: #0078d4;
  border: 1px solid #0078d4;
  color: #ffffff;
}

.button-primary:hover {
  background: #106ebe;
}
</style>