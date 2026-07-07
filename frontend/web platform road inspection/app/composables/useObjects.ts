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
      const response = await apiFetch<ApiResponse<Object[]>>(`/Object/`, {
        method: "GET",
      });
      objects.value = response.data;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при загрузке пользователей";
    } finally {
      isLoading.value = false;
    }
  };

  const fetchObject = async (id: number) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object>>(`/Object/${id}`, {
        method: "GET",
      });
      currentObject.value = response.data;
    } catch (err: any) {
      error.value =
        err.data?.detail || "Ошибка при загрузке данных о своём пользователе";
    } finally {
      isLoading.value = false;
    }
  };

  const createObject = async (payload: ObjectCreate) => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object>>("/Object", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: { data: payload },
      });
      const newUser = response.data;
      objects.value.push(newUser);
      return newUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при создании пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const updateObject = async (
    id: number,
    payload: ObjectUpdate,
  ): Promise<Object | null> => {
    isLoading.value = true;
    cleanError();
    try {
      const response = await apiFetch<ApiResponse<Object>>(`/users/${id}`, {
        method: "PATCH",
        body: payload,
      });
      const updatedUser = response.data;
      // Локально обновляем массив, чтобы избежать лишнего запроса к БД
      const index = objects.value.findIndex((u) => u.id === id);
      if (index !== -1) {
        objects.value[index] = { ...objects.value[index], ...updatedUser };
      }
      if (currentObject.value?.id === id) {
        currentObject.value = { ...currentObject.value, ...updatedUser };
      }

      return updatedUser;
    } catch (err: any) {
      error.value = err.data?.detail || "Ошибка при обновлении пользователя";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteObject = async (id: number): Promise<boolean> => {
    isLoading.value = true;
    clearError();
    try {
      await apiFetch(`/Object/${id}`, {
        method: "DELETE",
      });
      // Локально удаляем из стейта
      objects.value = objects.value.filter((u) => u.id !== id);
      if (currentObject.value?.id === id) {
        currentObject.value = null;
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
    objects,
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
