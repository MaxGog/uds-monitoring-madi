import type { ApiResponse } from "~/types/api";
import type { Work, WorkCreate, WorkUpdate } from "~/types/work";

export function useWork() {
  const works = ref<Work[]>([]);
  const currentWork = ref<Work | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const fetchWorks = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Work[]>>(`/Work/`, {
        method: "GET",
      });
      works.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchWork = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Work>>(`/Work/${id}`, {
        method: "GET",
      });
      currentWork.value = response.data;
    } catch (err: any) {
      error.value =
        err.data?.detail || "Ошибка при загрузке данных о своём пользователе";
    } finally {
      isLoading.value = false;
    }
  };

  const createWork = async (payload: WorkCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Work>>("/Work", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: { data: payload },
      });
      const newUser = response.data;
      works.value.push(newUser);
      return newUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateWork = async (
    id: number,
    payload: WorkUpdate,
  ): Promise<Work | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Work>>(`/users/${id}`, {
        method: "PATCH",
        body: payload,
      });
      const updatedUser = response.data;
      // Локально обновляем массив, чтобы избежать лишнего запроса к БД
      const index = works.value.findIndex((u) => u.id === id);
      if (index !== -1) {
        works.value[index] = { ...works.value[index], ...updatedUser };
      }
      if (currentWork.value?.id === id) {
        currentWork.value = { ...currentWork.value, ...updatedUser };
      }

      return updatedUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteWork = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    clearError();
    try {
      await apiFetch(`/Work/${id}`, {
        method: "DELETE",
      });
      // Локально удаляем из стейта
      works.value = works.value.filter((u) => u.id !== id);
      if (currentWork.value?.id === id) {
        currentWork.value = null;
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
    works,
    isLoading,
    error,
    cleanError,
    fetchWorks,
    fetchWork,
    createWork,
    updateWork,
    deleteWork,
  };
}
