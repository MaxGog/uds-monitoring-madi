import type { ApiResponse } from "~/types/api";
import type { Work, WorkCreate, WorkUpdate } from "~/types/work";

const STATUS_TO_BACKEND: Record<string, string> = {
  "Проверка объемов": "pending",
  "Анализ отклонений": "in_progress",
  "Приемка работ": "verified",
  "Завершено": "completed",
};

const STATUS_TO_FRONTEND: Record<string, 'Проверка объемов' | 'Анализ отклонений' | 'Приемка работ' | 'Завершено'> = {
  "pending": "Проверка объемов",
  "assigned": "Проверка объемов",
  "in_progress": "Анализ отклонений",
  "paused": "Анализ отклонений",
  "verified": "Приемка работ",
  "completed": "Завершено",
  "canceled": "Завершено",
  "expired": "Завершено",
  "failed": "Завершено",
};

export function useWork() {
  const works = ref<Work[]>([]);
  const currentWork = ref<Work | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const mapWorkFromBackend = (backendData: any): Work => {
    if (!backendData) return backendData;

    const rawStatus = backendData.status || backendData.stage;
    const mappedStage = STATUS_TO_FRONTEND[rawStatus] || "Проверка объемов";

    const totalBudget = Number(backendData.cost || 0);
    const spentBudget = Number(backendData.budgetSpent || 0);
    const remainingBudget = totalBudget - spentBudget;

    return {
      id: backendData.id,
      objectName: backendData.title || backendData.objectName || "Без названия",
      region: backendData.region || "Не указан",
      stage: mappedStage,
      progress: backendData.progress !== undefined ? `${backendData.progress}%` : "0%",
      manager: backendData.manager || "Не назначен",
      updatedAt: backendData.updated_at
        ? new Date(backendData.updated_at).toLocaleDateString("ru-RU")
        : new Date().toLocaleDateString("ru-RU"),
      nextAction: backendData.nextAction || "Нет запланированных действий",
      hasDeviationAlert: !!backendData.hasDeviationAlert,

      budgetAllocation: {
        total: String(totalBudget),
        spent: String(spentBudget),
        remaining: String(remainingBudget)
      },

      historyLog: backendData.historyLog || []
    };
  };

  const fetchWorks = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<any[]>>(`/work/`, {
        method: "GET",
      });
      works.value = (response.data || []).map(mapWorkFromBackend);
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке мониторинга работ";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchWork = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<any>>(`/work/${id}`, {
        method: "GET",
      });
      currentWork.value = mapWorkFromBackend(response.data);
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке данных об объекте";
    } finally {
      isLoading.value = false;
    }
  };

  const createWork = async (payload: WorkCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const dbStatus = STATUS_TO_BACKEND[payload.stage] || "UNDER_REVIEW";

      const backendPayload = {
        title: payload.objectName,
        status: dbStatus,
        cost: payload.budgetTotal || 0,
        object_id: null,
        contractor_id: null
      };

      const response = await apiFetch<ApiResponse<any>>("/work/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: { data: backendPayload },
      });

      const newWork = mapWorkFromBackend(response.data);
      works.value.push(newWork);
      return newWork;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при инициализации мониторинга";
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
      const backendPayload: Record<string, any> = {};

      if (payload.objectName !== undefined) {
        backendPayload.title = payload.objectName;
      }
      if (payload.stage !== undefined) {
        backendPayload.status = STATUS_TO_BACKEND[payload.stage] || "UNDER_REVIEW";
      }
      if (payload.budgetTotal !== undefined) {
        backendPayload.cost = payload.budgetTotal;
      }

      const response = await apiFetch<ApiResponse<any>>(`/work/${id}`, {
        method: "PATCH",
        body: { data: backendPayload },
      });

      const updatedWork = mapWorkFromBackend(response.data);

      const index = works.value.findIndex((w) => w.id === id);
      if (index !== -1) {
        works.value[index] = { ...works.value[index], ...updatedWork };
      }
      if (currentWork.value?.id === id) {
        currentWork.value = { ...currentWork.value, ...updatedWork };
      }

      return updatedWork;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении статуса работы";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteWork = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    cleanError();
    try {
      await apiFetch(`/work/${id}`, {
        method: "DELETE",
      });
      works.value = works.value.filter((w) => w.id !== id);
      if (currentWork.value?.id === id) {
        currentWork.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при удалении объекта из мониторинга";
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    works,
    currentWork,
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