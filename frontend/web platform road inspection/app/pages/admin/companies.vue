<template>
  <div class="admin-page-layout">
    <div class="fluent-toolbar">
      <div>
        <h1 class="page-title">🏢 Справочник контрагентов и компаний</h1>
        <p class="page-subtitle">Редактирование реквизитов (ИНН/КПП, БИК) и расчетных счетов подрядчиков</p>
      </div>
      <button class="fluent-button button-primary" @click="openModal(null)">
        ➕ Добавить контрагента
      </button>
    </div>

    <div class="filter-bar">
      <input v-model="searchQuery" placeholder="Поиск по названию или ИНН..." class="fluent-input main-search" />
    </div>

    <div class="table-container">
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
              <div class="sub-text">{{ company.bank_name }} (БИК: {{ company.bic || '—' }})</div>
            </td>
            <td class="text-right">
              <button class="action-btn edit-btn" @click="openModal(company)">✏️</button>
              <button class="action-btn delete-btn" @click="handleDelete(company.id)">❌</button>
            </td>
          </tr>
          <tr v-if="filteredCompanies.length === 0">
            <td colspan="5" class="empty-row">Компании не внесены в базу данных.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="fluent-modal-overlay">
      <div class="fluent-modal-window">
        <div class="modal-header">
          <h3>{{ isEditMode ? 'Изменение данных контрагента' : 'Регистрация нового юридического лица' }}</h3>
          <button class="close-modal-btn" @click="closeModal">✕</button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-grid">
            <div class="form-field full-width">
              <label>Полное наименование организации *</label>
              <input v-model="form.name" type="text" required placeholder="ООО МосСпецСтрой" class="fluent-input" />
            </div>

            <div class="form-field">
              <label>ИНН</label>
              <input v-model="form.inn" type="text" maxlength="20" class="fluent-input" />
            </div>
            <div class="form-field">
              <label>КПП</label>
              <input v-model="form.kpp" type="text" maxlength="20" class="fluent-input" />
            </div>

            <div class="form-field full-width">
              <label>Юридический / Фактический адрес</label>
              <input v-model="form.address" type="text" placeholder="г. Москва, ул. Ленина, д. 10" class="fluent-input" />
            </div>

            <div class="form-field">
              <label>Расчетный счет</label>
              <input v-model="form.bank_account" type="text" maxlength="30" class="fluent-input" />
            </div>
            <div class="form-field">
              <label>БИК</label>
              <input v-model="form.bic" type="text" maxlength="20" class="fluent-input" />
            </div>

            <div class="form-field full-width">
              <label>Наименование банка</label>
              <input v-model="form.bank_name" type="text" placeholder="ПАО Сбербанк" class="fluent-input" />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="fluent-button button-secondary" @click="closeModal">Отмена</button>
            <button type="submit" class="fluent-button button-primary" :disabled="isLoading">
              {{ isEditMode ? 'Сохранить реквизиты' : 'Добавить в реестр' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCompany } from '~/composables/useCompany';
import type { Company } from '~/types/company';

const { companies, isLoading, fetchCompanies, createCompany, updateCompany, deleteCompany } = useCompany();

const searchQuery = ref('');
const isModalOpen = ref(false);
const isEditMode = ref(false);
const selectedCompanyId = ref<number | null>(null);

const form = ref({
  name: '',
  inn: '',
  kpp: '',
  address: '',
  bank_account: '',
  bank_name: '',
  bic: ''
});

onMounted(() => {
  fetchCompanies();
});

const filteredCompanies = computed(() => {
  return companies.value.filter(c => {
    return c.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
           (c.inn && c.inn.includes(searchQuery.value));
  });
});

const openModal = (company: Company | null) => {
  if (company) {
    isEditMode.value = true;
    selectedCompanyId.value = company.id;
    form.value = {
      name: company.name,
      inn: company.inn || '',
      kpp: company.kpp || '',
      address: company.address || '',
      bank_account: company.bank_account || '',
      bank_name: company.bank_name || '',
      bic: company.bic || ''
    };
  } else {
    isEditMode.value = false;
    selectedCompanyId.value = null;
    form.value = { name: '', inn: '', kpp: '', address: '', bank_account: '', bank_name: '', bic: '' };
  }
  isModalOpen.value = true;
};

const closeModal = () => { isModalOpen.value = false; };

const handleSubmit = async () => {
  if (isEditMode.value && selectedCompanyId.value) {
    await updateCompany(selectedCompanyId.value, form.value);
  } else {
    await createCompany(form.value);
  }
  fetchCompanies();
  closeModal();
};

const handleDelete = async (id: number) => {
  if (confirm('Удалить компанию? Проверьте, что с ней не связаны действующие контракты.')) {
    await deleteCompany(id);
  }
};
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