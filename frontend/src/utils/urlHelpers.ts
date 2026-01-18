/**
 * Extract domain name from a URL
 */
export const getDomain = (url: string): string => {
    try {
        return new URL(url).hostname.replace('www.', '')
    } catch {
        return url
    }
}
