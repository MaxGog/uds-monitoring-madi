<template>
  <div class="admin-page-layout">
    <PageToolbar
      title="📁 Реестр государственных контрактов"
      subtitle="Полный контроль, изменение статусов, типов и финансовых лимитов"
      :countText="`Всего контрактов: ${filteredContracts.length} из ${contracts.length}`"
    >
      <template #actions>
        <button class="fluent-button button-primary" @click="openModal(null)">
          <span class="plus-icon">＋</span> Заключить новый контракт
        </button>
      </template>
    </PageToolbar>

    <FilterBar>
      <input 
        v-model="searchQuery" 
        placeholder="Поиск по ID или описанию..." 
        class="fluent-input main-search" 
      />
      
      <select v-model="statusFilter" class="fluent-select">
        <option value="all">Все статусы</option>
        <option value="draft">Черновик</option>
        <option value="active">Активен</option>
        <option value="completed">Завершен</option>
        <option value="terminated">Расторгнут</option>
      </select>
    </FilterBar>

    <div v-if="filteredContracts.length" class="table-container">
      <table class="fluent-table">
        <thead>
          <tr>
            <th>ID / Номер</th>
            <th>Тип</th>
            <th>Статус</th>
            <th>Сумма (Лимит)</th>
            <th>Сроки выполнения</th>
            <th>Связи</th>
            <th class="text-right">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contract in filteredContracts" :key="contract.id">
            <td class="font-semibold">
              <div>#{{ contract.id }}</div>
              <div class="sub-text">{{ contract.id || 'Б/Н' }}</div>
            </td>
            <td>
              <span class="type-badge">{{ contract.type || contract.type }}</span>
            </td>
            <td>
              <span class="status-badge" :class="contract.status">
                {{ formatStatus(contract.status) }}
              </span>
            </td>
            <td class="font-semibold">
              {{ formatCurrency(contract.cost) }}
            </td>
            <td class="sub-text">
              <div>С: {{ formatDate(contract.planned_start) }}</div>
              <div>По: {{ formatDate(contract.planned_end) }}</div>
            </td>
            <td>
              <div v-if="contract.work_id" class="sub-text">🛠️ {{ contract.work_id }}</div>
              <div v-else-if="contract.work_id" class="sub-text">ID Работы: {{ contract.work_id }}</div>
              <div v-else class="sub-text text-muted">Нет привязки</div>
            </td>
            <td class="text-right">
              <div class="action-buttons">
                <button class="action-btn edit" @click="openModal(contract)" title="Редактировать">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1 0 .708l-9.82 9.82a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l9.82-9.82zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                  </svg>
                </button>
                <button class="action-btn delete" @click="handleDelete(contract.id)" title="Удалить">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <EmptyState
      v-else
      icon="📂"
      title="Контракты не найдены"
      description="Измените параметры фильтрации или заключите новое соглашение."
      buttonText="Сбросить фильтры"
      @action="resetFilters"
    />

    <CommonModal
      :is-open="isModalOpen"
      :title="isEditMode ? `Редактирование контракта #${form.contract_id}` : 'Заключение нового контракта'"
      width="680px"
      @close="closeModal"
    >
      <form @submit.prevent="handleSubmit">
        <FormControls>
          <div v-if="error" class="error-banner">
            ⚠️ Ошибка: {{ error }}
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="con-num">Номер контракта *</label>
              <input
                id="con-num"
                v-model="form.contract_id"
                type="text"
                required
                placeholder="ГК-2026/04"
                class="fluent-input"
              />
            </div>
            <div class="form-group">
              <label for="con-type">Тип контракта *</label>
              <select id="con-type" v-model="form.type" required class="fluent-select">
                <option :value="ContractType.GENERAL">Генподряд (general)</option>
                <option :value="ContractType.WORK">Рабочий контрагент (work)</option>
                <option :value="ContractType.ADDITIONAL">Доп. соглашение (additional)</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="con-start">Планируемая дата начала</label>
              <input
                id="con-start"
                v-model="form.planned_start"
                type="date"
                class="fluent-input"
              />
              <span class="field-hint">Оставьте пустым, если неизвестно</span>
            </div>
            <div class="form-group">
              <label for="con-end">Планируемая дата окончания</label>
              <input
                id="con-end"
                v-model="form.planned_end"
                type="date"
                class="fluent-input"
                :class="{ 'input-invalid': dateOrderError }"
              />
              <span v-if="dateOrderError" class="field-warning">⚠️ {{ dateOrderError }}</span>
              <span v-else class="field-hint">Оставьте пустым, если неизвестно</span>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="con-limit">Финансовый лимит (Сумма) *</label>
              <input
                id="con-limit"
                v-model.number="form.cost"
                type="number"
                min="0"
                step="0.01"
                required
                placeholder="0.00"
                class="fluent-input"
              />
              <span v-if="form.cost! <= 0" class="field-warning">⚠️ Сумма контракта должна быть больше 0</span>
            </div>
            <div class="form-group">
              <label for="con-status">Статус контракта</label>
              <select id="con-status" v-model="form.status" required class="fluent-select">
                <option value="draft">Черновик</option>
                <option value="active">Активен</option>
                <option value="completed">Завершен</option>
                <option value="terminated">Расторгнут</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="con-desc">Описание предмета контракта</label>
            <textarea
              id="con-desc"
              v-model="form.description"
              placeholder="Выполнение строительно-монтажных работ на объекте..."
              class="fluent-textarea"
            ></textarea>
          </div>
        </FormControls>

        <div class="form-actions">
          <button type="button" class="fluent-button button-secondary" @click="closeModal">Отмена</button>
          <button 
            type="submit" 
            class="fluent-button button-primary">
            {{ isEditMode ? 'Сохранить' : 'Создать' }}
          </button>
        </div>
      </form>
    </CommonModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import CommonModal from '~/components/common/common_modal.vue'
import FormControls from '~/components/common/form_controls.vue'
import { useContract } from '~/composables/useContract'
import { ContractStatus, ContractType } from '~/types/enums'
import type { Contract, ContractCreate, ContractUpdate } from '~/types/contract'

const {
  contracts,
  isLoading,
  error,
  fetchContracts,
  createContract,
  updateContract,
  deleteContract,
  clearError
} = useContract()

const searchQuery = ref('')
const statusFilter = ref('all')
const isModalOpen = ref(false)
const isEditMode = ref(false)
const currentContractId = ref<number | null>(null)

const getEmptyForm = (): ContractCreate => ({
  contract_id: '',
  status: ContractStatus.DRAFT,
  type: ContractType.GENERAL,
  description: '',
  cost: 0,
  total_cost: 0,
  planned_start: '',
  planned_end: '',
  actual_start: null,
  actual_end: null,
  object_id: null,
  work_id: null,
  date_signed: new Date().toISOString().split('T')[0]
})

const form = ref<ContractCreate | ContractUpdate>(getEmptyForm())

onMounted(() => {
  fetchContracts()
})

const dateOrderError = computed(() => {
  if (form.value.planned_start && form.value.planned_end) {
    const start = new Date(form.value.planned_start)
    const end = new Date(form.value.planned_end)
    if (end < start) {
      return 'Дата окончания не может быть раньше даты начала!'
    }
  }
  return ''
})

const filteredContracts = computed(() => {
  return contracts.value.filter(c => {
    const matchesSearch = !searchQuery.value || 
      c.id.toString().includes(searchQuery.value) || 
      (c.contract_id && c.contract_id.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (c.description && c.description.toLowerCase().includes(searchQuery.value.toLowerCase()))

    const matchesStatus = statusFilter.value === 'all' || c.status === statusFilter.value

    return matchesSearch && matchesStatus
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = 'all'
}

const openModal = (contract: Contract | null = null) => {
  clearError()
  if (contract) {
    isEditMode.value = true
    currentContractId.value = contract.id
    form.value = { ...contract } as ContractUpdate
  } else {
    isEditMode.value = false
    currentContractId.value = null
    form.value = getEmptyForm()
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const handleSubmit = async () => {
  if (dateOrderError.value) return

  const payload = { ...form.value }
  if (!payload.planned_start) payload.planned_start = 'null'
  if (!payload.planned_end) payload.planned_end = 'null'

  if (payload.cost && !payload.total_cost) {
    payload.total_cost = payload.cost
  }

  let result = null
  if (isEditMode.value && currentContractId.value) {
    result = await updateContract(currentContractId.value, payload as ContractUpdate)
  } else {
    result = await createContract(payload as ContractCreate)
  }

  if (result) {
    await fetchContracts()
    closeModal()
  }
}

const handleDelete = async (id: number) => {
  if (confirm('Удалить этот контракт из системы?')) {
    const success = await deleteContract(id)
    if (success) {
      await fetchContracts()
    }
  }
}

const formatStatus = (st: string) => {
  const map: Record<string, string> = {
    [ContractStatus.DRAFT]: 'Черновик',
    [ContractStatus.ACTIVE]: 'Активен',
    [ContractStatus.COMPLETED]: 'Завершен',
    [ContractStatus.TERMINATED]: 'Расторгнут'
  }
  return map[st] || st
}

const formatType = (type: string) => {
  const map: Record<string, string> = {
    [ContractType.GENERAL]: 'Генподряд',
    [ContractType.WORK]: 'Рабочий контрагент',
    [ContractType.ADDITIONAL]: 'Доп. соглашение'
  }
  return map[type] || type
}

const formatCurrency = (val: number) => {
  if (!val) return '0 ₽'
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(val)
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ru-RU')
}
</script>

<style scoped>
.admin-page-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}
.fluent-input.main-search {
  max-width: 400px;
  width: 100%;
}
.table-container {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  overflow: hidden;
}
.fluent-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.fluent-table th {
  background: #f3f4f6;
  padding: 12px;
  font-weight: 600;
  border-bottom: 1px solid #e1e3e8;
}
.fluent-table td {
  padding: 12px;
  border-bottom: 1px solid #f3f2f1;
}
.sub-text {
  font-size: 11px;
  color: #797979;
  margin-top: 2px;
}
.text-muted {
  color: #a19f9d;
}
.text-right {
  text-align: right;
}
.font-semibold {
  font-weight: 600;
}

/* Статусы */
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}
.status-badge.active { background: #dfefe5; color: #107c41; }
.status-badge.draft { background: #f3f2f1; color: #616161; }
.status-badge.completed { background: #e2f1f9; color: #0078d4; }
.status-badge.terminated { background: #fde7e9; color: #a80000; }

.type-badge {
  display: inline-block;
  padding: 2px 6px;
  background: #fafafa;
  border: 1px solid #d2d0ce;
  border-radius: 4px;
  font-size: 11px;
  color: #323130;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
}
.action-btn:hover {
  background: #f3f2f1;
}

/* Ошибки */
.error-banner {
  background: #fdf2f2;
  border: 1px solid #fde7e9;
  border-radius: 4px;
  color: #a80000;
  padding: 10px 14px;
  font-size: 13px;
}
.field-warning {
  color: #b13512;
  font-size: 11px;
  margin-top: 4px;
}
.field-hint {
  color: #797979;
  font-size: 11px;
  margin-top: 4px;
}
.input-invalid {
  border-color: #a80000 !important;
  background-color: #fff8f8 !important;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f3f2f1;
}
.fluent-button {
  padding: 8px 16px;
  font-weight: 600;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
}
.button-primary {
  background: #0078d4;
  color: #fff;
}
.button-primary:hover {
  background: #106ebe;
}
.button-primary:disabled {
  background: #f3f2f1;
  color: #a19f9d;
  cursor: not-allowed;
}
.button-secondary {
  background: #fff;
  border-color: #d2d0ce;
  color: #323130;
}
.button-secondary:hover {
  background: #f3f2f1;
}

.fluent-input, 
.fluent-select, 
.fluent-textarea {
  width: 100%;
  padding: 8px 12px;
  font-family: inherit;
  font-size: 14px;
  border: 1px solid #d2d0ce;
  border-radius: 4px;
  background-color: #ffffff;
  color: #323130;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-sizing: border-box;
}

.fluent-input:focus, 
.fluent-select:focus, 
.fluent-textarea:focus {
  outline: none;
  border-color: #0078d4;
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.2);
}

.fluent-textarea {
  min-height: 80px;
  resize: vertical;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #323130;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>