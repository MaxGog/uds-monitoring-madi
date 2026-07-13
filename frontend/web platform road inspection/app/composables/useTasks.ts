import { ref } from 'vue'
import type { ApiResponse } from "~/types/api"
import type { Task, TaskCreate, TaskUpdate } from "~/types/task"

export function useTasks() {
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)

  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const cleanError = () => {
    error.value = null
  }

  const fetchTasks = async () => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<Task[]>>('/task/', {
        method: "GET",
      })
      tasks.value = response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке задач"
    } finally {
      isLoading.value = false
    }
  }

  const fetchTask = async (id: number) => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<Task>>(`/task/${id}`, {
        method: "GET",
      })
      currentTask.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке данных о задаче"
      return null
    } finally {
      isLoading.value = false
    }
  }

  const createTask = async (payload: TaskCreate): Promise<Task | null> => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<Task>>('/task/', {
        method: "POST",
        body: { data: payload }
      })
      const newTask = response.data
      tasks.value.unshift(newTask)
      return newTask
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании задачи"
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateTask = async (id: number, payload: TaskUpdate): Promise<Task | null> => {
    isLoading.value = true
    cleanError()
    try {
      const response = await apiFetch<ApiResponse<Task>>(`/task/${id}`, {
        method: "PATCH",
        body: { data: payload }
      })
      const updatedTask = response.data

      const index = tasks.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], ...updatedTask }
      }
      if (currentTask.value?.id === id) {
        currentTask.value = { ...currentTask.value, ...updatedTask }
      }

      return updatedTask
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении задачи"
      return null
    } finally {
      isLoading.value = false
    }
  }

  const deleteTask = async (id: number): Promise<boolean> => {
    isLoading.value = true
    cleanError()
    try {
      await apiFetch(`/task/${id}`, {
        method: "DELETE",
      })
      tasks.value = tasks.value.filter((t) => t.id !== id)
      if (currentTask.value?.id === id) {
        currentTask.value = null
      }
      return true
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при удалении задачи"
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    tasks,
    currentTask,
    isLoading,
    error,
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
    cleanError
  }
}