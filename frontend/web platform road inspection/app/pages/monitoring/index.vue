<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Мониторинг объектов УДС</h2>
        <span class="objects-count">
          Найдено ОДХ: <strong>{{ filteredObjects.length }}</strong> из {{ objects.length }}
        </span>
      </div>

      <div class="toolbar-actions">
        <div class="fluent-pivot">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            class="pivot-item"
            :class="{ active: currentStatusFilter === tab.value }"
            @click="currentStatusFilter = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>

        <NuxtLink to="/monitoring/create" class="fluent-btn-primary">
          <span class="btn-icon">➕</span> Регистрация ОДХ
        </NuxtLink>
      </div>
    </div>

    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          class="fluent-input"
          placeholder="Поиск по наименованию, контракту или подрядчику..."
        />
      </div>

      <select v-model="regionFilter" class="fluent-select">
        <option value="all">Все административные округа</option>
        <option value="ЦАО">ЦАО (Центральный)</option>
        <option value="САО">САО (Северный)</option>
        <option value="ЮАО">ЮАО (Южный)</option>
        <option value="ЗАО">ЗАО (Западный)</option>
        <option value="ВАО">ВАО (Восточный)</option>
      </select>

      <select v-model="sourceFilter" class="fluent-select">
        <option value="all">Все источники данных</option>
        <option value="АСУ ПРИЗ">АСУ ПРИЗ</option>
        <option value="ЕАИСТ">ЕАИСТ</option>
        <option value="Ручной ввод">Локальный ввод</option>
      </select>
    </div>

    <div v-if="filteredObjects.length > 0" class="objects-grid">
      <ObjectCard
        v-for="obj in filteredObjects"
        :key="obj.id"
        :obj="obj"
      />
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">📂</div>
      <h3>Объекты не найдены</h3>
      <p>Попробуйте изменить параметры поиска или сбросить фильтры.</p>
      <button class="fluent-link-btn" @click="resetFilters">Сбросить все фильтры</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMockData } from '~/composables/useMockData'
import ObjectCard from '~/components/cards/object_card.vue'

const { objects } = useMockData()

const searchQuery = ref('')
const currentStatusFilter = ref('all')
const regionFilter = ref('all')
const sourceFilter = ref('all')

const statusTabs = [
  { label: 'Все ОДХ', value: 'all' },
  { label: 'Активные', value: 'Активный' },
  { label: 'На проверке', value: 'На проверке' },
  { label: 'В планировании', value: 'Планирование' },
  { label: 'Завершенные', value: 'Завершено' }
]

const filteredObjects = computed(() => {
  return objects.value.filter(obj => {
    const text = searchQuery.value.trim().toLowerCase()
    const matchesText = !text || 
      obj.title.toLowerCase().includes(text) ||
      obj.contractor.toLowerCase().includes(text) ||
      obj.contractNumber.toLowerCase().includes(text)

    const matchesStatus = currentStatusFilter.value === 'all' || obj.status === currentStatusFilter.value

    const matchesRegion = regionFilter.value === 'all' || obj.region === regionFilter.value

    const matchesSource = sourceFilter.value === 'all' || obj.source === sourceFilter.value

    return matchesText && matchesStatus && matchesRegion && matchesSource
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  currentStatusFilter.value = 'all'
  regionFilter.value = 'all'
  sourceFilter.value = 'all'
}
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #242424;
}

.objects-count {
  font-size: 12px;
  color: #616161;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.fluent-pivot {
  display: flex;
  gap: 8px;
}

.pivot-item {
  background: none;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  color: #616161;
  cursor: pointer;
  border-radius: 4px;
  position: relative;
  transition: all 0.15s ease;
}

.pivot-item:hover {
  background: #f3f3f3;
  color: #242424;
}

.pivot-item.active {
  color: #0078d4;
  font-weight: 600;
}

.pivot-item.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #0078d4;
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
</style>