import type { ApiResponse } from "~/types/api";
import type { Roadmap, RoadmapCreate, RoadmapUpdate } from "~/types/roadmap";

export function useRoadmap() {
  const roadmaps = ref<Roadmap[]>([]);
  const currentRoadmap = ref<Roadmap | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const fetchRoadmaps = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Roadmap[]>>(`/Roadmap/`, {
        method: "GET",
      });
      roadmaps.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchRoadmap = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Roadmap>>(`/Roadmap/${id}`, {
        method: "GET",
      });
      currentRoadmap.value = response.data;
    } catch (err: any) {
      error.value =
        err.data?.detail || "Ошибка при загрузке данных о своём пользователе";
    } finally {
      isLoading.value = false;
    }
  };

  const createRoadmap = async (payload: RoadmapCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Roadmap>>("/Roadmap", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: { data: payload },
      });
      const newUser = response.data;
      roadmaps.value.push(newUser);
      return newUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateRoadmap = async (
    id: number,
    payload: RoadmapUpdate,
  ): Promise<Roadmap | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Roadmap>>(`/users/${id}`, {
        method: "PATCH",
        body: payload,
      });
      const updatedUser = response.data;
      // Локально обновляем массив, чтобы избежать лишнего запроса к БД
      const index = roadmaps.value.findIndex((u) => u.id === id);
      if (index !== -1) {
        roadmaps.value[index] = { ...roadmaps.value[index], ...updatedUser };
      }
      if (currentRoadmap.value?.id === id) {
        currentRoadmap.value = { ...currentRoadmap.value, ...updatedUser };
      }

      return updatedUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteRoadmap = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    clearError();
    try {
      await apiFetch(`/Roadmap/${id}`, {
        method: "DELETE",
      });
      // Локально удаляем из стейта
      roadmaps.value = roadmaps.value.filter((u) => u.id !== id);
      if (currentRoadmap.value?.id === id) {
        currentRoadmap.value = null;
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
    roadmaps,
    isLoading,
    error,
    cleanError,
    fetchRoadmaps,
    fetchRoadmap,
    createRoadmap,
    updateRoadmap,
    deleteRoadmap,
  };
}
