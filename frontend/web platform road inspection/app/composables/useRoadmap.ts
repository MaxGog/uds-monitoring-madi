import type { ApiResponse } from "~/types/api";
import type { Roadmap } from "~/types/roadmap";

const PHASE_TO_BACKEND: Record<string, string> = {
  "Разработка проекта": "project_development",
  "Подготовка ИД": "preparation",
  "Проверка согласований": "checking",
  "Утверждено": "approved",
};

const PHASE_TO_FRONTEND: Record<string, 'Разработка проекта' | 'Подготовка ИД' | 'Проверка согласований' | 'Утверждено'> = {
  "project_development": "Разработка проекта",
  "preparation": "Подготовка ИД",
  "checking": "Проверка согласований",
  "approved": "Утверждено",
};

const RISK_TO_BACKEND: Record<string, string> = {
  "Низкий": "low",
  "Средний": "medium",
  "Высокий": "high",
};

const RISK_TO_FRONTEND: Record<string, 'Низкий' | 'Средний' | 'Высокий'> = {
  "low": "Низкий",
  "medium": "Средний",
  "high": "Высокий",
};

export function useRoadmap() {
  const roadmaps = ref<Roadmap[]>([]);
  const currentRoadmap = ref<Roadmap | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const mapRoadmapFromBackend = (backendData: any): Roadmap => {
    if (!backendData) return backendData;

    const rawPhase = backendData.phase || "project_development";
    const mappedPhase = PHASE_TO_FRONTEND[rawPhase] || "Разработка проекта";

    const rawRisk = backendData.risk || "low";
    const mappedRisk = RISK_TO_FRONTEND[rawRisk] || "Низкий";

    return {
      ...backendData,
      phase: mappedPhase,
      risk: mappedRisk,
      responsibleManager: backendData.responsibleManager || backendData.manager || "Не назначен",
      manager: backendData.manager || backendData.responsibleManager || "Не назначен",
      budget: backendData.budget || (backendData.cost ? `${backendData.cost.toLocaleString('ru-RU')} ₽` : "0 ₽"),
      milestones: (backendData.milestones || []).map((m: any) => ({
        ...m,
        status: m.status === 'in_schedule' ? 'В графике' :
          m.status === 'attention' ? 'Внимание' :
            m.status === 'critical' ? 'Критический сдвиг' :
              m.status === 'completed' ? 'Выполнено' : m.status
      }))
    };
  };

  const fetchRoadmaps = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<any[]>>(`/roadmap/`, {
        method: "GET",
      });
      roadmaps.value = (response.data || []).map(mapRoadmapFromBackend);
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке дорожных карт";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchRoadmap = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<any>>(`/roadmap/${id}`, {
        method: "GET",
      });
      currentRoadmap.value = mapRoadmapFromBackend(response.data);
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке данных о дорожной карте";
    } finally {
      isLoading.value = false;
    }
  };

  const createRoadmap = async (payload: Roadmap): Promise<Roadmap | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const backendPayload: any = { ...payload };

      if (payload.phase) {
        backendPayload.phase = PHASE_TO_BACKEND[payload.phase] || payload.phase;
      }
      if (payload.risk) {
        backendPayload.risk = RISK_TO_BACKEND[payload.risk] || payload.risk;
      }

      const response = await apiFetch<ApiResponse<any>>(`/roadmap/`, {
        method: "POST",
        body: { data: backendPayload },
      });

      const newRoadmap = mapRoadmapFromBackend(response.data);
      roadmaps.value.push(newRoadmap);
      return newRoadmap;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании дорожной карты";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteRoadmap = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    cleanError();
    try {
      await apiFetch(`/roadmap/${id}`, {
        method: "DELETE",
      });
      roadmaps.value = roadmaps.value.filter((r) => r.id !== id);
      if (currentRoadmap.value?.id === id) {
        currentRoadmap.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при удалении дорожной карты";
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    roadmaps,
    currentRoadmap,
    isLoading,
    error,
    fetchRoadmaps,
    fetchRoadmap,
    createRoadmap,
    deleteRoadmap,
  };
}