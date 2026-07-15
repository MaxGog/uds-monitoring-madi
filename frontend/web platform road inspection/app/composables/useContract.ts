import type { ApiResponse } from "~/types/api";
import type { Contract, ContractCreate, ContractUpdate } from "~/types/contract";

export function useContract() {
    const contracts = ref<Contract[]>([]);
    const currentContract = ref<Contract | null>(null);
    const isLoading = ref<boolean>(false);
    const error = ref<string | null>(null);

    const clearError = () => { error.value = null; };

    const fetchContracts = async () => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Contract[]>>("/contract/", { method: "GET" });
            contracts.value = response.data || [];
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при загрузке контрактов";
        } finally {
            isLoading.value = false;
        }
    };

    const fetchContract = async (id: number) => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Contract>>(`/contract/${id}`, { method: "GET" });
            currentContract.value = response.data;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при загрузке данных контракта";
        } finally {
            isLoading.value = false;
        }
    };

    const createContract = async (payload: ContractCreate) => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Contract>>("/contract/", {
                method: "POST",
                body: { data: payload },
            });
            return response.data;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при создании контракта";
            return null;
        } finally {
            isLoading.value = false;
        }
    };

    const updateContract = async (id: number, payload: ContractUpdate) => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Contract>>(`/contract/${id}`, {
                method: "PATCH",
                body: { data: payload },
            });
            return response.data;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при обновлении контракта";
            return null;
        } finally {
            isLoading.value = false;
        }
    };

    const deleteContract = async (id: number): Promise<boolean> => {
        isLoading.value = true;
        clearError();
        try {
            await apiFetch(`/contract/${id}`, { method: "DELETE" });
            contracts.value = contracts.value.filter((c) => c.id !== id);
            return true;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при удалении контракта";
            return false;
        } finally {
            isLoading.value = false;
        }
    };

    return { contracts, currentContract, isLoading, error, fetchContracts, fetchContract, createContract, updateContract, deleteContract, clearError };
}