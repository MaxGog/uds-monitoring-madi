import type { ApiResponse } from "~/types/api";
import type { Company, CompanyCreate, CompanyUpdate } from "~/types/company";

export function useCompany() {
    const companies = ref<Company[]>([]);
    const currentCompany = ref<Company | null>(null);
    const isLoading = ref<boolean>(false);
    const error = ref<string | null>(null);

    const clearError = () => { error.value = null; };

    const fetchCompanies = async () => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Company[]>>("/company/", { method: "GET" });
            companies.value = response.data || [];
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при загрузке списка компаний";
        } finally {
            isLoading.value = false;
        }
    };

    const fetchCompany = async (id: number) => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Company>>(`/company/${id}`, { method: "GET" });
            currentCompany.value = response.data;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при получении данных компании";
        } finally {
            isLoading.value = false;
        }
    };

    const createCompany = async (payload: CompanyCreate) => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Company>>("/company/", {
                method: "POST",
                body: { data: payload },
            });
            return response.data;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при создании компании";
            return null;
        } finally {
            isLoading.value = false;
        }
    };

    const updateCompany = async (id: number, payload: CompanyUpdate) => {
        isLoading.value = true;
        clearError();
        try {
            const response = await apiFetch<ApiResponse<Company>>(`/company/${id}`, {
                method: "PATCH",
                body: { data: payload },
            });
            return response.data;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при обновлении компании";
            return null;
        } finally {
            isLoading.value = false;
        }
    };

    const deleteCompany = async (id: number): Promise<boolean> => {
        isLoading.value = true;
        clearError();
        try {
            await apiFetch(`/company/${id}`, { method: "DELETE" });
            companies.value = companies.value.filter((c) => c.id !== id);
            return true;
        } catch (err: any) {
            error.value = err.data?.detail || "Ошибка при удалении компании";
            return false;
        } finally {
            isLoading.value = false;
        }
    };

    return { companies, currentCompany, isLoading, error, fetchCompanies, fetchCompany, createCompany, updateCompany, deleteCompany, clearError };
}