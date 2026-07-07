import type { ApiResponse } from "~/types/api";
import type { Act, ActCreate, ActUpdate } from "~/types/act";

export function useAct() {
  const acts = ref<Act[]>([]);
  const currentAct = ref<Act | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const fetchActs = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act[]>>(`/Act/`, {
        method: "GET",
      });
      acts.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchAct = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act>>(`/Act/${id}`, {
        method: "GET",
      });
      currentAct.value = response.data;
    } catch (err: any) {
      error.value =
        err.data?.detail || "Ошибка при загрузке данных о своём пользователе";
    } finally {
      isLoading.value = false;
    }
  };

  const createAct = async (payload: ActCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act>>("/Act", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: { data: payload },
      });
      const newUser = response.data;
      acts.value.push(newUser);
      return newUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateAct = async (
    id: number,
    payload: ActUpdate,
  ): Promise<Act | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act>>(`/users/${id}`, {
        method: "PATCH",
        body: payload,
      });
      const updatedUser = response.data;
      // Локально обновляем массив, чтобы избежать лишнего запроса к БД
      const index = acts.value.findIndex((u) => u.id === id);
      if (index !== -1) {
        acts.value[index] = { ...acts.value[index], ...updatedUser };
      }
      if (currentAct.value?.id === id) {
        currentAct.value = { ...currentAct.value, ...updatedUser };
      }

      return updatedUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteAct = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    clearError();
    try {
      await apiFetch(`/Act/${id}`, {
        method: "DELETE",
      });
      // Локально удаляем из стейта
      acts.value = acts.value.filter((u) => u.id !== id);
      if (currentAct.value?.id === id) {
        currentAct.value = null;
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
    acts,
    isLoading,
    error,
    cleanError,
    fetchActs,
    fetchAct,
    createAct,
    updateAct,
    deleteAct,
  };
}
