<template>
  <div class="monitoring-page">
    <div v-if="isLoading" class="loading-state">
      Загрузка пользователей...
    </div>
    <div v-else class="content-wrapper">
      <div class="toolbar">
        <div class="toolbar-left">
          <h2 class="page-title">Пользователи системы</h2>
          <!-- <span class="objects-count">Всего: {{ filteredUsers.length }}</span> -->
          <span class="objects-count">Всего: {{ users?.length ?? 0 }}</span>
        </div>
        
        <div class="toolbar-actions">
          <div class="fluent-pivot">
            <button 
              v-for="role in roles" 
              :key="role.value"
              class="pivot-item"
              :class="{ active: currentFilter === role.value }"
              @click="currentFilter = role.value"
            >
              {{ role.label }}
            </button>
          </div>
          
          <NuxtLink to="/users/create" class="btn-primary">
            <span class="btn-icon">＋</span> Добавить пользователя
          </NuxtLink>
        </div>
      </div>

      <div class="users-container" v-if="filteredUsers.length > 0">
        <table class="fluent-table">
          <thead>
            <tr>
              <th>ФИО пользователя</th>
              <th>Роль в системе</th>
              <th>Организация</th>
              <th>Email / Логин</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td class="user-name-cell">
                <div class="user-avatar">{{ user.username.charAt(0) }}</div>
                <div>
                  <div class="font-semibold">{{ user.username }}</div>
                  <div class="text-muted">{{ user.position }}</div>
                </div>
              </td>
              <td>{{ user.role }}</td>
              <td>{{ user.company }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span class="status-badge" :class="user.status">
                  {{ user.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>Пользователи не найдены</h3>
        <p>Попробуйте изменить параметры фильтрации ролей.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUser } from '~/composables/useUser'
import type { UserUpdate } from '~/types/user'

const roles = [
  { label: 'Все', value: 'all' },
  { label: 'Пользователь', value: 'user' },
  { label: 'Администраторы', value: 'admin' },
  { label: 'Аудит', value: 'viewer' },  // Аудит это типо глобальная роль viewer
]

// Извлекаем нужные состояния и методы из нашего композбла
const { 
  users, 
  isLoading, 
  error, 
  cleanError,
  fetchUsers,
  updateUser, 
  deleteUser,
} = useUser()

onMounted(async () => {
  await fetchUsers()
})

const handleUpdate = async (id: string, payload: UserUpdate) => {
  if (confirm('Вы уверены, что хотите обновить данные этого пользователя?')) {
    await updateUser(id, payload)
  }
}

// Обработчик удаления юзера
const handleDelete = async (id: string) => {
  if (confirm('Вы уверены, что хотите удалить этого пользователя?')) {
    await deleteUser(id)
  }
}



const currentFilter = ref('all')

const filteredUsers = computed(() => {

  if (currentFilter.value === 'all') {
    return users.value
  }

  return users.value.filter(u => u.role === currentFilter.value)
})

// const filteredUsers = computed(() => {
//   if (currentFilter.value === 'all') return users.value
//   return users.value.filter(u => u.role === currentFilter.value)
// })

// const mockUsers = ref([
//   {
//     id: 1,
//     name: 'Иванов Иван Иванович',
//     position: 'Главный специалист',
//     role: 'admin',
//     roleLabel: 'Администратор',
//     company: 'ГБУ Автомобильные дороги',
//     email: 'ivanov.ii@uds.mos.ru',
//     status: 'active'
//   },
//   {
//     id: 2,
//     name: 'Петров Петр Петрович',
//     position: 'Ведущий инженер технадзора',
//     role: 'user',
//     roleLabel: 'Технический надзор',
//     company: 'АО Мосинжпроект',
//     email: 'petrov.pp@mosinzh.ru',
//     status: 'active'
//   },
//   {
//     id: 3,
//     name: 'Сидоров Сидор Сергеевич',
//     position: 'Начальник участка',
//     role: 'user',
//     roleLabel: 'Подрядчик',
//     company: 'ООО ТехСтрой',
//     email: 'sidorov@techstroy.ru',
//     status: 'active'
//   }
// ])

// const filteredUsers = computed(() => {
//   if (currentFilter.value === 'all') return mockUsers.value
//   return mockUsers.value.filter(u => u.role === currentFilter.value)
// })


</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: var(--fluent-font, sans-serif);
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

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 20px;
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
  left: 0;
  right: 0;
  height: 2px;
  background-color: #0078d4;
}

.btn-primary {
  background-color: #0078d4;
  color: #ffffff;
  border: 1px solid transparent;
  height: 32px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}
.btn-primary:hover { background-color: #106ebe; }

.users-container {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.fluent-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.fluent-table th {
  background: #fafafa;
  padding: 10px 16px;
  font-weight: 600;
  color: #242424;
  border-bottom: 1px solid #eaeaea;
}

.fluent-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f3f3;
  color: #242424;
  vertical-align: middle;
}

.fluent-table tr:last-child td {
  border-bottom: none;
}

.fluent-table tr:hover td {
  background-color: #fafafa;
}

.user-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background-color: #eaf4ff;
  color: #0078d4;
  font-weight: 600;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.font-semibold { font-weight: 600; }
.text-muted { color: #616161; font-size: 11px; margin-top: 2px; }

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}
.status-badge.active { background: #dfefe1; color: #107c41; }
.status-badge.blocked { background: #fde7e9; color: #a80000; }

.empty-state {
  text-align: center;
  padding: 60px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px dashed #c5c9d1;
  color: #616161;
}
.empty-icon { font-size: 36px; margin-bottom: 12px; }
.empty-state h3 { margin: 0 0 6px 0; color: #242424; }
.empty-state p { margin: 0; font-size: 13px; }
</style>