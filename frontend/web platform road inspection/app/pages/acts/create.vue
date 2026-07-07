<template>
  <div class="create-act-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">Первичный ввод объёмов / Создание Акта</h2>
        <span class="page-subtitle">Двухэтапная валидация данных ИС (Интеграция со скриптом Code.gs)</span>
      </div>
      <div class="toolbar-actions">
        <NuxtLink to="/acts" class="fluent-button button-secondary">
          Отмена
        </NuxtLink>
        <button class="fluent-button button-primary" @click="handleSubmit">
          Сформировать акт
        </button>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="form-layout">
      
      <div class="form-section">
        <h3 class="section-title">Основные реквизиты объекта и контракта</h3>
        <div class="form-grid">
          <div class="form-field full-width">
            <label>Наименование объекта (ОДХ)</label>
            <input 
              v-model="form.objectName" 
              type="text" 
              required 
              placeholder="Например: Капитальный ремонт ул. Тверская" 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Государственный контракт / Основание</label>
            <input 
              v-model="form.contractNumber" 
              type="text" 
              required 
              placeholder="ГК-2026/..." 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Территориальное управление (Округ)</label>
            <select v-model="form.region" required class="fluent-select">
              <option value="" disabled>Выберите округ</option>
              <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <div class="form-field">
            <label>Генеральный подрядчик</label>
            <input 
              v-model="form.contractor" 
              type="text" 
              required 
              placeholder="ООО, АО или ГБУ" 
              class="fluent-input"
            />
          </div>

          <div class="form-field">
            <label>Тип документационного контроля</label>
            <select v-model="form.type" class="fluent-select">
              <option value="Приёмка работ">Приёмка работ</option>
              <option value="Технический контроль">Технический контроль</option>
              <option value="Инспекция объемов">Инспекция объемов</option>
            </select>
          </div>

          <div class="form-field full-width">
            <label>Общая плановая сумма контракта (₽)</label>
            <input 
              v-model="form.planAmount" 
              type="text" 
              placeholder="15 000 000 ₽" 
              class="fluent-input"
            />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Контролируемые технологические объёмы (Диапазон C:M)</h3>
        <p class="section-desc">Строки со значениями 0 или пусто согласно логике бэкенда будут исключены из печатной формы Google Docs.</p>
        
        <div class="volumes-table-wrapper">
          <table class="volumes-table">
            <thead>
              <tr>
                <th>Наименование технологической операции / Контрольной позиции</th>
                <th width="140">План</th>
                <th width="140">Факт</th>
                <th width="100">Ед. изм.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(vol, index) in form.volumes" :key="index">
                <td class="vol-name">{{ vol.name }}</td>
                <td>
                  <input v-model.number="vol.plan" type="number" min="0" step="any" class="fluent-table-input" />
                </td>
                <td>
                  <input v-model.number="vol.fact" type="number" min="0" step="any" class="fluent-table-input" />
                </td>
                <td class="vol-unit">{{ vol.unit }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Дополнительные сведения</h3>
        <div class="form-field full-width">
          <label>Примечания инспектора / Журнал разногласий</label>
          <textarea v-model="form.notes" rows="3" placeholder="Укажите замечания или комментарии к объемам..." class="fluent-textarea"></textarea>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMockData } from '~/composables/useMockData'

const router = useRouter()
const { acts, regions } = useMockData()

const form = reactive({
  objectName: '',
  contractNumber: '',
  region: 'ЦАО',
  contractor: '',
  type: 'Приёмка работ',
  planAmount: '',
  notes: '',
  volumes: [
    { name: '1. Фрезерование асфальтобетонного покрытия', plan: 0, fact: 0, unit: 'м³' },
    { name: '2. Укладка нижнего слоя покрытия из горячих смесей', plan: 0, fact: 0, unit: 'т' },
    { name: '3. Укладка upper слоя (ЩМА-16) на ПБВ', plan: 0, fact: 0, unit: 'т' },
    { name: '4. Демонтаж и установка бортового камня', plan: 0, fact: 0, unit: 'п.м.' },
    { name: '5. Ремонт и регулировка высотного положения люков колодцев', plan: 0, fact: 0, unit: 'шт' },
    { name: '6. Устройство подстилающих слоев из песка', plan: 0, fact: 0, unit: 'м³' },
    { name: '7. Устройство щебеночного основания', plan: 0, fact: 0, unit: 'м³' },
    { name: '8. Нанесение дорожной разметки термопластиком', plan: 0, fact: 0, unit: 'п.м.' }
  ]
})

const handleSubmit = () => {
  const totalFactItems = form.volumes.reduce((sum, v) => sum + (v.fact || 0), 0)
  const simulatedAmount = totalFactItems > 0 
    ? (totalFactItems * 4500).toLocaleString('ru-RU') + ' ₽' 
    : '0 ₽'

  const newId = acts.value.length ? Math.max(...acts.value.map(a => a.id)) + 1 : 1
  const actNumber = `АКТ-2026-${String(newId).padStart(3, '0')}`

  const newAct = {
    id: newId,
    number: actNumber,
    objectName: form.objectName,
    type: form.type,
    date: new Date().toLocaleDateString('ru-RU'),
    contractor: form.contractor,
    status: 'На утверждении' as const,
    amount: simulatedAmount,
    signedBy: 'Иванов И. И.',
    notes: form.notes || 'Акт успешно инициализирован в системе.',
    region: form.region as any,
    contractNumber: form.contractNumber,
    planAmount: form.planAmount || simulatedAmount,
    vatAmount: (totalFactItems * 900).toLocaleString('ru-RU') + ' ₽',
    docUrl: '#',
    pdfUrl: '#',
    signDate: '—',
    volumes: form.volumes.filter(v => v.plan > 0 || v.fact > 0)
  }

  acts.value.unshift(newAct)
  router.push('/acts')
}
</script>

<style scoped>
.create-act-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 4px;
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
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--fluent-gray-100);
}

.page-subtitle {
  font-size: 12px;
  color: #616161;
  margin-top: 4px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.fluent-button {
  padding: 6px 18px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.1s, border-color 0.1s;
}

.button-secondary {
  background: #ffffff;
  border: 1px solid #d2d0ce;
  color: #323130;
}

.button-secondary:hover {
  background: #f3f2f1;
}

.button-primary {
  background: #0078d4;
  border: 1px solid #0078d4;
  color: #ffffff;
}

.button-primary:hover {
  background: #106ebe;
  border-color: #106ebe;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e1e3e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--fluent-gray-100);
  border-bottom: 1px solid #f3f2f1;
  padding-bottom: 8px;
}

.section-desc {
  font-size: 12px;
  color: #616161;
  margin: -12px 0 16px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.full-width {
  grid-column: span 2;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: #616161;
}

.fluent-input,
.fluent-select,
.fluent-textarea {
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 13px;
  font-family: inherit;
  background: #ffffff;
  color: var(--fluent-gray-100);
}

.fluent-input:focus,
.fluent-select:focus,
.fluent-textarea:focus {
  border-color: #0078d4;
  outline: none;
}

.volumes-table-wrapper {
  border: 1px solid #e1e3e8;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.volumes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.volumes-table th {
  background: #f3f4f6;
  padding: 10px 12px;
  font-weight: 600;
  color: #242424;
  border-bottom: 1px solid #e1e3e8;
}

.volumes-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.vol-name {
  color: var(--fluent-gray-100);
  font-weight: 500;
}

.vol-unit {
  color: #616161;
  font-size: 12px;
}

.fluent-table-input {
  width: 100%;
  border: 1px solid #d6d9dc;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 13px;
  box-sizing: border-box;
}

.fluent-table-input:focus {
  border-color: #0078d4;
  outline: none;
}
</style>