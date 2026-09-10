import { ObjectStatus } from './enums'

export interface ObjectItem {
    id: number
    title: string
    address: string | null
    district: string | null
    status: ObjectStatus
    supervisor_id: number | null
    contractor_id: number | null
    supervisor_name?: string
    contractor_name?: string
}

export interface ObjectCreate {
    title: string
    address: string
    district: string
    status: ObjectStatus
    supervisor_id: number | null
    contractor_id: number | null
}

export type ObjectUpdate = Partial<ObjectCreate>