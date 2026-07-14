export type ObjectStatus =
    | 'pending'
    | 'accepted'
    | 'in_progress'
    | 'completed'
    | 'paused'
    | 'cancelled'
    | 'expired'
    | 'failed'

export interface ObjectItem {
    isOverdue: any
    id: number
    title: string
    address: string
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    status: ObjectStatus
    contractor?: string
    executor?: string
    progressSMR?: number
    source?: string
    sourceLabel?: string
    contractNumber?: string
    contractDate?: string
    startDate?: string
    endDate?: string
    contractAmount?: string
    spentAmount?: string
    remainingAmount?: string
    metadata_fields?: Record<string, any>
}

export interface ObjectCreate {
    title: string
    address: string
    region: string
    status: ObjectStatus
    contractor?: string
    executor?: string
    contractNumber?: string
    contractDate?: string
    startDate?: string
    endDate?: string
    contractAmount?: string
    metadata_fields?: Record<string, any>
}

export type ObjectUpdate = Partial<ObjectCreate>