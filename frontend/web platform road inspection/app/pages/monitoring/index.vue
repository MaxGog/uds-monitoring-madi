<template>
  <div class="monitoring-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Мониторинг объектов УДС</h2>
        <span class="objects-count">Всего: {{ filteredObjects.length }}</span>
      </div>
      
      <div class="toolbar-actions">
        <div class="fluent-pivot">
          <button 
            v-for="tab in tabs" 
            :key="tab.value"
            class="pivot-item"
            :class="{ active: currentTab === tab.value }"
            @click="currentTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="filteredObjects.length > 0" class="objects-grid">
      <ObjectCard
        v-for="obj in filteredObjects"
        :key="obj.id"
        :title="obj.title"
        :region="obj.region"
        :status="obj.status"
        :contractor="obj.contractor"
        :executor="obj.executor"
        :status-properties="obj.statusProperties"
      />
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>Объекты не найдены</h3>
      <p>Попробуйте изменить параметры фильтрации.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ObjectCard from '~/components/object_card.vue'

const tabs = [
  { label: 'Все объекты', value: 'all' },
  { label: 'В работе', value: 'В работе' },
  { label: 'Приостановлено', value: 'Приостановлено' },
  { label: 'Выполнено', value: 'Выполнено' }
]

const currentTab = ref('all')

const mockObjects = ref([
  {
    id: 1,
    title: 'Капитальный ремонт ул. Тверская (участок от Манежной пл. до Садового кольца)',
    region: 'ЦАО',
    status: 'В работе',
    contractor: 'ГБУ Автомобильные дороги',
    executor: 'ООО ТехСтрой',
    statusProperties: {
      'Текущая фаза': 'Фрезерование покрытия',
      'Техника на объекте': '12 ед.',
      'Рабочие': '24 чел.',
      'Замечания технадзора': 'Нет'
    }
  },
  {
    id: 2,
    title: 'Реконструкция путепровода на пересечении Ленинградского шоссе и МЦД-3',
    region: 'САО',
    status: 'Приостановлено',
    contractor: 'АО Мосинжпроект',
    executor: 'ООО Мостоотряд-4',
    statusProperties: {
      'Текущая фаза': 'Монтаж пролетных строений',
      'Техника на объекте': '2 ед.',
      'Рабочие': '4 чел.',
      'Замечания технадзора': 'Требуется согласование "окна" РЖД'
    }
  },
  {
    id: 3,
    title: 'Благоустройство территории парка и УДС в районе Нагатинская Пойма',
    region: 'ЮАО',
    status: 'В работе',
    contractor: 'ГБУ Автомобильные дороги ЮАО',
    executor: 'ООО ДорСтройРегион',
    statusProperties: {
      'Текущая фаза': 'Укладка нижнего слоя асфальтобетона',
      'Техника на объекте': '8 ед.',
      'Рабочие': '16 чел.',
      'Замечания технадзора': 'Нет'
    }
  },
  {
    id: 4,
    title: 'Ремонт локальных разрушений покрытия дублера Кутузовского проспекта',
    region: 'ЗАО',
    status: 'Выполнено',
    contractor: 'ГБУ Автомобильные дороги',
    executor: 'Собственные силы',
    statusProperties: {
      'Текущая фаза': 'Объект сдан',
      'Техника на объекте': '0 ед.',
      'Рабочие': '0 чел.',
      'Замечания технадзора': 'Нет'
    }
  }
])

const filteredObjects = computed(() => {
  if (currentTab.value === 'all') {
    return mockObjects.value
  }
  return mockObjects.value.filter(obj => obj.status === currentTab.value)
})
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e1e3e8;
}

.toolbar-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #242424;
  margin: 0;
}

.objects-count {
  font-size: 13px;
  color: #616161;
}

.fluent-pivot {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 4px;
}

.pivot-item {
  background: transparent;
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
  left: 12px;
  right: 12px;
  height: 2px;
  background-color: #0078d4;
  border-radius: 2px;
}

.objects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

@media (max-width: 480px) {
  .objects-grid {
    grid-template-columns: 1fr;
  }
}

.empty-state {
  text-align: center;
  padding: 60px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px dashed #c5c9d1;
  color: #616161;
}

.empty-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.empty-state h3 {
  margin: 0 0 6px 0;
  color: #242424;
}

.empty-state p {
  margin: 0;
  font-size: 13px;
}
</style>