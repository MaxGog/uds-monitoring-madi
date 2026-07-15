export interface Work {
    id: number
    objectName: string
    region: string
    stage: 'Проверка объемов' | 'Анализ отклонений' | 'Приемка работ' | 'Завершено'
    progress: string
    manager: string
    updatedAt: string
    nextAction: string
    hasDeviationAlert: boolean
    budgetAllocation: {
        total: string
        spent: string
        remaining: string
    }
    historyLog: Array<{
        date: string;
        title?: string;
        comment?: string;
        action?: string;
        user?: string;
        author?: string
    }>
}

export interface WorkCreate {
    objectName: string
    region: string
    manager: string
    stage: 'Проверка объемов' | 'Анализ отклонений' | 'Приемка работ' | 'Завершено'
    progress: number
    hasDeviationAlert: boolean
    budgetTotal: number
    budgetSpent: number
    nextAction?: string
    initialComment?: string
}

export interface WorkUpdate extends Partial<WorkCreate> {
    // При необходимости можно переопределить точечные поля
}