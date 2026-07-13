export enum TaskStatus {
    PENDING = 'pending',
    STARTED = 'started',
    IN_PROGRESS = 'in_progress',
    COMPLETED = 'completed',
    PAUSED = 'paused',
    CANCELLED = 'cancelled',
    EXPIRED = 'expired',
    FAILED = 'failed',
}

export enum TaskType {
    CMR_CHECK = 'cmr_check',
    ACTS_EXPORT = 'acts_export',
    REGISTRY_RECONCILIATION = 'registry_reconciliation',
    OTHER = 'other'
}

export interface Task {
    id: number
    title: string
    description: string
    completed: boolean
    status: TaskStatus
    type: TaskType
    objectTitle: string
    dueDate: string
    responsibleNames: string[]
    hasReminderTrigger: boolean
}

export interface TaskCreate {
    title: string
    description?: string
    status?: TaskStatus
    type: TaskType
    objectTitle?: string
    dueDate?: string
    responsibleNames?: string[]
    hasReminderTrigger?: boolean
}

export interface TaskUpdate {
    title?: string
    description?: string
    status?: TaskStatus
    type?: TaskType
    objectTitle?: string
    dueDate?: string
    responsibleNames?: string[]
    hasReminderTrigger?: boolean
}