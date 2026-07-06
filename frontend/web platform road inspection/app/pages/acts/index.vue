<template>
  <div class="acts-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Работа с актами</h2>
        <span class="objects-count">
          Всего: {{ acts.length }} (Подписано: {{ signedCount }}, Ожидает: {{ pendingCount }})
        </span>
      </div>

      <div class="toolbar-actions">
        <div class="fluent-pivot">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            class="pivot-item"
            :class="{ active: statusFilter === tab.value }"
            @click="statusFilter = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>

        <NuxtLink to="/acts/create" class="fluent-add-button">
          <span class="plus-icon">＋</span> Создать Акт
        </NuxtLink>
      </div>
    </div>

    <div class="filter-bar">
      <input
        v-model="search"
        class="fluent-input search-input"
        placeholder="Поиск по объекту, номеру или подрядчику..."
      />
      
      <select v-model="typeFilter" class="fluent-select type-select">
        <option value="all">Все типы актов</option>
        <option v-for="type in types" :key="type" :value="type">
          {{ type }}
        </option>
      </select>
    </div>

    <div v-if="filteredActs.length > 0" class="acts-grid">
      <ActCard
        v-for="act in filteredActs"
        :key="act.id"
        :act="act"
      />
    </div>

    <div v-else class="empty-state">
      <p>Записи, удовлетворяющие критериям фильтрации, не найдены.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMockData } from '~/composables/useMockData'
import ActCard from '~/components/cards/act_card.vue'

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

.toolbar-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
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
  gap: 16px;
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
  bottom: -5px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #0078d4;
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
  gap: 16px;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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