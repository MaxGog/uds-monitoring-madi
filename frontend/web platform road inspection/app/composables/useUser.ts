import { ref } from "vue"
import type { User, UserCreate, UserUpdate } from "~/types/user"
import type { ApiResponse } from "~/types/api"
import { apiFetch } from "#imports"

export function useUser() {
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)

  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const cleanError = () => {
    error.value = null
  }

  // Получить список всех пользователей
  const fetchUsers = async () => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User[]>>('/users/', {
        method: "GET",
      })
      users.value = response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей"
    } finally {
      isLoading.value = false
    }
  }

  // Получить профиль текущего авторизованного пользователя (/users/me)
  const fetchMe = async () => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>('/users/me', {
        method: "GET",
      })
      currentUser.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке вашего профиля"
      return null
    } finally {
      isLoading.value = false
    }
  }

  // Получить конкретного пользователя по ID
  const fetchUser = async (id: string) => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>(`/users/${id}`, {
        method: "GET",
      })
      currentUser.value = response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке данных пользователя"
    } finally {
      isLoading.value = false
    }
  }

  // Создать пользователя
  const createUser = async (payload: UserCreate): Promise<User | null> => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>('/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: { data: payload }
      })
      const newUser = response.data
      users.value.push(newUser)
      return newUser
    } catch (err: any) {
      console.error('Ошибка 422 / детальная ошибка:', err.data)
      error.value = typeof err.data?.detail === 'string'
        ? err.data.detail
        : 'Некорректные данные для создания пользователя'
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  // Обновить данные пользователя
  const updateUser = async (id: string, payload: UserUpdate): Promise<User | null> => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<User>>(`/users/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        // Обернули в { data: payload }, так как FastAPI ожидает BaseRequest[UserUpdateRequest]
        body: { data: payload }
      })
      const updatedUser = response.data

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

  // Удалить пользователя
  const deleteUser = async (id: string): Promise<boolean> => {
    isLoading.value = true
    cleanError() // Исправлено: было clearError()
    try {
      await apiFetch(`/users/${id}`, {
        method: 'DELETE'
      })
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
    fetchMe,
    fetchUser,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
  }
}