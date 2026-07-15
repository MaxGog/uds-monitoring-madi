export interface Contract {
    id: number;
    contract_id: string;
    date_signed: string;
    description: string;
    status: 'draft' | 'active' | 'completed' | 'terminated';
    type: 'general' | 'work' | 'additional';
    cost: number;
    total_cost: number;
    planned_start: string;
    planned_end: string;
    actual_start: string | null;
    actual_end: string | null;
    object_id: number | null;
    work_id: number | null;
}

export interface ContractCreate extends Omit<Partial<Contract>, 'id'> {
    contract_id: string;
    status: Contract['status'];
    type: Contract['type'];
}

export interface ContractUpdate extends Partial<ContractCreate> { }