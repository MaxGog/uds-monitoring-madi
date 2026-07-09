export interface ActShort {
    id: number
    number: string
    date: string
    amount: string
    status: string
}

export interface Object {
    id: number
    title: string
    address?: string
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    status: 'Активный' | 'На проверке' | 'Планирование' | 'Завершено'
    contractor: string
    executor: string
    progressSMR: number
    source: string
    sourceLabel: string
    contractNumber: string
    contractDate: string
    startDate?: string
    endDate?: string
    isOverdue?: boolean
    contractAmount: string
    spentAmount: string
    remainingAmount: string
    hasActs: boolean
    connectedActsCount: number
    actsList?: ActShort[]
    historyLog: Array<{ date: string; action: string; user: string }>
}

export type ObjectCreate = Omit<Object, 'id' | 'hasActs' | 'connectedActsCount' | 'historyLog'>
export type ObjectUpdate = Partial<ObjectCreate>