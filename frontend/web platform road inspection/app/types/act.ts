export interface ActVolumeRow {
    name: string
    plan: number
    fact: number
    unit: string
}

export interface Act {
    id: number
    number: string
    objectName: string
    type: string
    date: string
    contractor: string
    status: 'На утверждении' | 'Ожидает подписи' | 'Подписан'
    amount: string
    signedBy: string
    notes: string
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    contractNumber: string
    planAmount: string
    vatAmount: string
    docUrl: string
    pdfUrl: string
    signDate: string
    volumes: ActVolumeRow[]
}

export interface ActCreate {

}

export interface ActUpdate {
    
}