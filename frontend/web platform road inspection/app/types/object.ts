export interface Object {
    id: number
    title: string
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    status: 'Активный' | 'На проверке' | 'Планирование' | 'Завершено'
    contractor: string
    executor: string
    progressSMR: number
    source: string
    sourceLabel: string
    contractNumber: string
    contractDate: string
    contractAmount: string
    spentAmount: string
    remainingAmount: string
    hasActs: boolean
    connectedActsCount: number
    historyLog: Array<{ date: string; action: string; user: string }>
}
export interface ObjectCreate {

}

export interface ObjectUpdate {

}