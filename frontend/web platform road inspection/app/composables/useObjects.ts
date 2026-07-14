import type { ApiResponse } from "~/types/api";
import type { ObjectUpdate, ObjectCreate, ObjectItem } from "~/types/object";

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
      const response = await apiFetch<ApiResponse<Object[]>>("/object", {
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
      const response = await apiFetch<ApiResponse<Object>>(`/object/${id}`, {
        method: "GET",
      });
      currentObject.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке объекта";
    } finally {
      isLoading.value = false;
    }
  };

  const createObject = async (payload: ObjectCreate): Promise<ObjectItem | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<ObjectItem>>("/object/", {
        method: "POST",
        body: { data: payload },
      });

      const newObj = response.data;
      objects.value.push(newObj);
      return newObj;
    } catch (err: any) {
      console.error("422 Details:", err.data?.detail);
      error.value = Array.isArray(err.data?.detail)
        ? err.data.detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ')
        : err.data?.detail || "Ошибка при создании объекта";
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
      const response = await apiFetch<ApiResponse<Object>>(`/object/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: { data: payload },
      });
      const updatedObj = response.data;
      const index = objects.value.findIndex((u) => u === id);
      if (index !== -1) {
        objects.value[index] = { ...objects.value[index], ...updatedObj };
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
      await apiFetch(`/object/${id}`, {
        method: "DELETE",
      });
      objects.value = objects.value.filter((u) => u !== id);
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