/**
 * Format a date string into a relative time format (e.g., "2 hours ago")
 * or an absolute date format for older items
 */
export const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60))
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    if (diffHours < 1) return 'just now'
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
    if (diffDays === 1) return '1 day ago'
    if (diffDays <= 12) return `${diffDays} days ago`

    // Show date for items more than 12 days old
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return `${months[date.getMonth()]} ${date.getDate()}`
}

/**
 * Get a month key for grouping (format: YYYY-MM)
 */
export const getMonthKey = (date: Date): string => {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

/**
 * Format a month key into a readable month and year
 */
export const formatMonthDate = (monthKey: string): string => {
    const [year, month] = monthKey.split('-')
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return `${months[parseInt(month) - 1]} ${year}`
}
