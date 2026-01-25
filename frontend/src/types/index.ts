export interface UnionWin {
    id: number
    title: string
    union_name?: string
    emoji?: string
    date: string
    url: string
    summary: string
}

export interface PendingWin {
    id: number
    title: string
    union_name?: string
    emoji?: string
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
