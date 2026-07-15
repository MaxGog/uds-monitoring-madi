import { ActStatus, ActType } from './enums'
export interface ActItem {
    id?: number;
    act_id?: number;
    contract_item_id?: number;
    completed_quantity: number;
    price: number;
}

export interface Act {
    id: number;
    name: string;
    status: ActStatus;
    date_signed?: string | null;
    type?: ActType | null;
    metadata_fields?: Record<string, any> | null;
    object_id?: number | null;
    work_id?: number | null;
    contract_id?: number | null;
    created_at?: string;
    updated_at?: string;
    items?: ActItem[];
}

export interface ActItemCreate {
    contract_item_id: number;
    completed_quantity: number;
}

export interface ActCreate {
    name: string;
    status: ActStatus;
    type: ActType;
    date_signed: string;
    items: ActItemCreate[];
    object_id?: number | null;
    contract_id?: number | null;
    work_id?: number | null;
    metadata_fields?: Record<string, any>;
}

export interface ActUpdate {
    name?: string;
    status?: ActStatus;
    type?: ActType;
    date_signed?: string;
    metadata_fields?: Record<string, any>;
}