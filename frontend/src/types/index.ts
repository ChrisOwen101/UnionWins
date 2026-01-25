// Valid win types matching backend WIN_TYPES
export const WIN_TYPES = [
    'Pay Rise',
    'Recognition',
    'Strike Action',
    'Working Conditions',
    'Job Security',
    'Benefits',
    'Health & Safety',
    'Equality',
    'Legal Victory',
    'Organizing',
    'Other',
] as const

export type WinType = typeof WIN_TYPES[number]

// UK Unions list will be fetched from API
export type UnionName = string

export interface UnionWin {
    id: number
    title: string
    union_name?: string
    emoji?: string
    win_types?: string // Comma-separated list of win types from backend
    date: string
    url: string
    summary: string
}

export interface PendingWin {
    id: number
    title: string
    union_name?: string
    emoji?: string
    win_types?: string // Comma-separated list of win types from backend
    date: string
    url: string
    summary: string
    status: string
    submitted_by?: string
}

export interface SubmitWinRequest {
    url: string
    submitted_by?: string
}

export interface MousePosition {
    x: number
    y: number
}

export interface GroupedWins {
    monthKey: string
    wins: UnionWin[]
}

export type NewsletterFrequency = 'daily' | 'weekly' | 'monthly'

export interface NewsletterSubscribeRequest {
    email: string
    name?: string
    frequency: NewsletterFrequency
}

export interface NewsletterSubscribeResponse {
    success: boolean
    message: string
}
