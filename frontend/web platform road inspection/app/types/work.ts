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
    historyLog: Array<{ date: string; action: string; user: string }>
}

export interface WorkCreate {

}

export interface WorkUpdate {
    
}