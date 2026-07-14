import { computed } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { apiFetch } from '~/composables/useAPI'

export function useUserProfile() {
    const { user: authUser } = useAuth()

    const roleName = computed(() => {
        if (!authUser.value) return ''
        const rawRole = authUser.value.role_name || authUser.value.role_id

        if (typeof rawRole === 'object' && rawRole !== null) {
            return (rawRole as any).name || (rawRole as any).title || (rawRole as any).code || ''
        }
        return String(rawRole || '')
    })

    const isAdmin = computed(() => {
        const normalized = roleName.value.toLowerCase().trim()
        return normalized === 'admin' || normalized === 'администратор'
    })

    const userFullName = computed(() => {
        if (!authUser.value) return ''
        return authUser.value.full_name || authUser.value.name || authUser.value.email || 'Пользователь'
    })

    const currentUserHeader = computed(() => {
        if (!authUser.value) return null
        return {
            id: authUser.value.id,
            fullName: userFullName.value,
            email: authUser.value.email,
            role: roleName.value
        }
    })

    const loadProfile = async () => {
        if (authUser.value?.full_name && authUser.value?.email) return

        try {
            const response = await apiFetch<any>('/users/me')

            if (response?.data) {
                const data = response.data

                authUser.value = {
                    ...authUser.value,
                    ...data,
                    id: data.id,
                    email: data.email,
                    full_name: data.full_name,
                    role_name: data.role_name,
                    role_id: data.role_id
                }
            }
        } catch (err) {
            console.error('Ошибка при загрузке профиля /users/me:', err)
            authUser.value = null
        }
    }

    return {
        authUser,
        roleName,
        isAdmin,
        userFullName,
        currentUserHeader,
        loadProfile
    }
}