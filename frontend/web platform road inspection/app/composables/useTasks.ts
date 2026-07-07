import type { ApiResponse } from "~/types/api";
import type { Task, TaskCreate, TaskUpdate } from "~/types/task";

export function useTask() {
  const tasks = ref<Task[]>([]);
  const currentTask = ref<Task | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const fetchTasks = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Task[]>>(`/task/`, {
        method: "GET",
      });
      tasks.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchTask = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Task>>(`/task/${id}`, {
        method: "GET",
      });
      currentTask.value = response.data;
    } catch (err: any) {
      error.value =
        err.data?.detail || "Ошибка при загрузке данных о своём пользователе";
    } finally {
      isLoading.value = false;
    }
  };

  const createTask = async (payload: TaskCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Task>>("/task", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: { data: payload },
      });
      const newUser = response.data;
      tasks.value.push(newUser);
      return newUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateTask = async (
    id: number,
    payload: TaskUpdate,
  ): Promise<Task | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Task>>(`/users/${id}`, {
        method: "PATCH",
        body: payload,
      });
      const updatedUser = response.data;
      // Локально обновляем массив, чтобы избежать лишнего запроса к БД
      const index = tasks.value.findIndex((u) => u.id === id);
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], ...updatedUser };
      }
      if (currentTask.value?.id === id) {
        currentTask.value = { ...currentTask.value, ...updatedUser };
      }

      return updatedUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteTask = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    clearError();
    try {
      await apiFetch(`/task/${id}`, {
        method: "DELETE",
      });
      // Локально удаляем из стейта
      tasks.value = tasks.value.filter((u) => u.id !== id);
      if (currentTask.value?.id === id) {
        currentTask.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при удалении";
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    tasks,
    isLoading,
    error,
    cleanError,
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
  };
}
