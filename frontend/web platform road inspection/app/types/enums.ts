// Статусы объектов
export enum ObjectStatus {
    PENDING = 'pending',
    ACCEPTED = 'accepted',
    IN_PROGRESS = 'in_progress',
    COMPLETED = 'completed',
    PAUSED = 'paused',
    CANCELLED = 'cancelled',
    EXPIRED = 'expired',
    FAILED = 'failed'
}

// Статусы задач
export enum TaskStatus {
    PENDING = 'pending',
    ACCEPTED = 'accepted',
    IN_PROGRESS = 'in_progress',
    COMPLETED = 'completed',
    PAUSED = 'paused',
    CANCELLED = 'cancelled',
    EXPIRED = 'expired',
    FAILED = 'failed'
}

// Приоритеты задач
export enum TaskPriority {
    LOW = 'low',
    MEDIUM = 'medium',
    HIGH = 'high',
    CRITICAL = 'critical'
}

// Статусы актов
export enum ActStatus {
    DRAFT = 'draft',
    PENDING = 'pending',
    APPROVED = 'approved',
    COMPLETED = 'completed'
}

// Типы актов
export enum ActType {
    SUPERVISORY = 'supervisory',
    CONTRACTOR = 'contractor'
}

// Типы контрактов
export enum ContractType {
    GENERAL = 'general',
    WORK = 'work',
    ADDITIONAL = 'additional'
}

// Статусы контрактов
export enum ContractStatus {
    DRAFT = 'draft',
    ACTIVE = 'active',
    COMPLETED = 'completed',
    TERMINATED = 'terminated'
}