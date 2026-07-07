export interface Task {
    id: number
    title: string
    description: string
    completed: boolean // Избыточное поле, оставляю, чтобы не переделывать код
    status: TaskStatus
    type: TaskType
    objectTitle: string
    dueDate: string
    responsibleNames: string[]
    hasReminderTrigger: boolean
}

export interface TaskCreate {

}

export interface TaskUpdate {
    
}

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

// Ключи для i18n
export const TASK_STATUS_LABELS = {
  pending: 'task.status.pending',
  started: 'tast.status.started',
  in_progress: 'task.status.in_progress',
  completed: 'task.status.completed',
} as const;

// Ключи для i18n
export const TASK_TYPE_LABELS: Record<TaskType, string> = {
    [TaskType.CMR_CHECK]: 'task.types.cmr_check',
    [TaskType.ACTS_EXPORT]: 'task.types.acts_export',
    [TaskType.REGISTRY_RECONCILIATION]: 'task.types.registry_reconciliation',
    [TaskType.OTHER]: 'task.types.other',
};

