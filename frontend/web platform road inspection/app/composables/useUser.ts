import { ref } from "vue"
import type { User, UserCreate, UserUpdate, ApiResponse } from "~/types/user"
import { apiFetch } from "#imports"


// Как то так выглядит типичный композабл на Nuxt. Примеры кода взяты с официальных гитхубов разрабов.
// Композаблы незываются через use как раз потому, что мы используем их где угодно и передаём стейты результатов на UI
export function useUser() {
  const users = ref<User[]>([]) // Это конкретные юзеры при пагинации
  const currentUser = ref<User | null>(null)

  const isLoading = ref<boolean>(false) // Вообще можно было бы как нибудь интегрировать паттерн Result
  const error = ref<string | null>(null)

  const cleanError = () => {
    error.value = null
  }

  const fetchUsers = async () => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User[]>>(`/users/`, {
        method: "GET",
      })
      users.value = response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей"
    } finally {
      isLoading.value = false
    }
  }

  const fetchUser = async (id: string) => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>(`/users/${id}`, {
        method: "GET",
      })
      currentUser.value = response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке данных о своём пользователе"
    } finally {
      isLoading.value = false
    }
  }

  const createUser = async (payload: UserCreate): Promise<User | null> => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>('/users', {
        method: 'POST',
        body: payload
      })
      const newUser = response.data
      users.value.push(newUser)
      return newUser
    } catch (err: any) {
      error.value = err.data?.detail || 'Ошибка при создании пользователя'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateUser = async (id: string, payload: UserUpdate): Promise<User | null> => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>(`/users/${id}`, {
        method: 'PATCH',
        body: payload
      })
      const updatedUser = response.data
      // Локально обновляем массив, чтобы избежать лишнего запроса к БД
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...updatedUser }
      }
      if (currentUser.value?.id === id) {
        currentUser.value = { ...currentUser.value, ...updatedUser }
      }

      return updatedUser
    } catch (err: any) {
      error.value = err.data?.detail || 'Ошибка при обновлении пользователя'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const deleteUser = async (id: string): Promise<boolean> => {
    isLoading.value = true
    clearError()
    try {
      await apiFetch(`/users/${id}`, {
        method: 'DELETE'
      })
      // Локально удаляем из стейта
      users.value = users.value.filter(u => u.id !== id)
      if (currentUser.value?.id === id) {
        currentUser.value = null
      }
      return true
    } catch (err: any) {
      error.value = err.data?.detail || 'Ошибка при удалении'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    users,
    currentUser,
    isLoading,
    error,
    cleanError,
    fetchUser,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
  }
}
