import { TaskStatus, TaskPriority } from './enums'

export interface Task {
    id: number
    title: string
    description: string | null
    status: TaskStatus
    priority: TaskPriority
    performer_ids: string[]
    author_id?: string
    author_name?: string
    created_at: string
    updated_at: string
    completed_at: string | null
}

export interface TaskCreate {
    title: string
    description?: string | null
    status?: TaskStatus
    priority?: TaskPriority
    performer_ids?: string[]
}

export interface TaskUpdate {
    title?: string
    description?: string | null
    status?: TaskStatus
    priority?: TaskPriority
    performer_ids?: string[]
}