<template>
  <div class="admin-page-layout">
    <PageToolbar
      title="🏢 Справочник контрагентов и компаний"
      subtitle="Редактирование реквизитов (ИНН/КПП, БИК) и расчетных счетов подрядчиков"
      :countText="`Всего организаций: ${filteredCompanies.length} из ${companies.length}`"
    >
      <template #actions>
        <button class="fluent-button button-primary" @click="openModal(null)">
          <span class="plus-icon">＋</span> Добавить контрагента
        </button>
      </template>
    </PageToolbar>

    <FilterBar>
      <input 
        v-model="searchQuery" 
        placeholder="Поиск по названию или ИНН..." 
        class="fluent-input main-search" 
      />
    </FilterBar>

    <div v-if="filteredCompanies.length" class="table-container">
      <table class="fluent-table">
        <thead>
          <tr>
            <th>Наименование</th>
            <th>ИНН / КПП</th>
            <th>Юридический адрес</th>
            <th>Банковские реквизиты</th>
            <th class="text-right">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in filteredCompanies" :key="company.id">
            <td class="font-semibold text-blue">{{ company.name }}</td>
            <td>
              <div>ИНН: {{ company.inn || '—' }}</div>
              <div class="sub-text">КПП: {{ company.kpp || '—' }}</div>
            </td>
            <td class="max-width-address" :title="company.address || ''">
              {{ company.address || '—' }}
            </td>
            <td>
              <div v-if="company.bank_account">Р/С: {{ company.bank_account }}</div>
              <div class="sub-text" v-if="company.bic">БИК: {{ company.bic }}</div>
              <div v-if="!company.bank_account && !company.bic" class="sub-text">Не указаны</div>
            </td>
            <td class="text-right">
              <div class="action-buttons">
                <button class="action-btn edit" @click="openModal(company)" title="Редактировать">
                  <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1 0 .708l-9.82 9.82a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l9.82-9.82zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                  </svg>
                </button>
                <button class="action-btn delete" @click="handleDelete(company.id)" title="Удалить">
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
      icon="🏢"
      title="Компании не найдены"
      description="Измените поисковый запрос или добавьте новую организацию в справочник."
      buttonText="Сбросить поиск"
      @action="searchQuery = ''"
    />

    <CommonModal
      :is-open="isModalOpen"
      :title="isEditMode ? 'Редактировать контрагента' : 'Добавить нового контрагента'"
      width="640px"
      @close="closeModal"
    >
      <form @submit.prevent="handleSubmit">
        <FormControls>
          <div v-if="error" class="error-banner">
            ⚠️ Ошибка сохранения: {{ error }}
          </div>

          <div class="form-group">
            <label for="comp-name">Название компании *</label>
            <input
              id="comp-name"
              v-model="form.name"
              type="text"
              required
              placeholder="ООО 'СтройТехКонтроль'"
              class="fluent-input"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="comp-inn">ИНН *</label>
              <input
                id="comp-inn"
                v-model="form.inn"
                type="text"
                required
                placeholder="10 или 12 цифр"
                class="fluent-input"
                :class="{ 'input-invalid': innError }"
              />
              <span v-if="innError" class="field-warning">⚠️ {{ innError }}</span>
            </div>

            <div class="form-group">
              <label for="comp-kpp">КПП</label>
              <input
                id="comp-kpp"
                v-model="form.kpp"
                type="text"
                placeholder="9 цифр (для ЮЛ)"
                class="fluent-input"
                :class="{ 'input-invalid': kppError }"
              />
              <span v-if="kppError" class="field-warning">⚠️ {{ kppError }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="comp-address">Юридический адрес *</label>
            <input
              id="comp-address"
              v-model="form.address"
              type="text"
              required
              placeholder="Минимум 5 символов"
              class="fluent-input"
              :class="{ 'input-invalid': addressError }"
            />
            <span v-if="addressError" class="field-warning">⚠️ {{ addressError }}</span>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="comp-bic">БИК *</label>
              <input
                id="comp-bic"
                v-model="form.bic"
                type="text"
                required
                placeholder="9 цифр"
                class="fluent-input"
                :class="{ 'input-invalid': bicError }"
              />
              <span v-if="bicError" class="field-warning">⚠️ {{ bicError }}</span>
            </div>

            <div class="form-group">
              <label for="comp-bank">Расчетный счет *</label>
              <input
                id="comp-bank"
                v-model="form.bank_account"
                type="text"
                required
                placeholder="20 цифр"
                class="fluent-input"
                :class="{ 'input-invalid': bankAccountError }"
              />
              <span v-if="bankAccountError" class="field-warning">⚠️ {{ bankAccountError }}</span>
            </div>
          </div>
        </FormControls>

        <div class="form-actions">
          <button type="button" class="fluent-button button-secondary" @click="closeModal">Отмена</button>
          <button 
            type="submit" 
            class="fluent-button button-primary"
            :disabled="hasValidationErrors"
          >
            {{ isEditMode ? 'Сохранить изменения' : 'Создать' }}
          </button>
        </div>
      </form>
    </CommonModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PageToolbar from '~/components/common/page_toolbar.vue'
import FilterBar from '~/components/common/filter_bar.vue'
import EmptyState from '~/components/common/empty_state.vue'
import CommonModal from '~/components/common/common_modal.vue'
import FormControls from '~/components/common/form_controls.vue'

const companies = ref<any[]>([
  { id: 1, name: 'ООО ДорСтрой', inn: '7707083893', kpp: '773601001', address: 'г. Москва, ул. Ленина, д. 10', bank_account: '40702810900000001234', bic: '044525225' }
])
const searchQuery = ref('')
const error = ref<string | null>(null)

const isModalOpen = ref(false)
const isEditMode = ref(false)
const currentCompanyId = ref<number | null>(null)

const form = ref({
  name: '',
  inn: '',
  kpp: '',
  address: '',
  bank_account: '',
  bic: ''
})

const filteredCompanies = computed(() => {
  if (!searchQuery.value) return companies.value
  const q = searchQuery.value.toLowerCase()
  return companies.value.filter(c => 
    c.name.toLowerCase().includes(q) || 
    (c.inn && c.inn.includes(q))
  )
})

const innError = computed(() => {
  if (!form.value.inn) return ''
  const digitsOnly = form.value.inn.replace(/\D/g, '')
  if (digitsOnly !== form.value.inn) return 'ИНН должен состоять только из цифр'
  if (form.value.inn.length !== 10 && form.value.inn.length !== 12) {
    return `Длина ИНН должна быть 10 или 12 цифр (сейчас: ${form.value.inn.length})`
  }
  return ''
})

const kppError = computed(() => {
  if (!form.value.kpp) return ''
  const digitsOnly = form.value.kpp.replace(/\D/g, '')
  if (digitsOnly !== form.value.kpp) return 'КПП должен состоять только из цифр'
  if (form.value.kpp.length !== 9) {
    return `Длина КПП должна быть ровно 9 цифр (сейчас: ${form.value.kpp.length})`
  }
  return ''
})

const addressError = computed(() => {
  if (!form.value.address) return ''
  if (form.value.address.length < 5) {
    return 'Юридический адрес должен содержать минимум 5 символов'
  }
  return ''
})

const bicError = computed(() => {
  if (!form.value.bic) return ''
  const digitsOnly = form.value.bic.replace(/\D/g, '')
  if (digitsOnly !== form.value.bic) return 'БИК должен состоять только из цифр'
  if (form.value.bic.length !== 9) {
    return `Длина БИК должна быть ровно 9 цифр (сейчас: ${form.value.bic.length})`
  }
  return ''
})

const bankAccountError = computed(() => {
  if (!form.value.bank_account) return ''
  const digitsOnly = form.value.bank_account.replace(/\D/g, '')
  if (digitsOnly !== form.value.bank_account) return 'Расчетный счет должен состоять только из цифр'
  if (form.value.bank_account.length !== 20) {
    return `Длина р/с должна быть ровно 20 цифр (сейчас: ${form.value.bank_account.length})`
  }
  return ''
})

const hasValidationErrors = computed(() => {
  return !!(innError.value || kppError.value || addressError.value || bicError.value || bankAccountError.value)
})

const openModal = (company: any | null = null) => {
  error.value = null
  if (company) {
    isEditMode.value = true
    currentCompanyId.value = company.id
    form.value = { ...company }
  } else {
    isEditMode.value = false
    currentCompanyId.value = null
    form.value = { name: '', inn: '', kpp: '', address: '', bank_account: '', bic: '' }
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const handleSubmit = () => {
  if (hasValidationErrors.value) return

  if (isEditMode.value && currentCompanyId.value) {
    const idx = companies.value.findIndex(c => c.id === currentCompanyId.value)
    if (idx !== -1) companies.value[idx] = { ...companies.value[idx], ...form.value }
  } else {
    companies.value.push({
      id: Date.now(),
      ...form.value
    })
  }
  closeModal()
}

const handleDelete = (id: number) => {
  if (confirm('Вы уверены, что хотите удалить этого контрагента?')) {
    companies.value = companies.value.filter(c => c.id !== id)
  }
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
.max-width-address {
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sub-text {
  font-size: 11px;
  color: #797979;
  margin-top: 2px;
}
.text-right {
  text-align: right;
}
.font-semibold {
  font-weight: 600;
}
.text-blue {
  color: #0078d4;
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