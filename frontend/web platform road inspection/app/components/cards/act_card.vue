<template>
  <div class="fluent-act-card" :class="`status-${statusSlug}`">
    <div class="card-header">
      <div class="header-main">
        <div class="badge-row">
          <span class="act-type">{{ act.type }}</span>
          <span class="region-tag">{{ act.region }}</span>
        </div>
        <h3 class="act-title">Акт № {{ act.number }}</h3>
      </div>
      <span class="status-badge" :class="statusSlug">
        <span class="status-dot"></span>
        {{ act.status }}
      </span>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="fluent-icon">🏢</span>
        <div class="info-content">
          <span class="info-label">Объект дорожного хозяйства (ОДХ)</span>
          <span class="info-value text-ellipsis" :title="act.objectName">{{ act.objectName }}</span>
        </div>
      </div>
      <div class="info-row">
        <span class="fluent-icon">🤝</span>
        <div class="info-content">
          <span class="info-label">Подрядчик</span>
          <span class="info-value text-ellipsis" :title="act.contractor">{{ act.contractor }}</span>
        </div>
      </div>

      <div class="divider"></div>

      <div class="total-row">
        <span class="total-label">Факт выполнения:</span>
        <span class="total-amount">{{ act.amount }}</span>
      </div>
    </div>

    <div class="card-actions">
      <button class="fluent-button button-secondary" @click="isModalOpen = true">
        Открыть
      </button>
      <button v-if="act.status === 'Ожидает подписи'" class="fluent-button button-primary" @click="signAct">
        Подписать
      </button>
    </div>

    <CommonModal :isOpen="isModalOpen" width="750px" @close="isModalOpen = false">
      <template #header>
        <div class="modal-header-layout">
          <span class="act-type">{{ act.type }} | {{ act.region }} округ</span>
          <h3 class="modal-main-title">Система обработки и контроля объемов № {{ act.number }}</h3>
        </div>
      </template>

      <div class="modal-act-extended">
        <div class="modal-status-banner" :class="statusSlug">
          <strong>Статус записи в ИС:</strong> {{ act.status }} 
          <span v-if="act.status === 'Подписан'"> (Утверждено ЭЦП: {{ act.signDate }})</span>
        </div>

        <h4 class="block-title">Реквизиты и привязка к контракту</h4>
        <div class="details-grid">
          <div class="detail-field full">
            <label>Наименование объекта (ОДХ)</label>
            <div class="field-value font-semibold">{{ act.objectName }}</div>
          </div>
          
          <div class="detail-field">
            <label>Государственный контракт / Основание</label>
            <div class="field-value">📄 {{ act.contractNumber }}</div>
          </div>

          <div class="detail-field">
            <label>Территориальное управление (Округ)</label>
            <div class="field-value">📍 {{ act.region }}</div>
          </div>

          <div class="detail-field">
            <label>Генеральный подрядчик</label>
            <div class="field-value">🏢 {{ act.contractor }}</div>
          </div>

          <div class="detail-field">
            <label>Ответственный инспектор</label>
            <div class="field-value">👤 {{ act.signedBy || 'Не назначен' }}</div>
          </div>
        </div>

        <div class="modal-divider"></div>

        <h4 class="block-title">Финансовые показатели и сверка с планом (C:M)</h4>
        <div class="details-grid bg-finance-grid">
          <div class="detail-field">
            <label>Плановый объем СМР</label>
            <div class="field-value-light">{{ act.planAmount }}</div>
          </div>
          <div class="detail-field">
            <label>Принято по факту (Без НДС)</label>
            <div class="field-value-light">{{ act.amount }} (НДС 20%: {{ act.vatAmount }})</div>
          </div>
          <div class="detail-field full">
            <label>Итоговая сумма к закрытию</label>
            <div class="total-highlight-value">{{ act.amount }}</div>
          </div>
        </div>

        <div class="modal-divider"></div>

        <h4 class="block-title">Интеграция с файловым хранилищем Диска</h4>
        <div class="files-integration-box">
          <a :href="act.docUrl" target="_blank" class="file-link doc" :class="{ disabled: act.docUrl === '#' }">
            <span class="file-icon">📝</span> Google Docs Оригинал
          </a>
          <a :href="act.pdfUrl" target="_blank" class="file-link pdf" :class="{ disabled: act.pdfUrl === '#' }">
            <span class="file-icon">📕</span> Экспорт в PDF
          </a>
        </div>

        <div v-if="act.notes" class="modal-notes-section">
          <label>Примечания инспекции / Журнал изменений</label>
          <div class="notes-content-box">
            {{ act.notes }}
          </div>
        </div>
      </div>

      <template #footer>
        <button class="fluent-button button-secondary" @click="isModalOpen = false">Закрыть</button>
        <button 
          v-if="act.status === 'Ожидает подписи'" 
          class="fluent-button button-primary" 
          @click="signAct"
        >
          ✍️ Утвердить объемы и подписать ЭЦП
        </button>
      </template>
    </CommonModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { MockAct } from '~/composables/useMockData'
import CommonModal from '~/components/common/common_modal.vue'

const props = defineProps<{ act: MockAct }>()
const isModalOpen = ref(false)

const statusSlug = computed(() => {
  if (props.act.status === 'Подписан') return 'signed'
  if (props.act.status === 'Ожидает подписи') return 'pending'
  return 'review'
})

const signAct = () => {
  alert(`Акт № ${props.act.number} отправлен на шлюз ЭЦП. Запись зафиксирована в логе Google Таблиц.`)
}
</script>

<style scoped>
.fluent-act-card {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}
.fluent-act-card::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
}
.fluent-act-card.status-signed::before { background: #107c41; }
.fluent-act-card.status-pending::before { background: #b13512; }
.fluent-act-card.status-review::before { background: #0078d4; }

.card-header { padding: 14px 16px; display: flex; justify-content: space-between; align-items: flex-start; }
.badge-row { display: flex; gap: 6px; align-items: center; margin-bottom: 2px; }
.region-tag { font-size: 10px; background: #f3f2f1; padding: 1px 5px; border-radius: 2px; font-weight: 600; color: #424242; }
.act-type { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #616161; }
.act-title { margin: 2px 0 0; font-size: 14px; font-weight: 600; }

.status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 2px 6px; border-radius: 2px; font-size: 11px; font-weight: 500; }
.status-badge.signed { background: #ecfdf5; color: #107c41; }
.status-badge.pending { background: #fdf2f2; color: #b13512; }
.status-badge.review { background: #eff6ff; color: #0078d4; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; background: currentColor; }

.card-body { padding: 0 16px 12px; flex: 1; display: flex; flex-direction: column; gap: 8px; }
.divider { height: 1px; background: #f3f3f3; margin: 2px 0; }
.info-row { display: flex; gap: 8px; font-size: 13px; }
.info-label { font-size: 11px; color: #797979; display: block; }
.info-value { font-size: 13px; color: #242424; margin-top: 1px; }
.font-semibold { font-weight: 600; }
.text-ellipsis { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 240px; }

.total-row { display: flex; justify-content: space-between; align-items: center; background: #fbfbfb; padding: 6px 10px; border-radius: 4px; border: 1px solid #f3f3f3; }
.total-label { font-size: 11px; font-weight: 600; }
.total-amount { font-size: 14px; font-weight: 700; color: #242424; }

.card-actions { padding: 10px 16px; background: #f8f9fa; border-top: 1px solid #f3f3f3; display: flex; justify-content: flex-end; gap: 8px; }

.fluent-button { font-size: 12px; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: 500; }
.button-secondary { background: #ffffff; border: 1px solid #d2d0ce; color: #323130; }
.button-secondary:hover { background: #f3f2f1; }
.button-primary { background: #0078d4; border: 1px solid #0078d4; color: #ffffff; }
.button-primary:hover { background: #106ebe; }

.modal-header-layout { display: flex; flex-direction: column; }
.modal-main-title { margin: 2px 0 0 0; font-size: 18px; font-weight: 600; color: #242424; }

.modal-act-extended { display: flex; flex-direction: column; gap: 14px; }
.modal-status-banner { padding: 10px 14px; border-radius: 4px; font-size: 13px; border-left: 4px solid #a1a1a1; }
.modal-status-banner.signed { background: #ecfdf5; color: #107c41; border-left-color: #107c41; }
.modal-status-banner.pending { background: #fdf2f2; color: #b13512; border-left-color: #b13512; }
.modal-status-banner.review { background: #eff6ff; color: #0078d4; border-left-color: #0078d4; }

.block-title { margin: 8px 0 2px 0; font-size: 12px; font-weight: 600; color: #616161; text-transform: uppercase; letter-spacing: 0.3px; }

.details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.detail-field { display: flex; flex-direction: column; gap: 4px; }
.detail-field.full { grid-column: span 2; }
.detail-field label { font-size: 11px; font-weight: 600; color: #797979; }

.field-value { background: #f3f2f1; padding: 8px 12px; border-radius: 4px; border: 1px solid #edebe9; font-size: 13px; color: #242424; }
.field-value-light { background: #fafafa; padding: 6px 10px; border-radius: 4px; border: 1px dashed #d2d0ce; font-size: 13px; }

.bg-finance-grid { background-color: #fcfcfc; padding: 14px; border-radius: 6px; border: 1px solid #f0f0f0; }
.total-highlight-value { font-size: 22px; font-weight: 700; color: #107c41; margin-top: 2px; }
.modal-divider { height: 1px; background-color: #eaeaea; margin: 4px 0; }

.files-integration-box { display: flex; gap: 12px; }
.file-link { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 4px; font-size: 13px; text-decoration: none; font-weight: 500; border: 1px solid transparent; transition: all 0.1s; }
.file-link.doc { background: #f3f8ff; color: #005a9e; border-color: #d0e1f9; }
.file-link.doc:hover:not(.disabled) { background: #e0ecfd; }
.file-link.pdf { background: #fff5f5; color: #a4261d; border-color: #fcd2d2; }
.file-link.pdf:hover:not(.disabled) { background: #ffebeb; }
.file-link.disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; background: #f3f2f1 !important; color: #a19f9d !important; border-color: #edebe9 !important; }

.notes-content-box { background: #fffdf5; border: 1px solid #ffeab2; border-left: 4px solid #ffc247; padding: 12px; border-radius: 4px; font-size: 13px; color: #5d461a; font-style: italic; }
</style>