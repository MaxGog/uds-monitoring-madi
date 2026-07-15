<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <div>
        <p class="page-label">Обзор проекта</p>
        <h1 class="page-title">Панель контроля УДС</h1>
      </div>
      <div class="quick-links">
        <NuxtLink to="/acts" class="link-card">Акты</NuxtLink>
        <NuxtLink to="/monitoring" class="link-card">Объекты</NuxtLink>
        <NuxtLink to="/roadmap" class="link-card">Формирование ДК</NuxtLink>
      </div>
    </div>

    <div v-if="isLoadingActs || isLoadingObjects" class="loading-state">
      Загрузка данных...
    </div>
    <div v-if="errorActs || errorObjects" class="error-banner">
      ⚠️ {{ errorActs || errorObjects }}
    </div>

    <div v-else class="dashboard-sections">
      <CommonCard title="Последние акты" subtitle="Недавняя документация по объектам">
        <div v-if="recentActs.length" class="compact-grid">
          <ActCard v-for="act in recentActs" :key="act.id" :act="act" />
        </div>
        <div v-else class="empty-state">
          <span>📄</span>
          <p>Актов пока нет</p>
        </div>
      </CommonCard>

      <CommonCard title="Объекты мониторинга" subtitle="Состояние строительных объектов">
        <div v-if="recentObjects.length" class="compact-grid">
          <ObjectCard v-for="obj in recentObjects" :key="obj.id" :obj="obj" />
        </div>
        <div v-else class="empty-state">
          <span>🏗️</span>
          <p>Объектов пока нет</p>
        </div>
      </CommonCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import CommonCard from '~/components/common/common_card.vue'
import ActCard from '~/components/cards/act_card.vue'
import ObjectCard from '~/components/cards/object_card.vue'
import { useActs } from '~/composables/useActs'
import { useObject } from '~/composables/useObjects'

const { acts, isLoading: isLoadingActs, error: errorActs, fetchActs } = useActs()
const { objects, isLoading: isLoadingObjects, error: errorObjects, fetchObjects } = useObject()

const recentActs = computed(() => acts.value.slice(0, 2))
const recentObjects = computed(() => objects.value.slice(0, 3))

onMounted(async () => {
  await Promise.all([fetchActs(), fetchObjects()])
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.page-label {
  margin: 0;
  font-size: 13px;
  color: #616161;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.page-title {
  margin: 8px 0 0;
  font-size: 32px;
  font-weight: 700;
  color: #242424;
}

.quick-links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.link-card {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 18px;
  min-width: 150px;
  border-radius: 12px;
  border: 1px solid #e1e3e8;
  background: #ffffff;
  color: #242424;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.link-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

.loading-state,
.error-banner {
  padding: 16px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e1e3e8;
  text-align: center;
  color: #605e5c;
}

.error-banner {
  background: #fde7e9;
  border-color: #fccfd2;
  color: #a80000;
}

.dashboard-sections {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
}

.compact-grid {
  display: grid;
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 24px 0;
  color: #797979;
}

.empty-state span {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.empty-state p {
  margin: 0;
  font-size: 13px;
}

@media (max-width: 960px) {
  .dashboard-sections {
    grid-template-columns: 1fr;
  }
}
</style>