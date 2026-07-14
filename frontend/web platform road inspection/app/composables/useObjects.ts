import type { ApiResponse } from "~/types/api";
import type { Object, ObjectCreate, ObjectUpdate } from "~/types/object";

export function useObject() {
  const objects = ref<Object[]>([]);
  const currentObject = ref<Object | null>(null);

  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const cleanError = () => {
    error.value = null;
  };

  const fetchObjects = async () => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object[]>>("/monitoring/", {
        method: "GET",
      });
      objects.value = response.data || [];
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке объектов";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchObject = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object>>(`/monitoring/${id}`, {
        method: "GET",
      });
      currentObject.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке объекта";
    } finally {
      isLoading.value = false;
    }
  };

  const createObject = async (payload: ObjectCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object>>("/monitoring/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: { data: payload },
      });
      const newObj = response.data;
      if (newObj) {
        objects.value.push(newObj);
      }
      return newObj;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании объекта";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateObject = async (
    id: number,
    payload: ObjectUpdate
  ): Promise<Object | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object>>(`/monitoring/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: { data: payload },
      });
      const updatedObj = response.data;
      const index = objects.value.findIndex((u) => u.id === id);
      if (index !== -1) {
        objects.value[index] = { ...objects.value[index], ...updatedObj };
      }
      if (currentObject.value?.id === id) {
        currentObject.value = { ...currentObject.value, ...updatedObj };
      }

      return updatedObj;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении объекта";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteObject = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    cleanError();
    try {
      await apiFetch(`/monitoring/${id}`, {
        method: "DELETE",
      });
      objects.value = objects.value.filter((u) => u.id !== id);
      if (currentObject.value?.id === id) {
        currentObject.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при удалении объекта";
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    objects,
    currentObject,
    isLoading,
    error,
    cleanError,
    fetchObjects,
    fetchObject,
    createObject,
    updateObject,
    deleteObject,
  };
}