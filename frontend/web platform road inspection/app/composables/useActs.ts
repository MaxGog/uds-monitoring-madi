import type { ApiResponse } from "~/types/api";
import type { Act, ActCreate, ActUpdate } from "~/types/act";

export function useActs() {
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
      const response = await apiFetch<ApiResponse<Act[]>>("/act/", {
        method: "GET",
      });
      acts.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке актов";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchAct = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act>>(`/act/${id}`, {
        method: "GET",
      });
      currentAct.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке информации об акте";
    } finally {
      isLoading.value = false;
    }
  };

  const createAct = async (payload: ActCreate): Promise<Act | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act>>("/act/", {
        method: "POST",
        body: { data: payload },
      });
      const newAct = response.data;
      acts.value.unshift(newAct);
      return newAct;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании акта";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateAct = async (
    id: number,
    payload: ActUpdate
  ): Promise<Act | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Act>>(`/act/${id}`, {
        method: "PATCH",
        body: { data: payload },
      });
      const updated = response.data;

      const index = acts.value.findIndex((a) => a.id === id);
      if (index !== -1) {
        acts.value[index] = { ...acts.value[index], ...updated };
      }
      if (currentAct.value?.id === id) {
        currentAct.value = { ...currentAct.value, ...updated };
      }

      return updated;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении акта";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteAct = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    cleanError();
    try {
      await apiFetch(`/act/${id}`, {
        method: "DELETE",
      });

      acts.value = acts.value.filter((a) => a.id !== id);
      if (currentAct.value?.id === id) {
        currentAct.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при удалении акта";
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    acts,
    currentAct,
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