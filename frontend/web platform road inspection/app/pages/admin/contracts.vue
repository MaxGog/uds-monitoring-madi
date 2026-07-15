<template>
  <div class="admin-page-layout">
    <div class="fluent-toolbar">
      <div>
        <h1 class="page-title">📁 Реестр государственных контрактов</h1>
        <p class="page-subtitle">Полный контроль, изменение статусов, типов и финансовых лимитов</p>
      </div>
      <button class="fluent-button button-primary" @click="openModal(null)">
        ➕ Заключить новый контракт
      </button>
    </div>

    <div class="filter-bar">
      <input v-model="searchQuery" placeholder="Поиск по ID или описанию..." class="fluent-input main-search" />
      <select v-model="statusFilter" class="fluent-select">
        <option value="all">Все статусы</option>
        <option value="draft">Черновик</option>
        <option value="active">Активен</option>
        <option value="completed">Завершен</option>
        <option value="terminated">Расторгнут</option>
      </select>
    </div>

    <div class="table-container">
      <table class="fluent-table">
        <thead>
          <tr>
            <th>ID / Номер</th>
            <th>Тип</th>
            <th>Статус</th>
            <th>Сумма (Лимит)</th>
            <th>Сроки выполнения</th>
            <th>Связи (Объект/Работа)</th>
            <th class="text-right">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contract in filteredContracts" :key="contract.id">
            <td class="font-semibold">
              {{ contract.contract_id || `ID: ${contract.id}` }}
              <div class="sub-text">{{ contract.date_signed }}</div>
            </td>
            <td>
              <span class="type-badge" :class="contract.type">{{ mapType(contract.type) }}</span>
            </td>
            <td>
              <span class="status-badge" :class="contract.status">{{ mapStatus(contract.status) }}</span>
            </td>
            <td>
              <div class="cost-value">{{ formatCurrency(contract.cost) }}</div>
              <div class="sub-text">Всего: {{ formatCurrency(contract.total_cost) }}</div>
            </td>
            <td>
              <div class="date-range">План: {{ contract.planned_start }} - {{ contract.planned_end }}</div>
              <div class="sub-text" v-if="contract.actual_start">Факт: {{ contract.actual_start }}</div>
            </td>
            <td>
              <span class="link-id">Obj: {{ contract.object_id || '—' }}</span> / 
              <span class="link-id">Work: {{ contract.work_id || '—' }}</span>
            </td>
            <td class="text-right">
              <button class="action-btn edit-btn" @click="openModal(contract)">✏️</button>
              <button class="action-btn delete-btn" @click="handleDelete(contract.id)">❌</button>
            </td>
          </tr>
          <tr v-if="filteredContracts.length === 0">
            <td colspan="7" class="empty-row">Контракты не найдены.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fluent-modal-overlay">
      <div class="fluent-modal-window">
        <div class="modal-header">
          <h3>{{ isEditMode ? 'Редактирование контракта' : 'Регистрация нового контракта' }}</h3>
          <button class="close-modal-btn" @click="closeModal">✕</button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-grid">
            <div class="form-field">
              <label>Номер / ID контракта *</label>
              <input v-model="form.contract_id" type="text" required placeholder="Например, № 44-ФЗ/2026" class="fluent-input" />
            </div>
            <div class="form-field">
              <label>Дата подписания</label>
              <input v-model="form.date_signed" type="date" class="fluent-input" />
            </div>

            <div class="form-field">
              <label>Тип контракта</label>
              <select v-model="form.type" class="fluent-select">
                <option value="general">Генподряд (General)</option>
                <option value="work">Договор подряда (Work)</option>
                <option value="additional">Доп. соглашение (Additional)</option>
              </select>
            </div>
            <div class="form-field">
              <label>Статус</label>
              <select v-model="form.status" class="fluent-select">
                <option value="draft">Черновик (Draft)</option>
                <option value="active">Активен (Active)</option>
                <option value="completed">Завершен (Completed)</option>
                <option value="terminated">Расторгнут (Terminated)</option>
              </select>
            </div>

            <div class="form-field">
              <label>Текущая стоимость (Cost)</label>
              <input v-model.number="form.cost" type="number" step="0.01" class="fluent-input" />
            </div>
            <div class="form-field">
              <label>Общая итоговая стоимость (Total Cost)</label>
              <input v-model.number="form.total_cost" type="number" step="0.01" class="fluent-input" />
            </div>

            <div class="form-field">
              <label>Плановое начало</label>
              <input v-model="form.planned_start" type="date" class="fluent-input" />
            </div>
            <div class="form-field">
              <label>Плановое завершение</label>
              <input v-model="form.planned_end" type="date" class="fluent-input" />
            </div>

            <div class="form-field">
              <label>ID Объекта (Связь)</label>
              <input v-model.number="form.object_id" type="number" class="fluent-input" placeholder="ID из таблицы objects" />
            </div>
            <div class="form-field">
              <label>ID Работы (Связь)</label>
              <input v-model.number="form.work_id" type="number" class="fluent-input" placeholder="ID из таблицы works" />
            </div>

            <div class="form-field full-width">
              <label>Описание / Предмет контракта</label>
              <textarea v-model="form.description" rows="3" class="fluent-input textarea"></textarea>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="fluent-button button-secondary" @click="closeModal">Отмена</button>
            <button type="submit" class="fluent-button button-primary" :disabled="isLoading">
              {{ isEditMode ? 'Сохранить изменения' : 'Создать контракт' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useContract } from '~/composables/useContract';
import type { Contract } from '~/types/contract';

const { contracts, isLoading, fetchContracts, createContract, updateContract, deleteContract } = useContract();

const searchQuery = ref('');
const statusFilter = ref('all');

// Состояние модального окна
const isModalOpen = ref(false);
const isEditMode = ref(false);
const selectedContractId = ref<number | null>(null);

const form = ref({
  contract_id: '',
  date_signed: '',
  description: '',
  status: 'draft' as Contract['status'],
  type: 'work' as Contract['type'],
  cost: 0,
  total_cost: 0,
  planned_start: '',
  planned_end: '',
  actual_start: null as string | null,
  actual_end: null as string | null,
  object_id: null as number | null,
  work_id: null as number | null
});

onMounted(() => {
  fetchContracts();
});

const filteredContracts = computed(() => {
  return contracts.value.filter(c => {
    const matchesSearch = (c.contract_id?.toLowerCase() || '').includes(searchQuery.value.toLowerCase()) ||
                          (c.description?.toLowerCase() || '').includes(searchQuery.value.toLowerCase());
    const matchesStatus = statusFilter.value === 'all' || c.status === statusFilter.value;
    return matchesSearch && matchesStatus;
  });
});

const openModal = (contract: Contract | null) => {
  if (contract) {
    isEditMode.value = true;
    selectedContractId.value = contract.id;
    form.value = { ...contract };
  } else {
    isEditMode.value = false;
    selectedContractId.value = null;
    form.value = {
      contract_id: '',
      date_signed: new Date().toISOString().substring(0, 10),
      description: '',
      status: 'draft',
      type: 'work',
      cost: 0,
      total_cost: 0,
      planned_start: '',
      planned_end: '',
      actual_start: null,
      actual_end: null,
      object_id: null,
      work_id: null
    };
  }
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const handleSubmit = async () => {
  if (isEditMode.value && selectedContractId.value) {
    const res = await updateContract(selectedContractId.value, form.value);
    if (res) fetchContracts();
  } else {
    const res = await createContract(form.value);
    if (res) fetchContracts();
  }
  closeModal();
};

const handleDelete = async (id: number) => {
  if (confirm('Вы уверены, что хотите безвозвратно удалить этот контракт?')) {
    await deleteContract(id);
  }
};

const mapStatus = (s: string) => ({ draft: 'Черновик', active: 'Активен', completed: 'Завершен', terminated: 'Расторгнут' }[s] || s);
const mapType = (t: string) => ({ general: 'Генподряд', work: 'Подряд на работы', additional: 'Доп. соглашение' }[t] || t);
const formatCurrency = (val: number) => new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB' }).format(val || 0);
</script>

<style scoped>
.admin-page-layout {
  padding: 24px;
  font-family: var(--fluent-font, sans-serif);
  color: #242424;
}

.fluent-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 13px;
  color: #616161;
  margin: 0;
}

/* Кнопки */
.fluent-button {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid transparent;
}
.button-primary {
  background: #0078d4;
  color: white;
}
.button-primary:hover { background: #106ebe; }
.button-secondary {
  background: #ffffff;
  border-color: #d6d9dc;
  color: #242424;
}
.button-secondary:hover { background: #f3f2f1; }

.filter-bar {
  display: flex;
  gap: 12px;
  background: #ffffff;
  padding: 12px;
  border: 1px solid #e1e3e8;
  border-radius: 6px;
  margin-bottom: 16px;
}
.main-search { flex: 1; }

.fluent-input, .fluent-select {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 13px;
  background: #ffffff;
  outline: none;
}
.fluent-input:focus, .fluent-select:focus { border-color: #0078d4; }
.textarea { resize: vertical; }

.fluent-modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.fluent-modal-window {
  background: #ffffff;
  border-radius: 8px;
  width: 640px;
  max-width: 90%;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  overflow: hidden;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; background: #f3f4f6; border-bottom: 1px solid #eaeaea;
}
.modal-header h3 { margin: 0; font-size: 16px; font-weight: 600; }
.close-modal-btn { background: none; border: none; font-size: 16px; cursor: pointer; }

.modal-form { padding: 24px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-field { display: flex; flex-direction: column; gap: 4px; }
.form-field.full-width { grid-column: span 2; }
.form-field label { font-size: 12px; font-weight: 600; color: #616161; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }

.table-container { background: #ffffff; border: 1px solid #e1e3e8; border-radius: 6px; overflow: hidden; }
.fluent-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
.fluent-table th { background: #f3f4f6; padding: 12px; font-weight: 600; border-bottom: 1px solid #e1e3e8; }
.fluent-table td { padding: 12px; border-bottom: 1px solid #f3f2f1; vertical-align: top; }
.sub-text { font-size: 11px; color: #797979; margin-top: 2px; }
.text-right { text-align: right; }
.font-semibold { font-weight: 600; }
.empty-row { text-align: center; color: #797979; padding: 32px !important; }

.status-badge, .type-badge {
  display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;
}
.status-badge.active { background: #dfefe5; color: #107c41; }
.status-badge.draft { background: #f3f2f1; color: #616161; }
.status-badge.completed { background: #e2f1f9; color: #0078d4; }
.status-badge.terminated { background: #fde7e9; color: #a80000; }

.type-badge.general { background: #fff4ce; color: #795300; }
.type-badge.work { background: #ece6fc; color: #5c2d91; }
.type-badge.additional { background: #e4f7fc; color: #005a70; }

.action-btn { background: none; border: none; cursor: pointer; padding: 4px 8px; font-size: 14px; border-radius: 4px; }
.action-btn:hover { background: #f3f2f1; }
.link-id { background: #fafafa; padding: 1px 4px; border: 1px solid #eaeaea; border-radius: 3px; font-family: monospace; }
.max-width-address { max-width: 200px; white-space: nowrap; overflow: hidden; text-ellipsis: true; }
</style>