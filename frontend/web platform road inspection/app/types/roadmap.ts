export interface Roadmap {
    id: number
    title: string
    objectId: number
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    startDate: string
    endDate: string
    phase: 'Разработка проекта' | 'Подготовка ИД' | 'Проверка согласований' | 'Утверждено'
    risk: 'Низкий' | 'Средний' | 'Высокий'
    riskDescription: string
    manager: string
    budget: string
    progressPercentage: number
    area: number
    cost: number
    lastSource: 'Google Sheets' | 'Ручной ввод' | 'Интеграция API'
    milestones: Array<{
        id: number
        name: string           
        planDate: string
        factDate: string | null
        status: 'В графике' | 'Внимание' | 'Критический сдвиг' | 'Выполнено'
    }>
    responsibleManager: string
    hasRiskAlert: boolean
}
export interface RoadmapCreate {

}

export interface RoadmapUpdate {
    
}