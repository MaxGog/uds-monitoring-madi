export interface Company {
    id: number;
    name: string;
    inn: string | null;
    kpp: string | null;
    address: string | null;
    bank_account: string | null;
    bank_name: string | null;
    bic: string | null;
}

export interface CompanyCreate extends Omit<Partial<Company>, 'id'> {
    name: string;
}

export interface CompanyUpdate extends Partial<CompanyCreate> { }