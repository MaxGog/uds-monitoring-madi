<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <div>
        <p class="page-label">Обзор проекта</p>
        <h1 class="page-title">Панель контроля УДС</h1>
      </div>
      <div class="quick-links">
        <NuxtLink to="/acts" class="link-card">Акты</NuxtLink>
        <NuxtLink to="/work-statuses" class="link-card">Статусы работ</NuxtLink>
        <NuxtLink to="/roadmap" class="link-card">Формирование ДК</NuxtLink>
      </div>
    </div>

    <div class="dashboard-sections">
      <CommonCard title="Последние акты" subtitle="Недавняя документация по объектам">
        <div class="compact-grid">
          <ActCard v-for="act in recentActs" :key="act.id" :act="act" />
        </div>
      </CommonCard>

      <CommonCard title="Текущие статусы" subtitle="Состояние строительных объектов">
        <div class="compact-grid">
          <WorkStatusCard
            v-for="status in recentStatuses"
            :key="status.id"
            :status="status"
          />
        </div>
      </CommonCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import CommonCard from '~/components/common/common_card.vue'
import SummaryCard from '~/components/cards/summary_card.vue'
import ActCard from '~/components/cards/act_card.vue'
import WorkStatusCard from '~/components/cards/work_status_card.vue'
import { useMockData } from '~/composables/useMockData'
import { computed } from 'vue'

const { acts, workStatuses, roadmapItems } = useMockData()

const recentActs = computed(() => acts.value.slice(0, 2))
const recentStatuses = computed(() => workStatuses.value.slice(0, 2))
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

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
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

@media (max-width: 960px) {
  .dashboard-sections {
    grid-template-columns: 1fr;
  }
}
</style>
